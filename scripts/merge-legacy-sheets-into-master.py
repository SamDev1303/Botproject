#!/usr/bin/env python3
"""
Merge data from legacy cleanupbros accounts sheet into Master Operations sheet.
No new spreadsheets are created.
"""

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from google_sheets_api import GoogleSheetsAPI

MASTER_ID = "1sZOaf57GcR26sEXnZKSNltQPisXoLTGasx0qmbaCBGU"
LEGACY_ID = "1Yd87dToNUGbyF7Olo1mXFOtwYxc375Ts7YFOOFXElYM"
TZ = ZoneInfo("Australia/Sydney")


def parse_money(value) -> float:
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except Exception:
        return 0.0


def gst_split(total: float) -> tuple[float, float]:
    gst = round(total / 11, 2)
    net = round(total - gst, 2)
    return net, gst


def is_date(value: str) -> bool:
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
        return True
    except Exception:
        return False


def should_skip_legacy_row(row: list[str]) -> bool:
    if not row:
        return True
    first = str(row[0]).strip().lower() if row else ""
    joined = " ".join(str(x).strip().lower() for x in row)
    if first in {"date", ""}:
        return True
    if "total income" in joined:
        return True
    return False


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    master = GoogleSheetsAPI(spreadsheet_id=MASTER_ID)
    legacy = GoogleSheetsAPI(spreadsheet_id=LEGACY_ID)
    today = datetime.now(TZ).strftime("%Y-%m-%d")

    legacy_2026 = legacy.read("2026!A:F")
    legacy_exp = legacy.read("Expenses!A:E")
    legacy_wages = legacy.read("Staff Wages!A:F")
    legacy_outstanding = legacy.read("Outstanding!A:E")

    master_client = master.read("Client Log!A:L")
    master_expenses = master.read("Expenses!A:M")
    master_bookkeeping = master.read("Bookkeeping!A:K")
    master_wages = master.read("Staff & Wages!A:N")

    client_keys = {
        (
            str(r[0]).strip() if len(r) > 0 else "",
            str(r[1]).strip().lower() if len(r) > 1 else "",
            str(r[7]).strip().lower() if len(r) > 7 else "",
            str(r[9]).strip() if len(r) > 9 else "",
        )
        for r in master_client[1:]
    }
    expense_keys = {
        (
            str(r[1]).strip() if len(r) > 1 else "",
            str(r[4]).strip().lower() if len(r) > 4 else "",
            str(r[7]).strip() if len(r) > 7 else "",
        )
        for r in master_expenses[1:]
    }
    wage_keys = {
        (
            str(r[4]).strip() if len(r) > 4 else "",
            str(r[1]).strip().lower() if len(r) > 1 else "",
            str(r[8]).strip() if len(r) > 8 else "",
        )
        for r in master_wages[1:]
    }

    add_client: list[list[str]] = []
    add_expenses: list[list[str]] = []
    add_bookkeeping: list[list[str]] = []
    add_wages: list[list[str]] = []

    # Income / client rows from legacy 2026
    for row in legacy_2026:
        if should_skip_legacy_row(row):
            continue
        date = str(row[0]).strip()
        if not is_date(date):
            continue
        client = str(row[1]).strip()
        desc = str(row[2]).strip() if len(row) > 2 else "Cleaning"
        amt = parse_money(row[3] if len(row) > 3 else 0)
        method = str(row[4]).strip() if len(row) > 4 else ""
        invoice = str(row[5]).strip() if len(row) > 5 else ""
        key = (date, client.lower(), invoice.lower(), f"{amt:.2f}")
        if key in client_keys:
            continue
        add_client.append([
            date, client, "", "", "Cleaning", "", "", invoice, "Paid",
            f"${amt:.2f}", "Legacy cleanupbros accounts", f"{desc} | {method}"
        ])
        client_keys.add(key)

    # Outstanding rows to Client Log as overdue
    for row in legacy_outstanding:
        if should_skip_legacy_row(row):
            continue
        client = str(row[0]).strip()
        invoice = str(row[1]).strip() if len(row) > 1 else ""
        amt = parse_money(row[2] if len(row) > 2 else 0)
        status = str(row[3]).strip() if len(row) > 3 else "Overdue"
        notes = str(row[4]).strip() if len(row) > 4 else ""
        key = ("", client.lower(), invoice.lower(), f"{amt:.2f}")
        if key in client_keys:
            continue
        add_client.append([
            "", client, "", "", "Cleaning", "", f"${amt:.2f}", invoice, status,
            "$0.00", "Legacy cleanupbros accounts", notes
        ])
        client_keys.add(key)

    # Expenses -> Expenses + Bookkeeping
    exp_counter = len(master_expenses)
    for row in legacy_exp:
        if should_skip_legacy_row(row):
            continue
        date = str(row[0]).strip()
        if not is_date(date):
            continue
        desc = str(row[1]).strip()
        category = str(row[2]).strip() if len(row) > 2 else "General"
        total = parse_money(row[3] if len(row) > 3 else 0)
        method = str(row[4]).strip() if len(row) > 4 else ""
        supplier = desc.split(" - ")[0].strip() if " - " in desc else desc[:40]
        net, gst = gst_split(total)
        key = (date, desc.lower(), f"${total:.2f}")
        if key in expense_keys:
            continue
        exp_counter += 1
        exp_id = f"EXP-{date.replace('-', '')}-{exp_counter}"
        add_expenses.append([
            exp_id, date, supplier, category, desc,
            f"${net:.2f}", f"${gst:.2f}", f"${total:.2f}", method,
            "", "Yes", "", "Migrated from cleanupbros accounts"
        ])
        add_bookkeeping.append([
            date, "Expense", category, desc,
            f"${total:.2f}", f"${gst:.2f}", f"${net:.2f}",
            method, "", supplier, "Migrated from cleanupbros accounts"
        ])
        expense_keys.add(key)

    # Wages -> Staff & Wages
    wage_counter = len(master_wages)
    for row in legacy_wages:
        if should_skip_legacy_row(row):
            continue
        date = str(row[0]).strip()
        if not is_date(date):
            continue
        name = str(row[1]).strip()
        desc = str(row[2]).strip() if len(row) > 2 else "Wages"
        gross = parse_money(row[3] if len(row) > 3 else 0)
        abn = str(row[5]).strip() if len(row) > 5 else ""
        worker_type = "Contractor" if abn and "no abn" not in abn.lower() else "Employee"
        key = (date, name.lower(), f"${gross:.2f}")
        if key in wage_keys:
            continue
        wage_counter += 1
        pay_id = f"PAY-{date.replace('-', '')}-{wage_counter}"
        add_wages.append([
            pay_id, name, "Cleaner", worker_type, date, date, "", "",
            f"${gross:.2f}", "", "$0.00", f"${gross:.2f}", abn,
            f"{desc} | Migrated from cleanupbros accounts"
        ])
        wage_keys.add(key)

    print(f"Would add Client Log rows: {len(add_client)}")
    print(f"Would add Expenses rows: {len(add_expenses)}")
    print(f"Would add Bookkeeping rows: {len(add_bookkeeping)}")
    print(f"Would add Staff & Wages rows: {len(add_wages)}")

    if not args.apply:
        return 0

    if add_client:
        master.append_rows("Client Log!A:L", add_client)
    if add_expenses:
        master.append_rows("Expenses!A:M", add_expenses)
    if add_bookkeeping:
        master.append_rows("Bookkeeping!A:K", add_bookkeeping)
    if add_wages:
        master.append_rows("Staff & Wages!A:N", add_wages)

    # Write migration event
    master.append(
        "Task Log!A:H",
        [
            f"{today} 22:00",
            "Sheet Migration",
            f"Migrated legacy rows (client={len(add_client)}, expenses={len(add_expenses)}, wages={len(add_wages)})",
            "Google Sheets API",
            "SUCCESS",
            "auto",
            "Bella Auto",
            "cleanupbros accounts -> Master Ops",
        ],
    )
    print("Applied migration to Master Ops.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
