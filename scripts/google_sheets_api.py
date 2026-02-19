#!/usr/bin/env python3
"""
Google Sheets API Wrapper — Standalone
Read, append, update, and list sheets using OAuth tokens.

Extracted from: archive/mcp/google_server.py, archive/mcp/accounting_server.py
No external dependencies — stdlib only.
Loads tokens from ~/.clawdbot/google-oauth-tokens.json
Loads client creds from ~/.clawdbot/.env

Usage as module:
    from google_sheets_api import GoogleSheetsAPI
    gs = GoogleSheetsAPI()
    data = gs.read("Income!A:E")
    gs.append("Income!A:F", ["2026-01-15", "Client", "Desc", "$500", "Card"])

Usage standalone:
    python3 google_sheets_api.py list                       # list sheet tabs
    python3 google_sheets_api.py read "Income!A1:E10"       # read range
    python3 google_sheets_api.py append "Income!A:E" val1 val2 val3
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


# ─── Env & Token Loading ─────────────────────────────────────────────────────

ENV_FILE = Path.home() / ".clawdbot" / ".env"
TOKEN_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"


def _load_env():
    """Read ~/.clawdbot/.env into os.environ (won't overwrite)."""
    if not ENV_FILE.exists():
        return
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"'))

_load_env()


def _load_tokens() -> dict:
    """Load OAuth tokens from disk."""
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            f"Token file not found: {TOKEN_FILE}\n"
            "Run google-oauth-setup.py to authorize."
        )
    with open(TOKEN_FILE) as f:
        return json.load(f)


def _save_tokens(tokens: dict):
    """Persist tokens back to disk with restricted perms."""
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except OSError:
        pass


def _refresh_access_token(tokens: dict) -> str | None:
    """
    Refresh the access token using the stored refresh_token.
    Updates the token file on success.
    Returns the new access token or None on failure.
    """
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        return None

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None

    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            new = json.loads(resp.read().decode())
            tokens["access_token"] = new["access_token"]
            _save_tokens(tokens)
            return new["access_token"]
    except (urllib.error.HTTPError, urllib.error.URLError, KeyError, json.JSONDecodeError):
        return None


def get_access_token() -> str:
    """
    Return a valid Google access token, refreshing automatically if possible.
    """
    tokens = _load_tokens()
    # Always try to refresh — tokens expire after 1 hour
    refreshed = _refresh_access_token(tokens)
    if refreshed:
        return refreshed
    # Fallback to stored token (may be expired)
    token = tokens.get("access_token")
    if not token:
        raise RuntimeError("No access token available. Run google-oauth-setup.py")
    return token


# ─── Google Sheets Client ────────────────────────────────────────────────────

