#!/usr/bin/env python3
"""
Push dashboard financial snapshot into Master Ops sheet.
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from google_sheets_api import GoogleSheetsAPI
from sheet_router import client as routed_client

ROOT = Path("/Users/hafsahnuzhat/Desktop/🦀")
TZ = ZoneInfo("Australia/Sydney")

MONTH_COL = {
    1: "G",   # Jan
    2: "H",   # Feb
    3: "I",
    4: "J",
    5: "K",
    6: "L",
    7: "B",   # Jul
    8: "C",
    9: "D",
    10: "E",
    11: "F",
    12: "G",  # Dec
}


def load_dashboard() -> dict:
    path = ROOT / "dashboard-data.json"
    return json.loads(path.read_text())


def fmt(v: float) -> str:
    return f"${v:.2f}"


def main() -> int:
    now = datetime.now(TZ)
    month_col = MONTH_COL[now.month]

    data = load_dashboard()
    stats = data.get("stats", {})
    fin = data.get("financial", {}).get("totals", {})
    revenue = float(fin.get("revenueMTD", stats.get("revenueMTD", 0)) or 0)
    expenses = float(fin.get("expensesMTD", 0) or 0)
    net = float(fin.get("netMTD", revenue - expenses) or 0)

    gs = routed_client("business")

    # P&L Summary rows:
    # Row 9  -> TOTAL INCOME
    # Row 25 -> TOTAL EXPENSES
    # Row 27 -> NET PROFIT
    batch = [
        {"range": f"P&L Summary!{month_col}9", "values": [[fmt(revenue)]]},
        {"range": f"P&L Summary!{month_col}25", "values": [[fmt(expenses)]]},
        {"range": f"P&L Summary!{month_col}27", "values": [[fmt(net)]]},
    ]
    for item in batch:
        gs.update(item["range"], item["values"])

    stamp = now.strftime("%Y-%m-%d %H:%M:%S")
    gs.append(
        "Task Log!A:H",
        [
            stamp,
            "Dashboard Sync",
            f"Synced dashboard totals to P&L Summary ({month_col})",
            "Dashboard Script",
            "SUCCESS",
            "<1m",
            "Bella Auto",
            f"Revenue={fmt(revenue)}, Expenses={fmt(expenses)}, Net={fmt(net)}",
        ],
    )
    gs.append(
        "Bot_Change_Log!A:H",
        [
            stamp,
            "Bella",
            "P&L Summary",
            f"{month_col}9,{month_col}25,{month_col}27",
            "UPDATE",
            "",
            f"{fmt(revenue)} | {fmt(expenses)} | {fmt(net)}",
            "Dashboard refresh",
        ],
    )

    print("Master sheet updated from dashboard snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
