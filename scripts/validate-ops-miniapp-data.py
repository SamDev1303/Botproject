#!/usr/bin/env python3
import json
import sys
from pathlib import Path

P = Path('/Users/hafsahnuzhat/Desktop/🦀/dashboard-data.json')


def fail(msg: str):
    print(f'VALIDATION_FAIL: {msg}')
    sys.exit(1)


try:
    data = json.loads(P.read_text())
except Exception as e:
    fail(f'cannot read json: {e}')

for key in ['schemaVersion', 'updatedAt', 'status', 'tasks', 'crons', 'finance', 'calendar', 'health']:
    if key not in data:
        fail(f'missing key: {key}')

if data['schemaVersion'] != 'ops-miniapp.v2':
    fail('unexpected schemaVersion')

status = data['status']
for k in ['state', 'lastHeartbeat', 'lastSync', 'sourceCheckAt', 'freshness', 'note']:
    if k not in status:
        fail(f'missing status.{k}')

if status['state'] not in ['online', 'degraded', 'offline']:
    fail('invalid status.state')

summary = data['tasks'].get('summary', {})
for k in ['doing', 'done', 'high']:
    if k not in summary:
        fail(f'missing tasks.summary.{k}')

cron_summary = data['crons'].get('summary', {})
for k in ['total', 'enabled', 'healthy', 'failing']:
    if k not in cron_summary:
        fail(f'missing crons.summary.{k}')

for k in ['incomeMTD', 'pendingPayments', 'pendingTotal', 'recentPayments']:
    if k not in data['finance']:
        fail(f'missing finance.{k}')

if 'today' not in data['calendar']:
    fail('missing calendar.today')

for k in ['fullCheckOk', 'apiChecks', 'keyChecks', 'checkedAt']:
    if k not in data['health']:
        fail(f'missing health.{k}')

print('VALIDATION_OK')