class GoogleSheetsAPI:
    """Standalone Google Sheets client — stdlib only."""

    BASE = "https://sheets.googleapis.com/v4/spreadsheets"

    def __init__(self, spreadsheet_id: str = None):
        self.spreadsheet_id = spreadsheet_id or os.environ.get("GOOGLE_SHEETS_ID", "")
        if not self.spreadsheet_id:
            raise ValueError(
                "No spreadsheet ID. Set GOOGLE_SHEETS_ID in ~/.clawdbot/.env "
                "or pass spreadsheet_id directly."
            )

    # ── low-level ────────────────────────────────────────────────────────

    def _request(self, endpoint: str, method: str = "GET",
                 data: dict = None, timeout: int = 30) -> dict:
        """Authenticated Sheets API request."""
        token = get_access_token()
        url = f"{self.BASE}/{self.spreadsheet_id}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}

        body = None
        if data:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode()

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode()[:300]
            return {"error": f"HTTP {e.code}: {error_msg}"}
        except urllib.error.URLError as e:
            return {"error": f"Connection failed: {e}"}

    # ── public API ───────────────────────────────────────────────────────

    def info(self) -> dict:
        """Get spreadsheet metadata (title, sheet names, etc.)."""
        return self._request("")

    def list_sheets(self) -> list[str]:
        """Return list of sheet tab names."""
        result = self.info()
        if "error" in result:
            return []
        return [s["properties"]["title"] for s in result.get("sheets", [])]

    def read(self, range_str: str) -> list[list]:
        """
        Read a range. Returns list of rows (each row is a list of cell values).

        range_str examples: 'Income!A:E', 'Sheet1!A1:D10'
        """
        endpoint = f"/values/{urllib.parse.quote(range_str)}"
        result = self._request(endpoint)
        if "error" in result:
            raise RuntimeError(result["error"])
        return result.get("values", [])

    def append(self, range_str: str, values: list) -> dict:
        """
        Append a single row.

        values: list of cell values, e.g. ['2026-01-15', 'Client', '$500']
        """
        endpoint = (
            f"/values/{urllib.parse.quote(range_str)}:append"
            "?valueInputOption=USER_ENTERED"
        )
        return self._request(endpoint, method="POST", data={"values": [values]})

    def append_rows(self, range_str: str, rows: list[list]) -> dict:
        """Append multiple rows at once."""
        endpoint = (
            f"/values/{urllib.parse.quote(range_str)}:append"
            "?valueInputOption=USER_ENTERED"
        )
        return self._request(endpoint, method="POST", data={"values": rows})

    def update(self, range_str: str, values: list[list]) -> dict:
        """
        Overwrite a range with new values.

        values: list of rows, each row a list of cell values.
        """
        endpoint = (
            f"/values/{urllib.parse.quote(range_str)}"
            "?valueInputOption=USER_ENTERED"
        )
        return self._request(endpoint, method="PUT", data={"values": values})

    def clear(self, range_str: str) -> dict:
        """Clear a range of cells."""
        endpoint = f"/values/{urllib.parse.quote(range_str)}:clear"
        return self._request(endpoint, method="POST")

    def batch_get(self, ranges: list[str]) -> dict:
        """Read multiple ranges in one API call."""
        params = "&".join(f"ranges={urllib.parse.quote(r)}" for r in ranges)
        endpoint = f"/values:batchGet?{params}"
        return self._request(endpoint)

    def batch_update_spreadsheet(self, requests: list[dict]) -> dict:
        """
        Run structural/formatting updates via spreadsheets.batchUpdate.
        """
        endpoint = ":batchUpdate"
        return self._request(endpoint, method="POST", data={"requests": requests})


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _cli():
    args = sys.argv[1:]
    if not args:
        print("Usage: google_sheets_api.py <command> [args...]")
        print("Commands: list, read <range>, append <range> val1 val2 ..., info")
        sys.exit(1)

    cmd = args[0]
    gs = GoogleSheetsAPI()

    if cmd == "list":
        sheets = gs.list_sheets()
        print(f"Sheets in spreadsheet {gs.spreadsheet_id}:")
        for name in sheets:
            print(f"  • {name}")

    elif cmd == "info":
        result = gs.info()
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        title = result.get("properties", {}).get("title", "?")
        sheets = [s["properties"]["title"] for s in result.get("sheets", [])]
        print(f"Title: {title}")
        print(f"Sheets: {', '.join(sheets)}")
        print(f"URL: https://docs.google.com/spreadsheets/d/{gs.spreadsheet_id}")

    elif cmd == "read":
        if len(args) < 2:
            print("Usage: read <range>  (e.g. 'Income!A1:E10')")
            sys.exit(1)
        try:
            rows = gs.read(args[1])
        except RuntimeError as e:
            print(f"Error: {e}")
            sys.exit(1)
        if not rows:
            print("(empty)")
        else:
            for row in rows[:30]:  # limit output
                print(" | ".join(str(c) for c in row))
            if len(rows) > 30:
                print(f"  ... ({len(rows)} total rows, showing first 30)")

    elif cmd == "append":
        if len(args) < 3:
            print("Usage: append <range> val1 val2 val3 ...")
            sys.exit(1)
        range_str = args[1]
        values = args[2:]
        result = gs.append(range_str, values)
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        updated = result.get("updates", {}).get("updatedRange", range_str)
        print(f"Row appended to {updated}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    _cli()
