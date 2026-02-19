#!/usr/bin/env python3
"""
Square → Google Sheets Sync & Reconciliation
Fetches Square payments and syncs/reconciles against the Income sheet.

Extracted from: archive/old-scripts/sync_to_sheets.py,
                archive/old-scripts/reconcile_accounts.py,
                archive/old-scripts/reconcile_simple.py
No external dependencies — stdlib only.

Usage standalone:
    python3 square_sheets_sync.py check          # reconcile only (dry run)
    python3 square_sheets_sync.py sync           # sync missing to Sheets
    python3 square_sheets_sync.py sync --days 30 # last 30 days

Usage as module:
    from square_sheets_sync import SquareSheetsSync
    s = SquareSheetsSync()
    missing = s.find_missing_payments(days=14)
    s.sync_missing(missing)
"""

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# Import sibling modules (same scripts/ directory)
from square_api import SquareAPI
from google_sheets_api import GoogleSheetsAPI

SYDNEY_TZ = ZoneInfo("Australia/Sydney")


class SquareSheetsSync:
    """Reconcile Square payments with Google Sheets Income tab."""

    FINANCE_SHEET_ID = "1pocJwoOO3emKfQf9mzFHuahZ5nA7KSrehF9fBqn-00Q"
    INCOME_RANGE = "square!A:F"   # Date | Client | Desc | Amount | Method | PaymentID

    def __init__(self, square: SquareAPI = None, sheets: GoogleSheetsAPI = None):
        self.sq = square or SquareAPI()
        # Hard-pin finance backup sheet (never create new accounting sheet).
        self.gs = sheets or GoogleSheetsAPI(spreadsheet_id=self.FINANCE_SHEET_ID)

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _parse_amount(s) -> float:
        """Parse a cell like '$1,234.56' into a float."""
        try:
            return float(str(s).replace('$', '').replace(',', '').strip())
        except (ValueError, TypeError):
            return 0.0

    # ── reconciliation ───────────────────────────────────────────────────

    def get_sheet_income(self) -> list[dict]:
        """Read all rows from the finance backup 'square' tab and return as dicts."""
        try:
            rows = self.gs.read(self.INCOME_RANGE)
        except RuntimeError as e:
            print(f"Debug Sheet Error: {e}")
            return []

        records = []
        for row in rows:
            if len(row) < 4 or not row[0]: # Skip rows without a date
                continue
            if row[0].lower().startswith("date"): # Skip header rows
                continue
            
            records.append({
                "date": row[0],
                "client": row[1] if len(row) > 1 else "",
                "description": row[2] if len(row) > 2 else "",
                "amount": self._parse_amount(row[3]),
                "method": row[4] if len(row) > 4 else "",
                "invoice_id": row[5] if len(row) > 5 else "",
            })
        return records

    def get_square_payments(self, days: int = 30) -> list[dict]:
        """Fetch completed Square payments for the last N days."""
        payments = self.sq.list_payments(days=days, status="COMPLETED")
        results = []
        for p in payments:
            amt = p.get("amount_money", {}).get("amount", 0) / 100
            if amt <= 0:
                continue
            results.append({
                "id": p.get("id", ""),
                "date": p.get("created_at", "")[:10],
                "amount": amt,
                "status": p.get("status", ""),
                "reference": p.get("reference_id", ""),
            })
        return results

    def find_missing_payments(self, days: int = 30,
                              tolerance: float = 0.01) -> list[dict]:
        """
        Compare Square payments against the Sheet.
        Returns list of Square payments not found in the Sheet.

        Matching is by Invoice ID (reference) first, then amount.
        """
        sq_payments = self.get_square_payments(days=days)
        sheet_income = self.get_sheet_income()

        # Build set of existing invoice IDs in sheet
        sheet_ids = {r["invoice_id"] for r in sheet_income if r.get("invoice_id")}
        sheet_amounts = [r["amount"] for r in sheet_income if not r.get("invoice_id")]

        missing = []
        for p in sq_payments:
            # Check by ID first
            if p["id"] in sheet_ids:
                continue
            
            # Fallback to amount matching for manual entries
            matched = False
            for i, sa in enumerate(sheet_amounts):
                if abs(sa - p["amount"]) <= tolerance:
                    sheet_amounts.pop(i)
                    matched = True
                    break
            
            if not matched:
                missing.append(p)

        return missing

    def find_sheet_only(self, days: int = 30,
                        tolerance: float = 0.01) -> list[dict]:
        """
        Reverse check: find Sheet income rows that have NO matching
        Square payment (possible manual entries or other payment sources).
        """
        sq_payments = self.get_square_payments(days=days)
        sheet_income = self.get_sheet_income()

        sq_amounts = [p["amount"] for p in sq_payments]

        sheet_only = []
        for r in sheet_income:
            matched = False
            for i, sa in enumerate(sq_amounts):
                if abs(sa - r["amount"]) <= tolerance:
                    sq_amounts.pop(i)
                    matched = True
                    break
            if not matched and r["amount"] > 0:
                sheet_only.append(r)

        return sheet_only

    # ── sync ─────────────────────────────────────────────────────────────

    def sync_missing(self, missing: list[dict] = None,
                     days: int = 30, dry_run: bool = False) -> list[dict]:
        """
        Append missing Square payments to the Income sheet.

        Returns the list of payments that were synced (or would be synced in dry_run).
        """
        if missing is None:
            missing = self.find_missing_payments(days=days)

        if not missing:
            return []

        synced = []
        for m in missing:
            row = [
                m["date"],
                "Square Customer",
                f"Square Payment {m['id'][-6:]}",
                f"${m['amount']:.2f}",
                "Square",
                m["id"],
            ]
            if dry_run:
                synced.append(m)
                continue

            result = self.gs.append(self.INCOME_RANGE, row)
            if "error" not in result:
                synced.append(m)

        return synced

    # ── reporting ────────────────────────────────────────────────────────

    def reconciliation_report(self, days: int = 30) -> str:
        """Generate a full reconciliation report as text."""
        sq_payments = self.get_square_payments(days=days)
        sheet_income = self.get_sheet_income()
        missing = self.find_missing_payments(days=days)

        sq_total = sum(p["amount"] for p in sq_payments)
        sheet_total = sum(r["amount"] for r in sheet_income)

        lines = [
            "═" * 55,
            "  SQUARE ↔ GOOGLE SHEETS RECONCILIATION",
            f"  Last {days} days — {datetime.now(SYDNEY_TZ).strftime('%d/%m/%Y %H:%M')} AEST",
            "═" * 55,
            "",
            f"  Square payments (completed): {len(sq_payments):>5}   ${sq_total:>10,.2f}",
            f"  Sheet income rows:           {len(sheet_income):>5}   ${sheet_total:>10,.2f}",
            f"  Difference:                           ${sq_total - sheet_total:>10,.2f}",
            "",
        ]

        if not missing:
            lines.append("  ✅ All Square payments found in Google Sheets.")
        else:
            lines.append(f"  ⚠️  {len(missing)} Square payment(s) MISSING from Sheets:")
            lines.append("  " + "─" * 50)
            for m in missing:
                lines.append(f"    {m['date']}  ${m['amount']:>10,.2f}  ID: ...{m['id'][-8:]}")
            lines.append("")
            lines.append("  Run with 'sync' to add these to the Sheet.")

        lines.append("═" * 55)
        return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _cli():
    args = sys.argv[1:]
    cmd = args[0] if args else "check"

    # Parse --days flag
    days = 30
    for i, a in enumerate(args):
        if a == "--days" and i + 1 < len(args):
            days = int(args[i + 1])

    syncer = SquareSheetsSync()

    if cmd == "check":
        print(syncer.reconciliation_report(days=days))

    elif cmd == "sync":
        missing = syncer.find_missing_payments(days=days)
        if not missing:
            print("✅ Nothing to sync — all Square payments already in Sheets.")
            return

        print(f"Syncing {len(missing)} missing payment(s) to Sheets...")
        synced = syncer.sync_missing(missing)
        for s in synced:
            print(f"  ✅ {s['date']}  ${s['amount']:.2f}  ID: ...{s['id'][-8:]}")
        print(f"\nDone. Synced {len(synced)} of {len(missing)} payments.")

    elif cmd == "report":
        print(syncer.reconciliation_report(days=days))

    else:
        print("Usage: square_sheets_sync.py <check|sync|report> [--days N]")
        sys.exit(1)


if __name__ == "__main__":
    _cli()
