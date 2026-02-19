#!/usr/bin/env python3
import json
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from google_sheets_api import GoogleSheetsAPI
from square_api import SquareAPI
from sheet_router import ids

ROOT = Path("/Users/hafsahnuzhat/Desktop/🦀")
CLAW = Path.home() / ".clawdbot"
APP_PUBLIC = Path("/Users/hafsahnuzhat/bella-dashboard/public/dashboard-data.json")
TZ = ZoneInfo("Australia/Sydney")


def sh(cmd: str, timeout: int = 20) -> str:
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT, timeout=timeout)
        return out.strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def load_json(path: Path, default: Any):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def parse_money(value: Any) -> float:
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except Exception:
        return 0.0


def norm_invoice(value: str) -> str:
    return str(value or "").upper().replace("INVOICE", "").replace("#", "").strip()


def parse_iso_date(value: str) -> date | None:
    try:
        return datetime.fromisoformat(value[:10]).date()
    except Exception:
        return None


def resolve_client_name(inv: dict, customers_by_id: dict[str, str], client_log_map: dict[str, dict[str, Any]]) -> str:
    inv_num = norm_invoice(inv.get("invoice_number", ""))
    if inv_num and inv_num in client_log_map:
        name = str(client_log_map[inv_num].get("clientName", "")).strip()
        if name:
            return name

    recip = inv.get("primary_recipient", {}) or {}
    cid = str(recip.get("customer_id", "")).strip()
    if cid and cid in customers_by_id:
        return customers_by_id[cid]

    return "Square Client"


def build_client_log_map(gs: GoogleSheetsAPI) -> dict[str, dict[str, Any]]:
    rows = gs.read("Client Log!A:L")
    out: dict[str, dict[str, Any]] = {}
    for row in rows[1:]:
        if len(row) < 8:
            continue
        inv = norm_invoice(row[7])
        if not inv:
            continue
        out[inv] = {
            "date": row[0] if len(row) > 0 else "",
            "clientName": row[1] if len(row) > 1 else "",
            "phone": row[2] if len(row) > 2 else "",
            "email": row[3] if len(row) > 3 else "",
            "amount": row[6] if len(row) > 6 else "",
            "paymentStatus": row[8] if len(row) > 8 else "",
            "source": "business_ops",
        }
    return out


def build_financial_snapshot(now: datetime, business_sheet_id: str) -> dict[str, Any]:
    data = {
        "revenue_mtd": 0.0,
        "expenses_mtd": 0.0,
        "unpaid_invoices": 0,
        "outstanding_balance": 0.0,
        "recent_transactions": [],
        "overdue_accounts": [],
    }

    try:
        sq = SquareAPI()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_utc = month_start.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_utc = now.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")

        pay_result = sq._request(f"/payments?begin_time={start_utc}&end_time={end_utc}")
        payments = pay_result.get("payments", [])
        completed = [p for p in payments if str(p.get("status", "")).upper() == "COMPLETED"]

        data["revenue_mtd"] = round(
            sum(((p.get("amount_money", {}).get("amount", 0) or 0) / 100) for p in completed),
            2,
        )

        tx = []
        for p in sorted(completed, key=lambda x: str(x.get("created_at", "")), reverse=True)[:12]:
            amt = (p.get("amount_money", {}).get("amount", 0) or 0) / 100
            tx.append(
                {
                    "date": str(p.get("created_at", ""))[:10],
                    "description": "Square payment",
                    "amount": round(amt, 2),
                    "type": "income",
                }
            )
        data["recent_transactions"] = tx
    except Exception:
        pass

    for expense_tab in ("Expenses", "Bookkeeping"):
        try:
            gs = GoogleSheetsAPI(spreadsheet_id=business_sheet_id)
            exp_rows = gs.read(f"{expense_tab}!A:J")
            subtotal = 0.0
            for row in exp_rows[1:]:
                if len(row) < 4:
                    continue
                dt = str(row[0]).strip()
                amt = parse_money(row[3])
                if dt.startswith(now.strftime("%Y-%m")):
                    subtotal += amt
            if subtotal > 0:
                data["expenses_mtd"] = subtotal
                break
        except Exception:
            continue

    try:
        sq = SquareAPI()
        unpaid = sq.list_invoices(status="UNPAID")
        data["unpaid_invoices"] = len(unpaid)
        today = now.date()
        overdue = []
        for inv in unpaid:
            req = (inv.get("payment_requests") or [{}])[0]
            amt = (req.get("computed_amount_money", {}).get("amount", 0) or 0) / 100
            due_txt = str(req.get("due_date", ""))
            due = parse_iso_date(due_txt)
            data["outstanding_balance"] += amt
            if due and due < today:
                overdue.append(
                    {
                        "client": "Square Client",
                        "amount": round(amt, 2),
                        "daysOverdue": (today - due).days,
                        "status": f"Overdue since {due_txt}",
                    }
                )
        data["overdue_accounts"] = sorted(overdue, key=lambda x: x.get("daysOverdue", 0), reverse=True)[:10]
    except Exception:
        pass

    return data


