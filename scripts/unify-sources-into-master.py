#!/usr/bin/env python3
"""
Unify ingestion tabs into canonical unified tabs and lightweight downstream updates.
"""

from collections import defaultdict

from universal_sync_helpers import master_client, now_iso
from sheet_router import client as routed_client

INGEST_TABS = [
    "Ingestion_Gmail",
    "Ingestion_GCal",
    "Ingestion_AppleCal",
    "Ingestion_Reminders",
    "Ingestion_AppleNotes",
]


def parse_rows(gs, tab: str) -> list[dict]:
    rows = gs.read(f"{tab}!A:O")
    out = []
    for r in rows[1:]:
        if len(r) < 2:
            continue
        rec = {
            "source": r[0] if len(r) > 0 else "",
            "external_id": r[1] if len(r) > 1 else "",
            "title": r[2] if len(r) > 2 else "",
            "description": r[3] if len(r) > 3 else "",
            "party": r[4] if len(r) > 4 else "",
            "start_at": r[5] if len(r) > 5 else "",
            "end_at": r[6] if len(r) > 6 else "",
            "status": r[7] if len(r) > 7 else "",
            "amount": r[8] if len(r) > 8 else "",
            "location": r[10] if len(r) > 10 else "",
            "tags": r[11] if len(r) > 11 else "",
            "account_type": r[12] if len(r) > 12 else "business",
            "updated_at": str(r[13]) if len(r) > 13 else "",
        }
        out.append(rec)
    return out


def record_key(rec: dict) -> str:
    if rec["external_id"]:
        return f"{rec['source']}::{rec['external_id']}"
    return f"{rec['title']}|{rec['start_at']}|{rec['party']}"


def choose_record(a: dict, b: dict) -> dict:
    # Cancel wins, else latest updated_at lexical, else prefer Google calendar.
    if "cancel" in (a.get("status", "").lower()):
        return a
    if "cancel" in (b.get("status", "").lower()):
        return b
    if str(a.get("updated_at", "")) > str(b.get("updated_at", "")):
        return a
    if str(b.get("updated_at", "")) > str(a.get("updated_at", "")):
        return b
    if a.get("source") == "google_calendar":
        return a
    if b.get("source") == "google_calendar":
        return b
    return a


def is_airbnb(rec: dict) -> bool:
    txt = f"{rec.get('title','')} {rec.get('description','')} {rec.get('location','')}".lower()
    return any(k in txt for k in ["airbnb", "pinnacle", "nagle", "unit 3", "unit 4", "atkinson"])


def main() -> int:
    gs = master_client()
    sgs = routed_client("staff")

    all_rows = []
    for tab in INGEST_TABS:
        all_rows.extend(parse_rows(gs, tab))
    all_rows.extend(parse_rows(sgs, "Ingestion_Connecteam"))

    merged: dict[str, dict] = {}
    for rec in all_rows:
        k = record_key(rec)
        if k in merged:
            merged[k] = choose_record(merged[k], rec)
        else:
            merged[k] = rec

    unified = []
    for k, rec in merged.items():
        unified.append([
            k,
            rec["source"],
            rec["title"],
            rec["party"],
            rec["start_at"][:10] if rec["start_at"] else "",
            rec["start_at"],
            rec["end_at"],
            rec["status"],
            rec["location"],
            rec["tags"],
            rec["updated_at"],
            "merged",
        ])

    unified.sort(key=lambda r: (r[4], r[2]))

    gs.clear("Unified_Bookings!A:L")
    gs.update("Unified_Bookings!A1:L1", [[
        "record_key", "source", "title", "party", "date", "start_at", "end_at",
        "status", "location", "tags", "last_updated", "resolution_note"
    ]])
    if unified:
        gs.append_rows("Unified_Bookings!A:L", unified)

    # Clients rollup
    client_map = defaultdict(lambda: {"source": set(), "latest_event": "", "latest_date": "", "status": "active", "notes": ""})
    for rec in merged.values():
        party = rec.get("party", "").strip()
        if not party:
            continue
        c = client_map[party]
        c["source"].add(rec.get("source", ""))
        if str(rec.get("start_at", "")) >= c["latest_date"]:
            c["latest_date"] = rec.get("start_at", "")
            c["latest_event"] = rec.get("title", "")
        if "cancel" in rec.get("status", "").lower():
            c["status"] = "cancelled"
    client_rows = []
    for name, v in client_map.items():
        client_rows.append([
            name.lower().replace(" ", "_"),
            name,
            "",
            "",
            ",".join(sorted(v["source"])),
            v["latest_event"],
            v["latest_date"],
            v["status"],
            v["notes"],
        ])
    gs.clear("Unified_Clients!A:I")
    gs.update("Unified_Clients!A1:I1", [[
        "client_key", "client_name", "phone", "email", "source", "latest_event",
        "latest_date", "status", "notes"
    ]])
    if client_rows:
        gs.append_rows("Unified_Clients!A:I", client_rows)

    # Lightweight downstream writes for booking tabs.
    airbnb_existing = gs.read("Airbnb Cleans!A:O")
    airbnb_notes = {str(r[14]).strip() for r in airbnb_existing[1:] if len(r) > 14}
    non_existing = gs.read("Non-Airbnb Jobs!A:P")
    non_notes = {str(r[15]).strip() for r in non_existing[1:] if len(r) > 15}
    a_rows = []
    n_rows = []
    idx_a = len(airbnb_existing)
    idx_n = len(non_existing)
    for rec in merged.values():
        if not rec.get("start_at"):
            continue
        note_tag = f"Unified::{record_key(rec)}"
        if is_airbnb(rec):
            if note_tag in airbnb_notes:
                continue
            idx_a += 1
            a_rows.append([
                f"UNI-A-{idx_a}",
                rec["start_at"][:10],
                "",
                rec["title"][:80],
                "",
                "",
                "Airbnb Turnover",
                "",
                "",
                "",
                "",
                "",
                "",
                rec.get("status", "Imported"),
                note_tag,
            ])
        else:
            if note_tag in non_notes:
                continue
            idx_n += 1
            n_rows.append([
                f"UNI-N-{idx_n}",
                rec["start_at"][:10],
                rec.get("party", "")[:80],
                "",
                "",
                rec.get("title", "Service"),
                rec.get("location", ""),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                rec.get("status", "Imported"),
                note_tag,
            ])
    if a_rows:
        gs.append_rows("Airbnb Cleans!A:O", a_rows)
    if n_rows:
        gs.append_rows("Non-Airbnb Jobs!A:P", n_rows)

    gs.append("Task Log!A:H", [
        now_iso(),
        "Unified Sync",
        f"Merged ingestion rows={len(all_rows)}, unified={len(unified)}",
        "unify-sources-into-master.py",
        "SUCCESS",
        "<1m",
        "Bella Auto",
        "",
    ])
    print(f"Unified records: {len(unified)} | Airbnb adds: {len(a_rows)} | Non-Airbnb adds: {len(n_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
