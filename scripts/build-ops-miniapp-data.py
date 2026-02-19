#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

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
        return {
            'ok': True,
            'error': '',
            'fetchedAt': check_at,
            'data': {
                'jobs': out,
                'summary': {
                    'total': len(out),
                    'enabled': len([j for j in out if j['enabled']]),
                    'healthy': healthy,
                    'failing': failing,
                },
                'sourceCheckAt': check_at,
            },
        }
    except Exception as e:
        return {
            'ok': False,
            'error': f'cron adapter failed: {e}',
            'fetchedAt': check_at,
            'data': {
                'jobs': [],
                'summary': {'total': 0, 'enabled': 0, 'healthy': 0, 'failing': 0},
                'sourceCheckAt': check_at,
            },
        }


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
                active.append({
                    'id': f"session:{key}",
                    'title': f"Active session: {s.get('chatType', 'session')}",
                    'priority': 'medium',
                    'updatedAt': ms_to_iso(updated),
                    'source': 'sessions',
                })
        return {
            'ok': True,
            'error': '',
            'fetchedAt': check_at,
            'data': {
                'lastHeartbeat': ms_to_iso(latest_ms) or check_at,
                'doingNow': active[:8],
            },
        }
    except Exception as e:
        return {
            'ok': False,
            'error': f'session adapter failed: {e}',
            'fetchedAt': check_at,
            'data': {
                'lastHeartbeat': check_at,
                'doingNow': [],
            },
        }


def build_tasks(session_adapter, cron_adapter):
    done_today = []
    today = now_local().date()
    for j in cron_adapter['data']['jobs']:
        lr = j.get('lastRunAt')
        if not lr:
            continue
        d = parse_iso(lr)
        if d and d.date() == today and j.get('lastStatus') in {'ok', 'success', 'completed', 'scheduled'}:
            done_today.append({
                'id': f"cron-done:{j['id']}",
                'title': f"Cron healthy: {j['name']}",
                'priority': 'low',
                'updatedAt': lr,
                'source': 'cron',
            })

    high = []
    for j in cron_adapter['data']['jobs']:
        if j.get('lastStatus') == 'error':
            high.append({
                'id': f"cron-hi:{j['id']}",
                'title': f"Fix cron failure: {j['name']}",
                'priority': 'high',
                'updatedAt': now_iso(),
                'source': 'cron',
            })

    doing = session_adapter['data']['doingNow']

    return {
        'doingNow': doing,
        'doneToday': done_today[:12],
        'highPriority': high[:12],
        'summary': {'doing': len(doing), 'done': len(done_today), 'high': len(high)},
    }


def build_status(session_adapter, cron_adapter):
    hb = parse_iso(session_adapter['data'].get('lastHeartbeat'))
    hb_age = mins_ago(hb)

    state = 'online'
    notes = []
    if not session_adapter['ok'] or not cron_adapter['ok']:
        state = 'degraded'
        if not session_adapter['ok']:
            notes.append('session adapter failed')
        if not cron_adapter['ok']:
            notes.append('cron adapter failed')

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
    return {
        'state': state,
        'lastHeartbeat': session_adapter['data'].get('lastHeartbeat', now),
        'lastSync': now,
        'sourceCheckAt': now,
        'freshness': freshness,
        'note': note,
    }


def main():
    crons = adapter_crons()
    sessions = adapter_sessions()

    status = build_status(sessions, crons)
    tasks = build_tasks(sessions, crons)

    payload = {
        'schemaVersion': 'ops-miniapp.v1',
        'build': {'phase': 7, 'mode': 'production-hardened'},
        'updatedAt': now_iso(),
        'status': status,
        'tasks': tasks,
        'crons': crons['data'],
        'adapters': {
            'sessions': {'ok': sessions['ok'], 'error': sessions['error'], 'fetchedAt': sessions['fetchedAt']},
            'crons': {'ok': crons['ok'], 'error': crons['error'], 'fetchedAt': crons['fetchedAt']},
        },
    }

    OUT.write_text(json.dumps(payload, indent=2))
    OUT_PUBLIC.write_text(json.dumps(payload, indent=2))
    print(f'Updated {OUT}')
    print(f'Updated {OUT_PUBLIC}')


if __name__ == '__main__':
    main()
