#!/usr/bin/env python3
"""
Shared utilities for Bella MCP servers

Provides common functions used across all servers to reduce duplication:
- Environment loading
- HTTP request helpers
- Date/time utilities (Sydney timezone)
- Rate limiting
"""
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from mcp.logging_config import setup_logging

logger = setup_logging("shared_utils")

# Sydney timezone - used across all servers
SYDNEY_TZ = ZoneInfo("Australia/Sydney")

# Standard paths
ENV_FILE = Path.home() / ".clawdbot" / ".env"
DATA_DIR = Path.home() / ".clawdbot" / "data"
LOGS_DIR = Path.home() / ".clawdbot" / "logs"
MEDIA_DIR = Path.home() / ".clawdbot" / "media"
TOKENS_FILE = Path.home() / ".clawdbot" / "google-oauth-tokens.json"


def load_env():
    """
    Load environment variables from ~/.clawdbot/.env

    This is the standard way all MCP servers load their configuration.
    Uses os.environ.setdefault so existing env vars are not overwritten.
    """
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))


def now_sydney() -> datetime:
    """Get current datetime in Sydney timezone"""
    return datetime.now(SYDNEY_TZ)


def format_date_au(dt: datetime = None) -> str:
    """Format datetime as DD/MM/YYYY (Australian format)"""
    if dt is None:
        dt = now_sydney()
    return dt.strftime("%d/%m/%Y")


def format_datetime_au(dt: datetime = None) -> str:
    """Format datetime as DD/MM/YYYY HH:MM (Australian format)"""
    if dt is None:
        dt = now_sydney()
    return dt.strftime("%d/%m/%Y %H:%M")


def api_get(url: str, headers: dict = None, timeout: int = 30) -> dict:
    """
    Make an HTTP GET request and return parsed JSON.

    Args:
        url: Full URL to request
        headers: Optional headers dict
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON response dict, or dict with "error" key on failure
    """
    req = urllib.request.Request(url, headers=headers or {}, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:300]
        logger.error(f"GET {url[:80]} - {e.code}: {error_msg}")
        return {"error": f"HTTP {e.code}: {error_msg}"}
    except urllib.error.URLError as e:
        logger.error(f"GET {url[:80]} - URL Error: {e.reason}")
        return {"error": f"Connection error: {e.reason}"}
    except TimeoutError:
        logger.error(f"GET {url[:80]} - Timeout after {timeout}s")
        return {"error": f"Request timed out after {timeout}s"}
    except json.JSONDecodeError as e:
        logger.error(f"GET {url[:80]} - Invalid JSON: {e}")
        return {"error": f"Invalid JSON response: {e}"}


def api_post(url: str, data: dict = None, headers: dict = None, timeout: int = 30) -> dict:
    """
    Make an HTTP POST request with JSON body and return parsed JSON.

    Args:
        url: Full URL to request
        data: Dict to send as JSON body
        headers: Optional headers dict
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON response dict, or dict with "error" key on failure
    """
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=default_headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()[:300]
        logger.error(f"POST {url[:80]} - {e.code}: {error_msg}")
        return {"error": f"HTTP {e.code}: {error_msg}"}
    except urllib.error.URLError as e:
        logger.error(f"POST {url[:80]} - URL Error: {e.reason}")
        return {"error": f"Connection error: {e.reason}"}
    except TimeoutError:
        logger.error(f"POST {url[:80]} - Timeout after {timeout}s")
        return {"error": f"Request timed out after {timeout}s"}
    except json.JSONDecodeError as e:
        logger.error(f"POST {url[:80]} - Invalid JSON: {e}")
        return {"error": f"Invalid JSON response: {e}"}


class RateLimiter:
    """
    Simple rate limiter for API calls.

    Usage:
        limiter = RateLimiter(max_calls=10, period=60)  # 10 calls per minute
        if limiter.allow():
            # make API call
        else:
            # rate limited, wait or skip
    """

    def __init__(self, max_calls: int = 10, period: float = 60.0):
        self.max_calls = max_calls
        self.period = period
        self._calls: list[float] = []

    def allow(self) -> bool:
        """Check if a call is allowed under the rate limit"""
        now = time.time()
        # Remove calls outside the window
        self._calls = [t for t in self._calls if now - t < self.period]

        if len(self._calls) < self.max_calls:
            self._calls.append(now)
            return True
        return False

    def wait_time(self) -> float:
        """Get seconds to wait before next allowed call"""
        if self.allow():
            # Remove the call we just added for the check
            self._calls.pop()
            return 0.0
        oldest = min(self._calls)
        return self.period - (time.time() - oldest)


def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist and return it"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_json_load(file_path: Path, default: dict = None) -> dict:
    """
    Safely load JSON from file, returning default on any error.

    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Parsed JSON dict or default value
    """
    if default is None:
        default = {}

    if not file_path.exists():
        return default

    try:
        with open(file_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to load {file_path}: {e}")
        return default


def safe_json_save(file_path: Path, data: dict) -> bool:
    """
    Safely save dict as JSON to file.

    Args:
        file_path: Path to save to
        data: Dict to serialize

    Returns:
        True on success, False on failure
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except (IOError, TypeError) as e:
        logger.error(f"Failed to save {file_path}: {e}")
        return False
