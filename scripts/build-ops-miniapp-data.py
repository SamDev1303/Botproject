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


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def ms_to_iso(ms: int | None):
    if not ms:
        return ''
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone(TZ).isoformat(timespec='seconds')


def now_iso():
    return datetime.now(TZ).isoformat(timespec='seconds')


def build_crons(now: datetime):
    jobs = load_json(CLAW / 'cron' / 'jobs.json', {}).get('jobs', [])
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
        'jobs': out,
        'summary': {
            'total': len(out),
            'enabled': len([j for j in out if j['enabled']]),
            'healthy': healthy,
            'failing': failing,
        },
        'sourceCheckAt': now.isoformat(timespec='seconds'),
    }


def build_status(now: datetime, crons: dict):
    sessions = load_json(CLAW / 'agents' / 'main' / 'sessions' / 'sessions.json', {})
    latest_ms = 0
    for _, s in sessions.items():
        latest_ms = max(latest_ms, int(s.get('updatedAt', 0) or 0))

    state = 'online'
    note = 'All adapters healthy.'
    if crons['summary']['failing'] > 0:
        state = 'degraded'
        note = 'One or more cron jobs failing.'

    return {
        'state': state,
        'lastHeartbeat': ms_to_iso(latest_ms) or now.isoformat(timespec='seconds'),
        'lastSync': now.isoformat(timespec='seconds'),
        'sourceCheckAt': now.isoformat(timespec='seconds'),
        'note': note,
    }


def build_tasks(now: datetime, crons: dict):
    sessions = load_json(CLAW / 'agents' / 'main' / 'sessions' / 'sessions.json', {})
    now_ms = int(now.timestamp() * 1000)

    doing = []
    for key, s in sessions.items():
        updated = int(s.get('updatedAt', 0) or 0)
        if now_ms - updated <= 15 * 60 * 1000:
            doing.append({
                'id': f"session:{key}",
                'title': f"Active session: {s.get('chatType', 'session')}",
                'priority': 'medium',
                'updatedAt': ms_to_iso(updated),
                'source': 'sessions',
            })
    doing = doing[:8]

    done_today = []
    today = now.date()
    for j in crons['jobs']:
        lr = j.get('lastRunAt')
        if lr:
            try:
                d = datetime.fromisoformat(lr).date()
                if d == today and j.get('lastStatus') in {'ok', 'success', 'completed', 'scheduled'}:
                    done_today.append({
                        'id': f"cron-done:{j['id']}",
                        'title': f"Cron healthy: {j['name']}",
                        'priority': 'low',
                        'updatedAt': lr,
                        'source': 'cron',
                    })
            except Exception:
                pass

    high = []
    for j in crons['jobs']:
        if j.get('lastStatus') == 'error':
            high.append({
                'id': f"cron-hi:{j['id']}",
                'title': f"Fix cron failure: {j['name']}",
                'priority': 'high',
                'updatedAt': now.isoformat(timespec='seconds'),
                'source': 'cron',
            })

    return {
        'doingNow': doing,
        'doneToday': done_today[:12],
        'highPriority': high[:12],
        'summary': {
            'doing': len(doing),
            'done': len(done_today),
            'high': len(high),
        },
    }


def main():
    now = datetime.now(TZ)
    crons = build_crons(now)
    status = build_status(now, crons)
    tasks = build_tasks(now, crons)

    data = {
        'updatedAt': now.isoformat(timespec='seconds'),
        'status': status,
        'tasks': tasks,
        'crons': crons,
    }

    OUT.write_text(json.dumps(data, indent=2))
    OUT_PUBLIC.write_text(json.dumps(data, indent=2))
    print(f'Updated {OUT}')
    print(f'Updated {OUT_PUBLIC}')


if __name__ == '__main__':
    main()
