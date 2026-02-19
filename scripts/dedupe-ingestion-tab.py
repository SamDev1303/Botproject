#!/usr/bin/env python3
"""
Deduplicate ingestion tab by external_id, keeping latest updated/ingested row.
"""

import argparse

from google_sheets_api import GoogleSheetsAPI

MASTER_ID = "1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU"


def key_for(row: list[str]) -> str:
    return str(row[1]).strip() if len(row) > 1 else ""


def rank(row: list[str]) -> tuple[str, str]:
    upd = str(row[13]).strip() if len(row) > 13 else ""
    ing = str(row[14]).strip() if len(row) > 14 else ""
    return (upd, ing)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tab", required=True)
    args = p.parse_args()

    gs = GoogleSheetsAPI(spreadsheet_id=MASTER_ID)
    rows = gs.read(f"{args.tab}!A:O")
    if not rows:
        print("No rows.")
        return 0
    header = rows[0]
    dedup = {}
    order = []
    for row in rows[1:]:
        k = key_for(row)
        if not k:
            continue
        if k not in dedup:
            dedup[k] = row
            order.append(k)
        else:
            if rank(row) > rank(dedup[k]):
                dedup[k] = row

    out = [header] + [dedup[k] for k in order]
    gs.clear(f"{args.tab}!A:O")
    gs.update(f"{args.tab}!A1:O1", [header])
    if len(out) > 1:
        gs.append_rows(f"{args.tab}!A:O", out[1:])
    print(f"{args.tab}: before={len(rows)-1} after={len(out)-1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