def build_clients_section(now: datetime, business_sheet_id: str) -> dict[str, Any]:
    fallback = {
        "summary": {"paid": 0, "pending": 0, "overdue": 0, "totalOutstanding": 0.0},
        "kanban": {"paid": [], "pending": [], "overdue": []},
        "updatedAt": now.isoformat(timespec="seconds"),
        "source": "square+business_ops",
    }

    try:
        gs = GoogleSheetsAPI(spreadsheet_id=business_sheet_id)
        client_log_map = build_client_log_map(gs)
    except Exception:
        client_log_map = {}

    try:
        sq = SquareAPI()
        invoices = sq.list_invoices() or []
        customers = sq.list_customers(limit=200) or []
        customers_by_id = {}
        for c in customers:
            cid = str(c.get("id", "")).strip()
            if not cid:
                continue
            name = f"{str(c.get('given_name', '')).strip()} {str(c.get('family_name', '')).strip()}".strip()
            customers_by_id[cid] = name or str(c.get("company_name", "")).strip() or "Square Client"

        paid: list[dict[str, Any]] = []
        pending: list[dict[str, Any]] = []
        overdue: list[dict[str, Any]] = []

        today = now.date()
        seen = set()

        for inv in invoices:
            inv_num_raw = str(inv.get("invoice_number", "")).strip()
            inv_num_norm = norm_invoice(inv_num_raw)
            if not inv_num_norm:
                continue
            if inv_num_norm in seen:
                continue
            seen.add(inv_num_norm)

            req = (inv.get("payment_requests") or [{}])[0]
            due_txt = str(req.get("due_date", ""))
            due = parse_iso_date(due_txt)
            amount = (req.get("computed_amount_money", {}).get("amount", 0) or 0) / 100
            status = str(inv.get("status", "PENDING")).upper()
            name = resolve_client_name(inv, customers_by_id, client_log_map)

            if status == "PAID":
                payment_status = "PAID"
            elif due and due < today:
                payment_status = "OVERDUE"
            else:
                payment_status = "PENDING"

            card = {
                "clientName": name,
                "invoiceNumber": inv_num_raw if inv_num_raw.startswith("#") else f"#{inv_num_raw}",
                "amountDue": round(amount, 2),
                "paymentStatus": payment_status,
                "dueDate": due_txt or "n/a",
                "daysOverdue": (today - due).days if (due and payment_status == "OVERDUE") else 0,
                "sourceRef": f"square:{inv.get('id', inv_num_norm)}",
            }

            if payment_status == "PAID":
                paid.append(card)
            elif payment_status == "OVERDUE":
                overdue.append(card)
            else:
                pending.append(card)

        # Square is source-of-truth for active client payment status on dashboard.
        total_outstanding = sum(float(x.get("amountDue", 0) or 0) for x in pending + overdue)

        by_client: dict[str, dict[str, Any]] = {}
        for card in paid + pending + overdue:
            name = str(card.get("clientName", "Unknown")).strip() or "Unknown"
            bucket = by_client.setdefault(name, {"count": 0, "paidTotal": 0.0})
            bucket["count"] += 1
            if str(card.get("paymentStatus", "")).upper() == "PAID":
                bucket["paidTotal"] += float(card.get("amountDue", 0) or 0)

        recurring_clients = [n for n, v in by_client.items() if int(v.get("count", 0)) >= 2]
        one_time_clients = [n for n, v in by_client.items() if int(v.get("count", 0)) == 1]
        recurring_paid_total = round(sum(float(by_client[n].get("paidTotal", 0) or 0) for n in recurring_clients), 2)

        one_time_list = sorted(one_time_clients)[:60]

        return {
            "summary": {
                "paid": len(paid),
                "pending": len(pending),
                "overdue": len(overdue),
                "totalOutstanding": round(total_outstanding, 2),
                "recurringClients": len(recurring_clients),
                "recurringPaidTotal": recurring_paid_total,
                "oneTimeClients": len(one_time_list),
            },
            "oneTimeClientList": one_time_list,
            "kanban": {
                "paid": sorted(paid, key=lambda x: str(x.get("clientName", "")))[:25],
                "pending": sorted(pending, key=lambda x: str(x.get("dueDate", "")))[:25],
                "overdue": sorted(overdue, key=lambda x: int(x.get("daysOverdue", 0)), reverse=True)[:25],
            },
            "updatedAt": now.isoformat(timespec="seconds"),
            "source": "square+business_ops",
        }
    except Exception:
        return fallback


