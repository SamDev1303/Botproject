#!/usr/bin/env python3
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path('/Users/hafsahnuzhat/Desktop/🦀')
sys.path.insert(0, str(ROOT / 'scripts'))
from square_api import SquareAPI
from google_sheets_api import get_access_token

TZ = ZoneInfo("Australia/Sydney")
ROOT = Path('/Users/hafsahnuzhat/Desktop/🦀')
CLAW = Path.home() / '.clawdbot'
OUT = ROOT / 'dashboard-data.json'
OUT_PUBLIC = Path('/Users/hafsahnuzhat/bella-dashboard/public/dashboard-data.json')

FRESH_GREEN_MIN = 5
FRESH_AMBER_MIN = 15
OFFLINE_MIN = 60


def load_json(path: Path):
    return json.loads(path.read_text())


def now_local():
    return datetime.now(TZ)


def now_iso():
    return now_local().isoformat(timespec='seconds')


def ms_to_iso(ms: int | None):
    if not ms:
        return ''
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone(TZ).isoformat(timespec='seconds')


def parse_iso(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def mins_ago(ts: datetime | None):
    if not ts:
        return 10_000
    return int((now_local() - ts).total_seconds() // 60)


def adapter_crons():
    check_at = now_iso()
    try:
        jobs = load_json(CLAW / 'cron' / 'jobs.json').get('jobs', [])
        out = []
        healthy = 0
        failing = 0
        for j in jobs:
            st = j.get('state', {}) or {}
            status = str(st.get('lastStatus', '')).lower() or ('scheduled' if j.get('enabled') else 'disabled')
            if status in {'ok', 'success', 'completed', 'scheduled'}:
                healthy += 1
            if status == 'error':
                failing += 1
            out.append({
                'id': j.get('id', ''),
                'name': j.get('name', 'unknown'),
                'enabled': bool(j.get('enabled')),
                'schedule': (j.get('schedule', {}) or {}).get('expr', 'n/a'),
                'lastStatus': status,
                'lastRunAt': ms_to_iso(st.get('lastRunAtMs') or st.get('lastRunAt')),
                'nextRunAt': ms_to_iso(st.get('nextRunAtMs') or st.get('nextRunAt')),
            })
        out.sort(key=lambda x: (0 if x['lastStatus'] == 'error' else 1, x['name']))
        return {'ok': True, 'error': '', 'fetchedAt': check_at, 'data': {'jobs': out, 'summary': {'total': len(out), 'enabled': len([j for j in out if j['enabled']]), 'healthy': healthy, 'failing': failing}, 'sourceCheckAt': check_at}}
    except Exception as e:
        return {'ok': False, 'error': f'cron adapter failed: {e}', 'fetchedAt': check_at, 'data': {'jobs': [], 'summary': {'total': 0, 'enabled': 0, 'healthy': 0, 'failing': 0}, 'sourceCheckAt': check_at}}


def adapter_sessions():
    check_at = now_iso()
    try:
        sessions = load_json(CLAW / 'agents' / 'main' / 'sessions' / 'sessions.json')
        latest_ms = 0
        active = []
        now_ms = int(now_local().timestamp() * 1000)
        for key, s in sessions.items():
            updated = int(s.get('updatedAt', 0) or 0)
            latest_ms = max(latest_ms, updated)
            if now_ms - updated <= 15 * 60 * 1000:
                active.append({'id': f"session:{key}", 'title': f"Active session: {s.get('chatType', 'session')}", 'priority': 'medium', 'updatedAt': ms_to_iso(updated), 'source': 'sessions'})
        return {'ok': True, 'error': '', 'fetchedAt': check_at, 'data': {'lastHeartbeat': ms_to_iso(latest_ms) or check_at, 'doingNow': active[:8]}}
    except Exception as e:
        return {'ok': False, 'error': f'session adapter failed: {e}', 'fetchedAt': check_at, 'data': {'lastHeartbeat': check_at, 'doingNow': []}}


def adapter_square():
    check_at = now_iso()
    try:
        sq = SquareAPI()
        unpaid = sq.list_invoices(status='UNPAID') or []
        unpaid_total = 0.0
        for inv in unpaid:
            req = (inv.get('payment_requests') or [{}])[0]
            unpaid_total += (req.get('computed_amount_money', {}).get('amount', 0) or 0) / 100

        now = now_local()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_utc = month_start.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_utc = now.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')
        pay_result = sq._request(f"/payments?begin_time={start_utc}&end_time={end_utc}")
        payments = pay_result.get('payments', [])
        completed = [p for p in payments if str(p.get('status', '')).upper() == 'COMPLETED']
        income_mtd = round(sum(((p.get('amount_money', {}).get('amount', 0) or 0) / 100) for p in completed), 2)

        recent = []
        for p in sorted(completed, key=lambda x: str(x.get('created_at', '')), reverse=True)[:5]:
            recent.append({
                'date': str(p.get('created_at', ''))[:10],
                'amount': round((p.get('amount_money', {}).get('amount', 0) or 0) / 100, 2),
                'status': p.get('status', 'COMPLETED')
            })

        return {'ok': True, 'error': '', 'fetchedAt': check_at, 'data': {'incomeMTD': income_mtd, 'pendingPayments': len(unpaid), 'pendingTotal': round(unpaid_total, 2), 'recentPayments': recent, 'keyPresent': bool(getattr(sq, 'access_token', ''))}}
    except Exception as e:
        return {'ok': False, 'error': f'square adapter failed: {e}', 'fetchedAt': check_at, 'data': {'incomeMTD': 0.0, 'pendingPayments': 0, 'pendingTotal': 0.0, 'recentPayments': [], 'keyPresent': False}}


def adapter_calendar_today():
    check_at = now_iso()
    try:
        token = get_access_token()
        now = datetime.now(timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        qs = urllib.parse.urlencode({'timeMin': start.isoformat().replace('+00:00', 'Z'), 'timeMax': end.isoformat().replace('+00:00', 'Z'), 'singleEvents': 'true', 'orderBy': 'startTime', 'maxResults': '20'})
        req = urllib.request.Request(f"https://www.googleapis.com/calendar/v3/calendars/primary/events?{qs}", headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode())
        events = []
        for e in data.get('items', [])[:6]:
            s = e.get('start', {}).get('dateTime', e.get('start', {}).get('date', ''))
            events.append({'title': e.get('summary', '(no title)'), 'time': s[11:16] if 'T' in s else 'all day'})
        return {'ok': True, 'error': '', 'fetchedAt': check_at, 'data': {'today': events, 'tokenOk': True}}
    except Exception as e:
        return {'ok': False, 'error': f'calendar adapter failed: {e}', 'fetchedAt': check_at, 'data': {'today': [], 'tokenOk': False}}


def build_tasks(session_adapter, cron_adapter):
    done_today = []
    today = now_local().date()
    for j in cron_adapter['data']['jobs']:
        lr = j.get('lastRunAt')
        if not lr:
            continue
        d = parse_iso(lr)
        if d and d.date() == today and j.get('lastStatus') in {'ok', 'success', 'completed', 'scheduled'}:
            done_today.append({'id': f"cron-done:{j['id']}", 'title': f"Cron healthy: {j['name']}", 'priority': 'low', 'updatedAt': lr, 'source': 'cron'})

    high = []
    for j in cron_adapter['data']['jobs']:
        if j.get('lastStatus') == 'error':
            high.append({'id': f"cron-hi:{j['id']}", 'title': f"Fix cron failure: {j['name']}", 'priority': 'high', 'updatedAt': now_iso(), 'source': 'cron'})

    doing = session_adapter['data']['doingNow']
    return {'doingNow': doing, 'doneToday': done_today[:12], 'highPriority': high[:12], 'summary': {'doing': len(doing), 'done': len(done_today), 'high': len(high)}}


def build_status(session_adapter, cron_adapter, square_adapter, cal_adapter):
    hb = parse_iso(session_adapter['data'].get('lastHeartbeat'))
    hb_age = mins_ago(hb)

    state = 'online'
    notes = []
    adapters = [('session', session_adapter), ('cron', cron_adapter), ('square', square_adapter), ('calendar', cal_adapter)]
    for name, ad in adapters:
        if not ad['ok']:
            state = 'degraded'
            notes.append(f'{name} adapter failed')

    if cron_adapter['data']['summary'].get('failing', 0) > 0:
        state = 'degraded'
        notes.append('cron failures present')

    if hb_age > FRESH_AMBER_MIN and state == 'online':
        state = 'degraded'
        notes.append(f'heartbeat stale ({hb_age}m)')

    if hb_age > OFFLINE_MIN:
        state = 'offline'
        notes.append(f'heartbeat offline threshold exceeded ({hb_age}m)')

    freshness = 'green'
    if hb_age > FRESH_GREEN_MIN:
        freshness = 'amber'
    if hb_age > FRESH_AMBER_MIN:
        freshness = 'red'

    note = '; '.join(notes) if notes else 'All adapters healthy.'
    now = now_iso()
    return {'state': state, 'lastHeartbeat': session_adapter['data'].get('lastHeartbeat', now), 'lastSync': now, 'sourceCheckAt': now, 'freshness': freshness, 'note': note}


def build_insights(square_adapter, cal_adapter):
    out = []
    if square_adapter['data'].get('pendingPayments', 0) > 0:
        out.append(f"{square_adapter['data']['pendingPayments']} pending payments totalling ${square_adapter['data']['pendingTotal']:.2f}")
    else:
        out.append('No pending payments in Square')

    tcount = len(cal_adapter['data'].get('today', []))
    out.append(f"{tcount} calendar items for today")
    return out


def main():
    crons = adapter_crons()
    sessions = adapter_sessions()
    square = adapter_square()
    calendar = adapter_calendar_today()

    status = build_status(sessions, crons, square, calendar)
    tasks = build_tasks(sessions, crons)
    insights = build_insights(square, calendar)

    health = {
        'fullCheckOk': all([sessions['ok'], crons['ok'], square['ok'], calendar['ok']]),
        'apiChecks': {
            'squareApi': square['ok'],
            'googleCalendarApi': calendar['ok'],
            'cronStore': crons['ok'],
            'sessionStore': sessions['ok'],
        },
        'keyChecks': {
            'squareKeyPresent': square['data'].get('keyPresent', False),
            'googleTokenOk': calendar['data'].get('tokenOk', False),
        },
        'checkedAt': now_iso(),
    }

    payload = {
        'schemaVersion': 'ops-miniapp.v2',
        'build': {'phase': 8, 'mode': 'production-hardened'},
        'updatedAt': now_iso(),
        'status': status,
        'tasks': tasks,
        'crons': crons['data'],
        'finance': square['data'],
        'calendar': calendar['data'],
        'insights': insights,
        'health': health,
        'adapters': {
            'sessions': {'ok': sessions['ok'], 'error': sessions['error'], 'fetchedAt': sessions['fetchedAt']},
            'crons': {'ok': crons['ok'], 'error': crons['error'], 'fetchedAt': crons['fetchedAt']},
            'square': {'ok': square['ok'], 'error': square['error'], 'fetchedAt': square['fetchedAt']},
            'calendar': {'ok': calendar['ok'], 'error': calendar['error'], 'fetchedAt': calendar['fetchedAt']},
        },
    }

    OUT.write_text(json.dumps(payload, indent=2))
    OUT_PUBLIC.write_text(json.dumps(payload, indent=2))
    print(f'Updated {OUT}')
    print(f'Updated {OUT_PUBLIC}')


if __name__ == '__main__':
    main()
