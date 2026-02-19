#!/usr/bin/env python3
"""
One-time migration from Cubs-Accounts bank statement folder into Bella 3-sheet SOT.

- Parses statement PDFs using pdftotext
- Extracts transactions (CommBank + ANZ styles)
- Classifies business vs personal
- Appends to Business Ops / Personal sheets with idempotency key
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from google_sheets_api import GoogleSheetsAPI
from sheet_router import client as routed_client

TZ = ZoneInfo("Australia/Sydney")


@dataclass
class Tx:
    date: str
    description: str
    amount: float
    bank: str
    source_file: str


BUSINESS_HINTS = [
    "square",
    "clean",
    "client",
    "airbnb",
    "bunnings",
    "fuel",
    "flyer",
    "cleaning",
    "business",
    "supplier",
    "invoice",
    "wallace",
]
PERSONAL_HINTS = [
    "tuition",
    "nurse training",
    "uber eats",
    "mcdonald",
    "coles",
    "rent",
    "baby",
    "family",
    "personal",
]


def classify_account(text: str) -> str:
    low = text.lower()
    if any(k in low for k in PERSONAL_HINTS):
        return "personal"
    if any(k in low for k in BUSINESS_HINTS):
        return "business"
    return "business"


def run_pdftotext(pdf: Path) -> str:
    out = Path(tempfile.gettempdir()) / f"cubs_{hashlib.md5(str(pdf).encode()).hexdigest()}.txt"
    subprocess.check_call(["pdftotext", "-layout", str(pdf), str(out)])
    return out.read_text(errors="ignore")


def normalize_date(token: str) -> str:
    # Supports: 31 Jan 2026, 31/01/26, 31/01/2026
    token = token.strip()
    for fmt in ["%d %b %Y", "%d/%m/%y", "%d/%m/%Y"]:
        try:
            return datetime.strptime(token, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return ""


def parse_commbank_text(text: str, source_file: str) -> list[Tx]:
    txs: list[Tx] = []
    # Date + details + amount + balance on one line
    line_re = re.compile(r"^\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\s+(.+?)\s+(-?\$[\d,]+\.\d{2})\s+\$?[\d,]+\.\d{2}\s*$")

    for raw in text.splitlines():
        line = raw.rstrip()
        m = line_re.match(line)
        if not m:
            continue
        d = normalize_date(m.group(1))
        if not d:
            continue
        desc = re.sub(r"\s+", " ", m.group(2)).strip()
        amt_raw = m.group(3).replace("$", "").replace(",", "")
        amt = float(amt_raw)
        txs.append(Tx(date=d, description=desc, amount=amt, bank="commbank", source_file=source_file))

    return txs


def detect_statement_year(text: str, fallback: int = datetime.now(TZ).year) -> int:
    # Prefer explicit statement range year first.
    m = re.search(r"(\\d{1,2}\\s+[A-Za-z]+\\s+\\d{4})\\s*-\\s*(\\d{1,2}\\s+[A-Za-z]+\\s+\\d{4})", text)
    if m:
        try:
            return datetime.strptime(m.group(2), "%d %B %Y").year
        except Exception:
            try:
                return datetime.strptime(m.group(2), "%d %b %Y").year
            except Exception:
                pass

    m = re.search(r"Commencing\\s+\\d{1,2}\\s+[A-Za-z]+\\s+(\\d{4})", text)
    if m:
        return int(m.group(1))

    years = [int(y) for y in re.findall(r"\\b(20\\d{2})\\b", "\\n".join(text.splitlines()[:80]))]
    return max(years) if years else fallback


def parse_anz_text(text: str, source_file: str) -> list[Tx]:
    txs: list[Tx] = []
    # ANZ rows often: "13 Jan  PAYMENT TO ... $100.00  $0.95"
    line_re = re.compile(r"^\s*(\d{1,2}\s+[A-Za-z]{3})\s+(.+?)\s+(\$[\d,]+\.\d{2})\s+(\$[\d,]+\.\d{2})\s*$")

    stmt_year = detect_statement_year(text)

    for raw in text.splitlines():
        line = raw.rstrip()
        m = line_re.match(line)
        if not m:
            continue

        dm = m.group(1)
        desc = re.sub(r"\s+", " ", m.group(2)).strip()
        v1 = float(m.group(3).replace("$", "").replace(",", ""))

        try:
            date_str = datetime.strptime(f"{dm} {stmt_year}", "%d %b %Y").strftime("%Y-%m-%d")
        except Exception:
            continue

        low = desc.lower()
        credit_hint = any(k in low for k in ["payment from", "transfer from", "from square", "fast transfer from"])
        debit_hint = any(k in low for k in ["payment to", "transfer to", "purchase", "visa debit", "eftpos", "card "])

        if credit_hint and not debit_hint:
            amt = abs(v1)
        elif debit_hint and not credit_hint:
            amt = -abs(v1)
        else:
            # fallback conservative: explicit "from" as income else expense
            amt = abs(v1) if " from " in f" {low} " else -abs(v1)

        txs.append(Tx(date=date_str, description=desc, amount=amt, bank="anz", source_file=source_file))

    return txs


def dedupe_by_key(items: list[Tx]) -> list[Tx]:
    seen = set()
    out = []
    for t in items:
        key = (t.date, t.description.lower(), round(t.amount, 2), t.bank)
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def get_existing_hashes(gs: GoogleSheetsAPI, tab: str) -> set[str]:
    rows = gs.read(f"{tab}!A:Z")
    hashes = set()
    for row in rows[1:]:
        if not row:
            continue
        joined = " | ".join(str(x) for x in row)
        m = re.search(r"tx_hash=([a-f0-9]{32})", joined)
        if m:
            hashes.add(m.group(1))
    return hashes


def tx_hash(tx: Tx) -> str:
    s = f"{tx.date}|{tx.description}|{tx.amount:.2f}|{tx.bank}|{tx.source_file}"
    return hashlib.md5(s.encode()).hexdigest()


def ensure_headers(gs_business: GoogleSheetsAPI, gs_personal: GoogleSheetsAPI):
    # Keep schemas explicit for accounting tabs.
    gs_business.update(
        "Income Ledger!A1:H1",
        [["date", "description", "category", "amount", "payment_method", "source_bank", "source_file", "notes"]],
    )
    gs_personal.update(
        "Personal_Expenses!A1:H1",
        [["date", "description", "category", "amount", "payment_method", "source_bank", "source_file", "notes"]],
    )


def append_rows(args, txs: list[Tx]) -> dict[str, int]:
    gs_business = routed_client("business")
    gs_personal = routed_client("personal")

    ensure_headers(gs_business, gs_personal)

    existing_business = get_existing_hashes(gs_business, "Business_Expenses")
    existing_income = get_existing_hashes(gs_business, "Income Ledger")
    existing_personal = get_existing_hashes(gs_personal, "Personal_Expenses")

    biz_exp_rows = []
    biz_inc_rows = []
    per_exp_rows = []

    for tx in txs:
        if tx.date <= args.cutoff_date:
            continue

        h = tx_hash(tx)
        category = "Income" if tx.amount > 0 else ("Fuel" if "fuel" in tx.description.lower() else "General")
        payment_method = "Bank Transfer"
        notes = f"Imported from Cubs-Accounts | tx_hash={h}"

        if tx.amount > 0:
            if h in existing_income:
                continue
            biz_inc_rows.append([
                tx.date,
                tx.description,
                category,
                f"${abs(tx.amount):.2f}",
                payment_method,
                tx.bank,
                tx.source_file,
                notes,
            ])
            continue

        account_type = classify_account(tx.description)
        amt_abs = abs(tx.amount)

        if account_type == "personal":
            if h in existing_personal:
                continue
            per_exp_rows.append([
                tx.date,
                tx.description,
                "Personal",
                f"${amt_abs:.2f}",
                payment_method,
                tx.bank,
                tx.source_file,
                notes,
            ])
        else:
            if h in existing_business:
                continue
            gst = round(amt_abs / 11, 2)
            ex_gst = round(amt_abs - gst, 2)
            biz_exp_rows.append([
                tx.date,
                tx.description,
                "Bank Statement Expense",
                f"${amt_abs:.2f}",
                f"${gst:.2f}",
                f"${ex_gst:.2f}",
                payment_method,
                tx.bank,
                tx.source_file,
                notes,
            ])

    if biz_inc_rows:
        gs_business.append_rows("Income Ledger!A:H", biz_inc_rows)
    if biz_exp_rows:
        gs_business.append_rows("Business_Expenses!A:J", biz_exp_rows)
    if per_exp_rows:
        gs_personal.append_rows("Personal_Expenses!A:H", per_exp_rows)

    stamp = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    gs_business.append(
        "Task Log!A:H",
        [
            stamp,
            "Cubs Accounts Migration",
            f"Imported bank statement transactions after {args.cutoff_date}",
            "migrate-cubs-accounts-to-three-sheets.py",
            "SUCCESS",
            "<5m",
            "Hafsah Request",
            f"income={len(biz_inc_rows)} business_expenses={len(biz_exp_rows)} personal_expenses={len(per_exp_rows)}",
        ],
    )

    return {
        "income_added": len(biz_inc_rows),
        "business_expenses_added": len(biz_exp_rows),
        "personal_expenses_added": len(per_exp_rows),
    }


def parse_all_pdfs(folder: Path) -> list[Tx]:
    all_txs: list[Tx] = []
    pdfs = sorted(folder.rglob("*.pdf"))
    for pdf in pdfs:
        txt = run_pdftotext(pdf)
        source = pdf.name
        upper_path = str(pdf).upper()
        if "ANZ" in upper_path:
            all_txs.extend(parse_anz_text(txt, source))
        elif "COMMON" in upper_path or "COMMBANK" in upper_path:
            all_txs.extend(parse_commbank_text(txt, source))
        else:
            # Fallback: attempt both.
            all_txs.extend(parse_commbank_text(txt, source))
            all_txs.extend(parse_anz_text(txt, source))
    return dedupe_by_key(all_txs)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--folder", required=True, help="Path to Cubs-Accounts folder")
    p.add_argument("--cutoff-date", default="2025-12-31", help="Only import transactions after this date (YYYY-MM-DD)")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    folder = Path(args.folder)
    if not folder.exists():
        print(f"ERROR: folder not found: {folder}")
        return 1

    txs = parse_all_pdfs(folder)
    today = datetime.now(TZ).date().strftime("%Y-%m-%d")
    txs = [t for t in txs if t.date and t.date <= today]
    txs.sort(key=lambda t: (t.date, t.description, t.amount))

    print(f"Parsed transactions: {len(txs)}")
    if txs:
        print("Date range:", txs[0].date, "->", txs[-1].date)

    preview = txs[:8]
    for t in preview:
        print(f"  {t.date} | {t.amount:>9.2f} | {t.bank:<8} | {t.description[:80]}")

    if args.dry_run:
        print("DRY RUN: no sheet writes performed")
        return 0

    summary = append_rows(args, txs)
    print("Import summary:", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