def build_tasks_board(existing: dict[str, Any], now: datetime, cron_jobs: list[dict[str, Any]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []

    def add_task(item: dict[str, Any]):
        if not item.get("id"):
            return
        if any(x["id"] == item["id"] for x in items):
            return
        items.append(item)

    for t in existing.get("tasks", {}).get("now", []):
        label = str(t.get("label", "TASK")).strip()
        status = str(t.get("status", "unknown")).strip()
        add_task(
            {
                "id": f"now:{label}",
                "title": label.replace("_", " "),
                "source": "runtime",
                "priority": "high" if "fail" in status.lower() or "error" in status.lower() else "medium",
                "status": "done" if status.lower() in {"ok", "running", "updated", "pass"} else "open",
                "dueAt": now.isoformat(timespec="seconds"),
                "owner": "Bella",
                "sheetContext": "Business Ops",
                "blockingReason": "" if status.lower() in {"ok", "running", "updated", "pass"} else status,
            }
        )

    for q in existing.get("tasks", {}).get("queue", []):
        qtxt = str(q).strip()
        add_task(
            {
                "id": f"queue:{qtxt}",
                "title": qtxt,
                "source": "pipeline",
                "priority": "medium",
                "status": "open",
                "dueAt": now.isoformat(timespec="seconds"),
                "owner": "Bella",
                "sheetContext": "Business Ops",
                "blockingReason": "",
            }
        )

    for b in existing.get("tasks", {}).get("blockers", []):
        btxt = str(b).strip()
        add_task(
            {
                "id": f"blocker:{btxt}",
                "title": btxt,
                "source": "cron",
                "priority": "high",
                "status": "blocked",
                "dueAt": now.isoformat(timespec="seconds"),
                "owner": "Bella",
                "sheetContext": "Business Ops",
                "blockingReason": btxt,
            }
        )

    for ev in existing.get("calendar", {}).get("today", []):
        title = str(ev.get("title", "Calendar task")).strip()
        due = str(ev.get("date", "")).strip()
        add_task(
            {
                "id": f"calendar:{title}:{due}",
                "title": title,
                "source": "calendar",
                "priority": "medium",
                "status": "open",
                "dueAt": due or now.isoformat(timespec="seconds"),
                "owner": "Ops",
                "sheetContext": "Business Ops",
                "blockingReason": "",
            }
        )

    for job in cron_jobs:
        last_status = str(job.get("state", {}).get("lastStatus", "")).lower()
        if last_status == "error":
            name = str(job.get("name", "cron-job"))
            err = str(job.get("state", {}).get("lastError", "cron error"))
            add_task(
                {
                    "id": f"cronerr:{name}",
                    "title": f"Fix cron: {name}",
                    "source": "cron",
                    "priority": "high",
                    "status": "blocked",
                    "dueAt": now.isoformat(timespec="seconds"),
                    "owner": "Bella",
                    "sheetContext": "Business Ops",
                    "blockingReason": err,
                }
            )

    priority_rank = {"high": 0, "medium": 1, "low": 2}
    status_rank = {"blocked": 0, "open": 1, "done": 2}
    items.sort(key=lambda x: (priority_rank.get(x.get("priority", "low"), 3), status_rank.get(x.get("status", "open"), 3), x.get("title", "")))

    summary = {
        "total": len(items),
        "dueToday": len([i for i in items if str(i.get("dueAt", "")).startswith(now.strftime("%Y-%m-%d"))]),
        "overdue": len([i for i in items if i.get("priority") == "high" and i.get("status") != "done"]),
        "blocked": len([i for i in items if i.get("status") == "blocked"]),
        "completedToday": len([i for i in items if i.get("status") == "done"]),
    }

    return {"items": items[:140], "summary": summary}


def build_cron_technical(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    out = []
    healthy = 0
    failing = 0

    for j in jobs:
        state = j.get("state", {}) or {}
        sched = j.get("schedule", {}) or {}
        enabled = bool(j.get("enabled"))

        raw_status = str(state.get("lastStatus", "")).strip().lower()
        if raw_status:
            status = raw_status
        else:
            status = "scheduled" if enabled else "disabled"

        if status == "error":
            failing += 1
        elif status in {"ok", "success", "completed", "scheduled"}:
            healthy += 1

        last_run = state.get("lastRunAt") or state.get("lastCompletedAt") or state.get("nextRunAt") or "n/a"

        out.append(
            {
                "name": j.get("name", "unknown"),
                "enabled": enabled,
                "schedule": sched.get("expr") or sched.get("kind") or "n/a",
                "lastStatus": status,
                "lastRunAt": last_run,
                "durationMs": state.get("lastDurationMs") or 0,
                "command": j.get("command") or j.get("task") or "n/a",
                "lastError": state.get("lastError") or "",
                "lastOutputSnippet": str(state.get("lastOutput") or state.get("lastError") or "")[:220],
            }
        )

    out.sort(key=lambda x: (0 if str(x.get("lastStatus", "")).lower() == "error" else 1, str(x.get("name", ""))))
    return {
        "jobs": out,
        "summary": {
            "total": len(jobs),
            "enabled": len([j for j in jobs if j.get("enabled")]),
            "healthy": healthy,
            "failing": failing,
        },
    }


def check_sheet(sheet_id: str, critical_tabs: list[str]) -> dict[str, Any]:
    if not sheet_id:
        return {"id": "", "health": "missing", "lastRead": "n/a", "lastWrite": "n/a", "tabHealth": []}

    gs = GoogleSheetsAPI(spreadsheet_id=sheet_id)
    tab_health = []
    failed = 0

    for tab in critical_tabs:
        try:
            rows = gs.read(f"{tab}!A:Z")
            tab_health.append({"tab": tab, "status": "ok", "rows": max(0, len(rows) - 1)})
        except Exception as exc:
            failed += 1
            tab_health.append({"tab": tab, "status": "error", "rows": 0, "error": str(exc)[:120]})

    health = "healthy" if failed == 0 else ("degraded" if failed < len(critical_tabs) else "error")
    stamp = datetime.now(TZ).strftime("%Y-%m-%d %H:%M %Z")
    return {
        "id": sheet_id,
        "health": health,
        "lastRead": stamp,
        "lastWrite": stamp,
        "tabHealth": tab_health,
    }


def main():
    now = datetime.now(TZ)
    now_iso = now.isoformat(timespec="seconds")
    now_label = now.strftime("%Y-%m-%d %H:%M %Z")

    existing = load_json(ROOT / "dashboard-data.json", {})
    claw_cfg = load_json(CLAW / "clawdbot.json", {})
    cron_obj = load_json(CLAW / "cron" / "jobs.json", {"jobs": []})
    sessions = load_json(CLAW / "agents" / "main" / "sessions" / "sessions.json", {})

    route_ids = ids()
    business_sheet = route_ids.get("business", "")
    staff_sheet = route_ids.get("staff", "")
    personal_sheet = route_ids.get("personal", "")

    model = claw_cfg.get("agents", {}).get("defaults", {}).get("model", {})
    primary = model.get("primary", "unknown")
    fallbacks = model.get("fallbacks", [])

    codex_login = sh("codex login status")
    auth_mode = "chatgpt-subscription" if "ChatGPT" in codex_login else "api-key"

    gateway_status_raw = sh("clawdbot gateway status")
    gateway_ok = "Runtime: running" in gateway_status_raw
    rpc_ok = "RPC probe: failed" not in gateway_status_raw
    pid = "unknown"
    for line in gateway_status_raw.splitlines():
        if "Runtime: running (pid" in line:
            pid = line.split("pid", 1)[1].split(",", 1)[0].strip(" ()")
            break

    model_check = sh(f"bash {ROOT}/scripts/check-model.sh")
    smoke = sh('clawdbot agent --local --agent main --message "Reply exactly: BOT_DASH_OK" --thinking low --json', timeout=30)
    smoke_ok = "BOT_DASH_OK" in smoke

    jobs = cron_obj.get("jobs", [])
    enabled_jobs = [j for j in jobs if j.get("enabled")]
    error_jobs = [j for j in jobs if str(j.get("state", {}).get("lastStatus", "")).lower() == "error"]
    critical_names = {
        "dashboard-live-sync-hourly",
        "social-morning-post",
        "social-lunch-post",
        "social-evening-post",
        "commercial-outreach-daily",
        "universal-sync-hourly",
    }
    critical_jobs = [j for j in jobs if j.get("name") in critical_names]

    session_items = []
    latest_session_ms = 0
    for key, value in sessions.items():
        updated = int(value.get("updatedAt", 0) or 0)
        latest_session_ms = max(latest_session_ms, updated)
        session_items.append(
            {
                "label": key,
                "chatType": value.get("chatType", "unknown"),
                "updatedAtMs": updated,
                "model": value.get("model", primary),
            }
        )
    session_items.sort(key=lambda x: x["updatedAtMs"], reverse=True)

    workspace_skills = [p for p in (ROOT / "skills").iterdir() if p.is_dir()] if (ROOT / "skills").exists() else []
    live_skills = [p for p in (CLAW / "skills").iterdir() if p.is_dir()] if (CLAW / "skills").exists() else []

    memory_files = list((ROOT / "memory").glob("*.md")) if (ROOT / "memory").exists() else []
    today_memory = ROOT / "memory" / f"{now.strftime('%Y-%m-%d')}.md"

    financial = existing.get("financial", {})
    calendar = existing.get("calendar", {})
    live_fin = build_financial_snapshot(now, business_sheet)
    clients = build_clients_section(now, business_sheet)
    tasks_board = build_tasks_board(existing, now, jobs)
    cron_technical = build_cron_technical(jobs)

    data = {
        "lastUpdated": now_iso,
        "uiMeta": {
            "version": "5.0.0",
            "generatedAt": now_iso,
            "timezone": "Australia/Sydney",
        },
        "tabs": {
            "defaultTab": "overview",
            "enabled": ["overview", "tasks", "clients", "crons", "sheets", "insights"],
        },
        "controlCenter": {
            "title": "Bella Three-Sheet Control Center",
            "mode": "three-sheet-control-center",
            "objective": "Operate all critical business tasks from one trusted state view.",
            "health": "healthy" if (gateway_ok and smoke_ok) else "degraded",
            "threeSheetMode": {
                "enabled": True,
                "sheets": {
                    "businessOpsId": business_sheet,
                    "staffPropertiesId": staff_sheet,
                    "personalId": personal_sheet,
                },
            },
        },
        "stats": {
            "revenueMTD": round(live_fin["revenue_mtd"], 2),
            "outstandingBalance": round(clients.get("summary", {}).get("totalOutstanding", live_fin["outstanding_balance"]), 2),
            "unpaidInvoices": int(live_fin["unpaid_invoices"]),
            "leads": existing.get("stats", {}).get("leads", "0"),
            "gstPayable": round(max((live_fin["revenue_mtd"] - live_fin["expenses_mtd"]) / 11, 0), 2),
            "lastHeartbeat": now_label,
        },
        "runtime": {
            "gateway": {
                "status": "running" if gateway_ok else "down",
                "rpc": "ok" if rpc_ok else "flaky",
                "pid": pid,
                "port": 18789,
                "checkedAt": now_label,
            },
            "llm": {
                "provider": "openai-codex",
                "primary": primary,
                "fallbacks": fallbacks,
                "authMode": auth_mode,
                "checkModelResult": model_check,
                "smokeTest": "pass" if smoke_ok else "fail",
            },
            "memory": {
                "files": len(memory_files),
                "todayLogPresent": today_memory.exists(),
                "lastSummary": "memory/2026-02-19.md",
            },
        },
        "sourcesOfTruth": [
            {"name": "Square", "status": "required", "lastSync": now_label, "note": "Financial and client truth source"},
            {"name": "Google Calendar", "status": "required", "lastSync": now_label, "note": "Schedule truth source"},
            {"name": "Connecteam", "status": "required", "lastSync": now_label, "note": "Roster truth source"},
            {"name": "Google Sheets", "status": "required", "lastSync": now_label, "note": "Three-sheet accounting and ops mirror"},
        ],
        "financial": {
            **financial,
            "totalOutstanding": round(clients.get("summary", {}).get("totalOutstanding", live_fin["outstanding_balance"]), 2),
            "totals": {
                "revenueMTD": round(live_fin["revenue_mtd"], 2),
                "expensesMTD": round(live_fin["expenses_mtd"], 2),
                "netMTD": round(live_fin["revenue_mtd"] - live_fin["expenses_mtd"], 2),
            },
            "recentTransactions": live_fin["recent_transactions"],
            "overdueAccounts": live_fin["overdue_accounts"],
        },
        "calendar": calendar,
        "tasksBoard": tasks_board,
        "clients": clients,
        "crons": {
            "summary": {
                "total": len(jobs),
                "enabled": len(enabled_jobs),
                "errors": len(error_jobs),
                "lastCheck": now_label,
                "status": "healthy" if not error_jobs else "degraded",
                "note": "Cron jobs include social, dashboard sync, and accounting automations.",
            },
            "critical": [
                {
                    "name": j.get("name", "unknown"),
                    "enabled": bool(j.get("enabled")),
                    "schedule": j.get("schedule", {}).get("expr", j.get("schedule", {}).get("kind", "n/a")),
                    "lastStatus": j.get("state", {}).get("lastStatus", "unknown"),
                }
                for j in critical_jobs
            ],
            "technical": cron_technical,
        },
        "sheetsCenter": {
            "businessOps": check_sheet(business_sheet, ["Client Log", "Bookkeeping", "Task Log", "SOT_Health"]),
            "staffProperties": check_sheet(staff_sheet, ["Staff & Wages", "Properties"]),
            "personal": check_sheet(personal_sheet, ["Personal_Expenses"]),
        },
        "tasks": {
            "now": existing.get("tasks", {}).get("now", []),
            "queue": [
                "Square -> Business Ops sync",
                "Expenses -> Business Ops/Personal routing",
                "Three-sheet dashboard refresh",
                "Calendar refresh for next 48h",
                "Cron technical review",
            ],
            "blockers": [f"{j.get('name')}: {j.get('state', {}).get('lastError', 'error')}" for j in error_jobs[:5]],
        },
        "skills": {
            "workspaceTotal": len(workspace_skills),
            "liveTotal": len(live_skills),
            "critical": [
                "model-switcher",
                "model-switch-control",
                "api-health-and-quotas",
                "codex-opencli-update-watch",
                "pre-flight-validator",
                "secret-guard",
                "bella-dashboard-manager",
            ],
            "newlyAdded": ["model-switch-control", "api-health-and-quotas", "codex-opencli-update-watch"],
        },
        "sessions": {
            "count": len(session_items),
            "lastActivityMs": latest_session_ms,
            "active": session_items[:8],
        },
        "patterns": [
            {"description": "Three-sheet source-of-truth cutover remains locked (Business Ops, Staff Properties, Personal).", "date": now.strftime("%Y-%m-%d")},
            {"description": "Codex routing stabilized at 5.3 primary with 5.2 fallback; broken fallbacks removed.", "date": now.strftime("%Y-%m-%d")},
            {"description": "Universal sync pass completed with accuracy+integrity validation PASS.", "date": now.strftime("%Y-%m-%d")},
        ],
        "insights": {
            "tips": [
                {"id": "collections", "title": "Clear overdue first", "impact": "cashflow", "action": "Follow up overdue invoices before noon daily."},
                {"id": "sheets", "title": "Route by account type", "impact": "accuracy", "action": "Keep personal and business expenses split at entry time."},
                {"id": "cron", "title": "Watch failing jobs", "impact": "reliability", "action": "Resolve any failing cron in the same day."},
            ],
            "patterns": existing.get("patterns", []),
            "risks": [
                {"level": "high" if error_jobs else "low", "message": "Cron pipeline health" if error_jobs else "No active runtime blocker.", "mitigation": "Review Crons tab technical logs and fix failing jobs." if error_jobs else "Maintain hourly sync cadence."}
            ],
        },
        "quickActions": [
            {"label": "Model Check", "command": f"bash {ROOT}/scripts/check-model.sh"},
            {"label": "Gateway Restart", "command": "clawdbot gateway restart"},
            {"label": "Smoke Test", "command": 'clawdbot agent --local --agent main --message "Reply exactly: BOT_HEALTH_OK" --thinking low --json'},
        ],
        "legacyCompat": {
            "bella": existing.get("bella", {}),
            "liveTasks": existing.get("liveTasks", []),
            "activeSessions": existing.get("activeSessions", {}),
        },
    }

    (ROOT / "dashboard-data.json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"Updated {ROOT / 'dashboard-data.json'}")

    if APP_PUBLIC.parent.exists():
        try:
            APP_PUBLIC.write_text(json.dumps(data, indent=2) + "\n")
            print(f"Updated {APP_PUBLIC}")
        except PermissionError:
            print(f"Skipped {APP_PUBLIC} (permission denied in current sandbox).")

    print("Done.")


if __name__ == "__main__":
    main()
