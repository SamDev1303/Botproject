#!/usr/bin/env python3
"""
Square API Wrapper — Standalone
List customers, invoices, payments; create invoices & payment links.

Extracted from: archive/mcp/square_server.py, archive/old-scripts/create_sam_square.py
No external dependencies — stdlib only.
Loads credentials from ~/.clawdbot/.env

Usage as module:
    from square_api import SquareAPI
    sq = SquareAPI()
    print(sq.list_customers())

Usage standalone:
    python3 square_api.py                   # list locations
    python3 square_api.py customers         # list customers
    python3 square_api.py payments [days]   # recent payments
    python3 square_api.py invoices [status] # list invoices
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SYDNEY_TZ = ZoneInfo("Australia/Sydney")


# ─── Env Loader ──────────────────────────────────────────────────────────────

def _load_env():
    """Read ~/.clawdbot/.env and populate os.environ (won't overwrite existing)."""
    env_file = Path.home() / ".clawdbot" / ".env"
    if not env_file.exists():
        return
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"'))

_load_env()


# ─── API Client ──────────────────────────────────────────────────────────────

class SquareAPI:
    """Lightweight Square API client — no pip dependencies."""

    BASE_URL = "https://connect.squareup.com/v2"
    API_VERSION = "2025-01-21"
    MAX_RETRIES = 3

    def __init__(self, access_token: str = None, location_id: str = None):
        self.access_token = access_token or os.environ.get("SQUARE_ACCESS_TOKEN", "")
        self.location_id = location_id or os.environ.get("SQUARE_LOCATION_ID", "")
        if not self.access_token:
            raise RuntimeError(
                "SQUARE_ACCESS_TOKEN not set. "
                "Put it in ~/.clawdbot/.env or pass it directly."
            )

    # ── low-level request ────────────────────────────────────────────────

    def _request(self, endpoint: str, method: str = "GET", data: dict = None,
                 timeout: int = 30) -> dict:
        """Make an authenticated Square API request with retries."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Square-Version": self.API_VERSION,
        }
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        for attempt in range(self.MAX_RETRIES):
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                error_body = e.read().decode()[:300]
                if e.code >= 500 and attempt < self.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"error": f"HTTP {e.code}: {error_body}"}
            except urllib.error.URLError as e:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"error": f"Connection failed: {e}"}
        return {"error": "Max retries exceeded"}

    # ── helpers ──────────────────────────────────────────────────────────

    def _ensure_location(self) -> str:
        """Return a location ID, fetching the first one if not set."""
        if self.location_id:
            return self.location_id
        result = self._request("/locations")
        locs = result.get("locations", [])
        if locs:
            self.location_id = locs[0]["id"]
        return self.location_id

    @staticmethod
    def _dollars(cents: int) -> float:
        return cents / 100 if cents else 0.0

    # ── Locations ────────────────────────────────────────────────────────

    def list_locations(self) -> list:
        """Return list of location dicts."""
        result = self._request("/locations")
        return result.get("locations", [])

    # ── Customers ────────────────────────────────────────────────────────

    def list_customers(self, limit: int = 100) -> list:
        """Return list of customer dicts."""
        result = self._request(f"/customers?limit={limit}")
        return result.get("customers", [])

    def search_customer_by_email(self, email: str) -> dict | None:
        """Find a customer by exact email match."""
        result = self._request("/customers/search", method="POST", data={
            "query": {"filter": {"email_address": {"exact": email}}}
        })
        customers = result.get("customers", [])
        return customers[0] if customers else None

    def create_customer(self, given_name: str, family_name: str = "",
                        email: str = "", phone: str = "",
                        address: dict = None, note: str = "") -> dict:
        """
        Create a new customer.

        address example:
            {"address_line_1": "43 Pinnacle St", "locality": "Sadleir",
             "administrative_district_level_1": "NSW", "postal_code": "2168",
             "country": "AU"}
        """
        payload = {
            "given_name": given_name,
            "idempotency_key": str(uuid.uuid4()),
        }
        if family_name:
            payload["family_name"] = family_name
        if email:
            payload["email_address"] = email
        if phone:
            payload["phone_number"] = phone
        if address:
            payload["address"] = address
        if note:
            payload["note"] = note

        result = self._request("/customers", method="POST", data=payload)
        if "error" in result:
            return result
        return result.get("customer", result)

    # ── Invoices ─────────────────────────────────────────────────────────

    def list_invoices(self, status: str = None) -> list:
        """List invoices, optionally filtered by status (UNPAID, PAID, etc.)."""
        loc = self._ensure_location()
        result = self._request(f"/invoices?location_id={loc}")
        invoices = result.get("invoices", [])
        if status:
            invoices = [i for i in invoices if i.get("status") == status]
        return invoices

    def create_invoice(self, customer_id: str, amount_dollars: float,
                       description: str, due_days: int = 7) -> dict:
        """
        Create, populate, and publish an invoice.
        Returns the invoice dict or error dict.
        """
        loc = self._ensure_location()
        due_date = (datetime.now(SYDNEY_TZ) + timedelta(days=due_days)).strftime("%Y-%m-%d")
        amount_cents = int(round(amount_dollars * 100))

        # Step 1 — create the invoice shell
        create_data = {
            "invoice": {
                "location_id": loc,
                "primary_recipient": {"customer_id": customer_id},
                "payment_requests": [{
                    "request_type": "BALANCE",
                    "due_date": due_date,
                    "automatic_payment_source": "NONE",
                }],
                "delivery_method": "EMAIL",
                "accepted_payment_methods": {"card": True, "bank_account": True},
            },
            "idempotency_key": str(uuid.uuid4()),
        }
        result = self._request("/invoices", method="POST", data=create_data)
        if "error" in result:
            return result

        invoice = result.get("invoice", {})
        inv_id = invoice.get("id")
        version = invoice.get("version", 0)

        # Step 2 — add line item
        update_data = {
            "invoice": {
                "version": version,
                "line_items": [{
                    "name": description,
                    "quantity": "1",
                    "base_price_money": {"amount": amount_cents, "currency": "AUD"},
                }],
            },
            "idempotency_key": str(uuid.uuid4()),
        }
        self._request(f"/invoices/{inv_id}", method="PUT", data=update_data)

        # Step 3 — publish
        publish_data = {
            "version": version + 1,
            "idempotency_key": str(uuid.uuid4()),
        }
        self._request(f"/invoices/{inv_id}/publish", method="POST", data=publish_data)

        invoice["due_date"] = due_date
        return invoice

    def create_invoice_for_email(self, email: str, amount_dollars: float,
                                 description: str, due_days: int = 7) -> dict:
        """
        Convenience: find or create customer by email, then create invoice.
        """
        customer = self.search_customer_by_email(email)
        if not customer:
            create_result = self.create_customer(given_name=email.split("@")[0], email=email)
            if "error" in create_result:
                return create_result
            customer = create_result

        return self.create_invoice(customer["id"], amount_dollars, description, due_days)

    # ── Payments ─────────────────────────────────────────────────────────

    def list_payments(self, days: int = 7, status: str = None) -> list:
        """List payments from the last N days."""
        now_utc = datetime.utcnow()
        end_time = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        start_time = (now_utc - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

        result = self._request(
            f"/payments?begin_time={start_time}&end_time={end_time}"
        )
        payments = result.get("payments", [])
        if status:
            payments = [p for p in payments if p.get("status") == status]
        return payments

    def payments_total(self, days: int = 7) -> float:
        """Sum of COMPLETED payment amounts (dollars) over last N days."""
        payments = self.list_payments(days=days, status="COMPLETED")
        return sum(
            self._dollars(p.get("amount_money", {}).get("amount", 0))
            for p in payments
        )

    # ── Payment Links ────────────────────────────────────────────────────

    def create_payment_link(self, amount_dollars: float, description: str) -> dict:
        """Create a shareable payment link. Returns dict with 'url' key."""
        loc = self._ensure_location()
        amount_cents = int(round(amount_dollars * 100))

        data = {
            "checkout_options": {"ask_for_shipping_address": False},
            "quick_pay": {
                "name": description,
                "price_money": {"amount": amount_cents, "currency": "AUD"},
                "location_id": loc,
            },
            "idempotency_key": str(uuid.uuid4()),
        }
        result = self._request("/online-checkout/payment-links", method="POST", data=data)
        if "error" in result:
            return result
        return result.get("payment_link", result)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _cli():
    sq = SquareAPI()
    args = sys.argv[1:]
    cmd = args[0] if args else "locations"

    if cmd == "locations":
        for loc in sq.list_locations():
            print(f"  • {loc['name']} ({loc.get('status','?')}) — ID: {loc['id']}")

    elif cmd == "customers":
        for c in sq.list_customers():
            name = f"{c.get('given_name','')} {c.get('family_name','')}".strip()
            print(f"  • {name or '(no name)'}  {c.get('email_address','')}  ID: {c['id']}")

    elif cmd == "payments":
        days = int(args[1]) if len(args) > 1 else 7
        total = 0.0
        for p in sq.list_payments(days=days):
            amt = SquareAPI._dollars(p.get("amount_money", {}).get("amount", 0))
            total += amt
            status = p.get("status", "?")
            date = p.get("created_at", "")[:10]
            print(f"  • {date}  ${amt:.2f}  {status}")
        print(f"\n  Total: ${total:.2f}  (last {days} days)")

    elif cmd == "invoices":
        status = args[1].upper() if len(args) > 1 else None
        invoices = sq.list_invoices(status=status)
        if not invoices:
            print(f"  No invoices found{' with status ' + status if status else ''}.")
        for inv in invoices:
            amt_obj = inv.get("payment_requests", [{}])[0].get("computed_amount_money", {})
            amt = SquareAPI._dollars(amt_obj.get("amount", 0))
            print(f"  • #{inv.get('invoice_number','?')}  ${amt:.2f}  {inv.get('status','?')}")

    elif cmd == "link":
        if len(args) < 3:
            print("Usage: square_api.py link <amount> <description>")
            sys.exit(1)
        amount = float(args[1])
        desc = " ".join(args[2:])
        result = sq.create_payment_link(amount, desc)
        if "error" in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  Amount: ${amount:.2f}")
            print(f"  Description: {desc}")

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: locations, customers, payments [days], invoices [status], link <amt> <desc>")
        sys.exit(1)


if __name__ == "__main__":
    _cli()
