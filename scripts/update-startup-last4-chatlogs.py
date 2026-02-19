#!/usr/bin/env python3
"""
Build startup memory references from the last 4 non-cron Bella chat logs.

Outputs:
- memory/startup-last4-chatlogs.md
- memory/YYYY-MM-DD-last4-chatlogs.md
- appends note to memory/YYYY-MM-DD.md
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Australia/Sydney")


def parse_ts(ts: str) -> datetime:
    if not ts:
        return datetime(1970, 1, 1, tzinfo=TZ)
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)
    except Exception:
        return datetime(1970, 1, 1, tzinfo=TZ)


def flatten_content(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                txt = item.get("text") or item.get("content") or ""
                if txt:
                    parts.append(str(txt))
        return " ".join(parts).strip()
    if isinstance(content, dict):
        return str(content.get("text") or content.get("content") or "").strip()
    return ""


def compact_text(s: str, limit: int = 220) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= limit:
        return s
    return s[: limit - 1] + "…"


def select_sessions(meta: dict) -> list[tuple[str, dict]]:
    rows = []
    for key, value in meta.items():
        if ":cron:" in key:
            continue
        if key.endswith(":heartbeat"):
            continue
        sid = str(value.get("sessionId", "")).strip()
        if not sid:
            continue
        rows.append((key, value))
    rows.sort(key=lambda kv: int(kv[1].get("updatedAt", 0) or 0), reverse=True)
    return rows[:4]


def extract_tail_pairs(jsonl_path: Path, max_pairs: int = 6) -> list[tuple[str, str]]:
    lines = jsonl_path.read_text(errors="ignore").splitlines() if jsonl_path.exists() else []
    msgs = []
    for ln in lines:
        try:
            obj = json.loads(ln)
        except Exception:
            continue
        if obj.get("type") != "message":
            continue
        msg = obj.get("message") or {}
        role = msg.get("role")
        if role not in {"user", "assistant"}:
            continue
        txt = compact_text(flatten_content(msg.get("content")))
        if not txt:
            continue
        msgs.append((role, txt))

    # Keep latest user->assistant pairs.
    out: list[tuple[str, str]] = []
    i = len(msgs) - 1
    while i >= 0 and len(out) < max_pairs:
        role, txt = msgs[i]
        if role == "assistant":
            user_txt = ""
            j = i - 1
            while j >= 0:
                if msgs[j][0] == "user":
                    user_txt = msgs[j][1]
                    break
                j -= 1
            out.append((user_txt, txt))
        i -= 1
    out.reverse()
    return out


def main() -> int:
    base = Path.home() / ".clawdbot" / "agents" / "main" / "sessions"
    sessions_file = base / "sessions.json"
    if not sessions_file.exists():
        print("No sessions.json found")
        return 1

    meta = json.loads(sessions_file.read_text())
    top = select_sessions(meta)

    now = datetime.now(TZ)
    day = now.strftime("%Y-%m-%d")
    stamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    mem_dir = Path("/Users/hafsahnuzhat/Desktop/🦀/memory")
    mem_dir.mkdir(parents=True, exist_ok=True)

    startup_ref = mem_dir / "startup-last4-chatlogs.md"
    dated_ref = mem_dir / f"{day}-last4-chatlogs.md"
    today_log = mem_dir / f"{day}.md"

    lines = []
    lines.append(f"# Startup Last 4 Chat Logs ({stamp})")
    lines.append("")
    lines.append("Use this file first on new startup to recover immediate context.")
    lines.append("")

    if not top:
        lines.append("No chat sessions found.")
    else:
        for idx, (key, val) in enumerate(top, 1):
            sid = val.get("sessionId", "")
            chat_type = val.get("chatType") or "unknown"
            if val.get("updatedAt"):
                updated_iso = datetime.fromtimestamp((val.get("updatedAt", 0) or 0) / 1000, TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
            else:
                updated_iso = "unknown"
            p = base / f"{sid}.jsonl"
            pairs = extract_tail_pairs(p, max_pairs=4)

            lines.append(f"## {idx}. {key}")
            lines.append(f"- session_id: `{sid}`")
            lines.append(f"- chat_type: `{chat_type}`")
            lines.append(f"- updated: `{updated_iso}`")
            lines.append("")

            if not pairs:
                lines.append("- No user/assistant message pairs found.")
            else:
                for u, a in pairs:
                    if u:
                        lines.append(f"- user: {u}")
                    lines.append(f"- bella: {a}")
            lines.append("")

    body = "\n".join(lines).strip() + "\n"
    startup_ref.write_text(body)
    dated_ref.write_text(body)

    note = (
        f"\n## 🧠 Startup Chat Context Refresh ({stamp})\n"
        f"- Generated `memory/startup-last4-chatlogs.md` from last 4 non-cron sessions.\n"
        f"- Snapshot copy: `memory/{day}-last4-chatlogs.md`.\n"
        f"- Rule: read startup file at beginning of new chat to retain near-term context.\n"
    )
    if today_log.exists():
        text = today_log.read_text()
        if f"Startup Chat Context Refresh ({stamp})" not in text:
            today_log.write_text(text.rstrip() + "\n" + note)
    else:
        today_log.write_text(f"# {day}\n" + note)

    print(f"Wrote {startup_ref}")
    print(f"Wrote {dated_ref}")
    print(f"Updated {today_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
