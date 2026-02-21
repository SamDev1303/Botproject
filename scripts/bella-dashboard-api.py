#!/usr/bin/env python3
"""
Bella Live Dashboard — Local API server
Serves live bot data at http://localhost:18800
Pulls directly from local clawdbot config/state files
"""

import json
import time
import subprocess
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

CLAW_HOME = Path.home() / ".clawdbot"
CONFIG_FILE = CLAW_HOME / "clawdbot.json"
AUTH_FILE = CLAW_HOME / "agents" / "main" / "agent" / "auth-profiles.json"
SESSIONS_FILE = CLAW_HOME / "agents" / "main" / "sessions" / "sessions.json"
LOG_DIR = CLAW_HOME / "logs"
WORKSPACE = Path.home() / "Desktop" / "🦀"
PORT = 18800


def get_model_config():
    try:
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        model = data.get("agents", {}).get("defaults", {}).get("model", {})
        return {
            "primary": model.get("primary", "unknown"),
            "fallbacks": model.get("fallbacks", []),
        }
    except Exception as e:
        return {"primary": "error", "fallbacks": [], "error": str(e)}


def get_token_health():
    try:
        with open(AUTH_FILE) as f:
            data = json.load(f)
        now = int(time.time() * 1000)
        tokens = []
        for name, prof in data.get("profiles", {}).items():
            ptype = prof.get("type", "unknown")
            expires = prof.get("expires", 0)
            if ptype == "api_key":
                tokens.append({"name": name, "type": ptype, "status": "ok", "label": "API Key (never expires)"})
            elif expires:
                remaining_h = (expires - now) // 3600000
                if expires < now:
                    tokens.append({"name": name, "type": "oauth", "status": "expired", "label": f"EXPIRED {abs(remaining_h)}h ago"})
                elif remaining_h < 24:
                    tokens.append({"name": name, "type": "oauth", "status": "warning", "label": f"Expiring in {remaining_h}h"})
                else:
                    tokens.append({"name": name, "type": "oauth", "status": "ok", "label": f"{remaining_h // 24}d {remaining_h % 24}h remaining"})
            else:
                tokens.append({"name": name, "type": ptype, "status": "ok", "label": "No expiry"})

        # Check cooldowns
        cooldowns = []
        for key, entry in data.get("usageStats", {}).items():
            if not isinstance(entry, dict):
                continue
            cd = int(entry.get("cooldownUntil") or 0)
            errors = int(entry.get("errorCount") or 0)
            if cd > now:
                cooldowns.append({"provider": key, "remaining_min": (cd - now) // 60000, "errors": errors})
            elif errors > 0:
                cooldowns.append({"provider": key, "remaining_min": 0, "errors": errors})

        return {"tokens": tokens, "cooldowns": cooldowns}
    except Exception as e:
        return {"tokens": [], "cooldowns": [], "error": str(e)}


def get_sessions():
    try:
        with open(SESSIONS_FILE) as f:
            data = json.load(f)
        now = int(time.time() * 1000)
        sessions = []
        entries = data if isinstance(data, list) else data.get("sessions", data.get("entries", []))
        if isinstance(entries, dict):
            entries = list(entries.values())
        for s in entries[:10]:
            if isinstance(s, dict):
                sid = s.get("sessionId", s.get("id", "?"))
                last = s.get("lastActiveAt", s.get("updatedAt", 0))
                if last:
                    ago = (now - last) // 60000
                    sessions.append({"id": sid[:30], "ago": f"{ago}m ago" if ago < 60 else f"{ago // 60}h ago"})
        return sessions
    except Exception as e:
        return []


def get_gateway_status():
    try:
        result = subprocess.run(
            ["clawdbot", "health"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout
        telegram_ok = "ok" in output.lower() and "telegram" in output.lower()
        return {
            "running": True,
            "telegram": telegram_ok,
            "raw": output[:500]
        }
    except Exception:
        return {"running": False, "telegram": False, "raw": "Gateway unreachable"}


def get_recent_logs():
    logs = []
    for log_name in ["model-switch.log", "auto-failover.log", "token-refresh.log", "model-monitor.log"]:
        log_path = LOG_DIR / log_name
        if log_path.exists():
            try:
                lines = log_path.read_text().strip().split("\n")
                last_lines = lines[-5:] if len(lines) > 5 else lines
                logs.append({"file": log_name, "lines": last_lines})
            except:
                pass
    return logs


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BELLA // Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Instrument+Serif&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #060608;
  --surface: #0c0c10;
  --surface-raised: #111116;
  --border: #1a1a22;
  --border-active: #c8553a;
  --text: #b8b8c4;
  --text-dim: #55556a;
  --text-bright: #e8e8f0;
  --accent: #c8553a;
  --accent-glow: rgba(200, 85, 58, 0.15);
  --green: #3d9970;
  --green-dim: rgba(61, 153, 112, 0.12);
  --amber: #c49035;
  --amber-dim: rgba(196, 144, 53, 0.12);
  --red: #c44040;
  --red-dim: rgba(196, 64, 64, 0.12);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Mono', 'SF Mono', monospace;
  font-size: 13px;
  font-weight: 300;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Noise texture overlay */
body::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
}

.shell {
  max-width: 1280px;
  margin: 0 auto;
  padding: 40px 32px;
}

/* Header — editorial/magazine feel */
header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 32px;
  margin-bottom: 32px;
  border-bottom: 1px solid var(--border);
}

.brand {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.brand h1 {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 42px;
  font-weight: 400;
  color: var(--text-bright);
  letter-spacing: -1px;
  line-height: 1;
}

.brand .tag {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 3px;
  color: var(--accent);
  border: 1px solid var(--accent);
  padding: 3px 10px;
  position: relative;
  top: -4px;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: var(--text-dim);
}

.pulse-ring {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--green);
  position: relative;
}

.pulse-ring::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 1px solid var(--green);
  animation: ring 2.5s ease-out infinite;
}

@keyframes ring {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(2.2); opacity: 0; }
}

/* Grid — asymmetric, intentional */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 16px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-active), transparent);
  opacity: 0;
  transition: opacity 0.4s;
}

.card:hover::before { opacity: 1; }

.card-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 3px;
  color: var(--text-dim);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-label::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 3px;
  background: var(--accent);
}

/* Span configs */
.span-2 { grid-column: span 2; }
.span-3 { grid-column: span 3; }

/* Model display */
.model-stack { display: flex; flex-direction: column; gap: 8px; }

.model-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--surface-raised);
  border-left: 2px solid transparent;
  transition: all 0.2s;
}

.model-row.active {
  border-left-color: var(--green);
  background: var(--green-dim);
}

.model-row.standby {
  border-left-color: var(--border);
}

.model-row .rank {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--text-dim);
  min-width: 70px;
}

.model-row .name {
  font-weight: 500;
  color: var(--text-bright);
  flex: 1;
  margin-left: 12px;
}

.model-row .badge {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 2px;
  padding: 2px 8px;
}

.badge-active { color: var(--green); border: 1px solid var(--green); }
.badge-standby { color: var(--text-dim); }

/* Token rows */
.token-stack { display: flex; flex-direction: column; gap: 6px; }

.token-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--surface-raised);
}

.token-name { color: var(--text); font-size: 12px; }

.token-status {
  font-size: 11px;
  font-weight: 400;
  padding: 2px 8px;
}

.tok-ok { color: var(--green); background: var(--green-dim); }
.tok-warn { color: var(--amber); background: var(--amber-dim); }
.tok-expired { color: var(--red); background: var(--red-dim); }

/* Gateway */
.gw-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.gw-metric {
  padding: 16px;
  background: var(--surface-raised);
  text-align: center;
}

.gw-metric .value {
  font-size: 20px;
  font-weight: 500;
  color: var(--text-bright);
  margin-bottom: 4px;
}

.gw-metric .label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--text-dim);
}

/* Sessions */
.session-list { display: flex; flex-direction: column; gap: 1px; }

.session-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--surface-raised);
  font-size: 11px;
}

.session-row .sid { color: var(--text); font-family: 'DM Mono', monospace; }
.session-row .time { color: var(--text-dim); }

/* Actions */
.action-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.act-btn {
  background: var(--surface-raised);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 10px 18px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.15s;
  text-transform: uppercase;
}

.act-btn:hover {
  border-color: var(--accent);
  color: var(--text-bright);
  background: var(--accent-glow);
}

.act-btn.emergency {
  border-color: var(--green);
  color: var(--green);
}

.act-btn.emergency:hover {
  background: var(--green-dim);
  color: var(--text-bright);
}

.act-btn.warn-btn {
  border-color: var(--amber);
  color: var(--amber);
}

.act-btn.warn-btn:hover {
  background: var(--amber-dim);
}

#action-result {
  margin-top: 16px;
  padding: 12px 16px;
  background: var(--surface-raised);
  font-size: 11px;
  color: var(--text-dim);
  display: none;
  max-height: 200px;
  overflow-y: auto;
}

#action-result.visible { display: block; }
#action-result pre { white-space: pre-wrap; font-family: 'DM Mono', monospace; }

/* Log panel */
.log-group { margin-bottom: 12px; }

.log-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--accent);
  margin-bottom: 6px;
}

.log-lines {
  background: var(--surface-raised);
  padding: 12px 14px;
  font-size: 10px;
  line-height: 1.7;
  color: var(--text-dim);
  overflow-x: auto;
}

.log-lines pre { white-space: pre-wrap; font-family: 'DM Mono', monospace; }

/* Cooldown warning bar */
.cooldown-bar {
  background: var(--red-dim);
  border: 1px solid rgba(196, 64, 64, 0.3);
  padding: 8px 14px;
  margin-top: 10px;
  font-size: 11px;
  color: var(--red);
}

/* Responsive */
@media (max-width: 900px) {
  .grid { grid-template-columns: 1fr; }
  .span-2, .span-3 { grid-column: span 1; }
  header { flex-direction: column; align-items: flex-start; gap: 16px; }
}
</style>
</head>
<body>

<div class="shell">
  <header>
    <div class="brand">
      <h1>Bella</h1>
      <span class="tag">Command Center</span>
    </div>
    <div class="live-indicator">
      <span class="pulse-ring"></span>
      <span id="live-status">Connecting...</span>
    </div>
  </header>

  <div class="grid">
    <!-- Model Config — prominent left column -->
    <div class="card">
      <div class="card-label">Model Routing</div>
      <div id="model-config" class="model-stack">
        <div class="model-row"><span class="rank">loading</span></div>
      </div>
    </div>

    <!-- Token Health -->
    <div class="card">
      <div class="card-label">Token Health</div>
      <div id="token-health" class="token-stack">
        <div class="token-item"><span class="token-name">loading...</span></div>
      </div>
    </div>

    <!-- Gateway -->
    <div class="card">
      <div class="card-label">Gateway</div>
      <div id="gateway-status" class="gw-grid">
        <div class="gw-metric"><div class="value">--</div><div class="label">Status</div></div>
        <div class="gw-metric"><div class="value">--</div><div class="label">Telegram</div></div>
      </div>
    </div>

    <!-- Actions — full width -->
    <div class="card span-2">
      <div class="card-label">Quick Actions</div>
      <div class="action-bar">
        <button class="act-btn" onclick="runAction('switch-sonnet')">Sonnet 4.6</button>
        <button class="act-btn" onclick="runAction('switch-opus')">Opus 4.6</button>
        <button class="act-btn" onclick="runAction('switch-gemini')">Gemini 3</button>
        <button class="act-btn" onclick="runAction('switch-codex')">Codex 5.3</button>
        <button class="act-btn emergency" onclick="runAction('failover')">Auto-Failover</button>
        <button class="act-btn warn-btn" onclick="runAction('token-fix')">Fix Tokens</button>
        <button class="act-btn" onclick="runAction('restart')">Restart</button>
      </div>
      <div id="action-result"></div>
    </div>

    <!-- Sessions -->
    <div class="card">
      <div class="card-label">Recent Sessions</div>
      <div id="sessions" class="session-list">
        <div class="session-row"><span class="sid">loading...</span></div>
      </div>
    </div>

    <!-- Logs — full width bottom -->
    <div class="card span-3">
      <div class="card-label">System Log</div>
      <div id="logs"></div>
    </div>
  </div>
</div>

<script>
async function fetchData() {
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        renderAll(data);
        document.getElementById('live-status').textContent = 'Live \u2014 ' + new Date().toLocaleTimeString();
    } catch (e) {
        document.getElementById('live-status').textContent = 'Disconnected';
    }
}

function shortModel(id) {
    const map = {
        'anthropic/claude-sonnet-4-6': 'Sonnet 4.6',
        'anthropic/claude-opus-4-6': 'Opus 4.6',
        'anthropic/claude-opus-4-5': 'Opus 4.5',
        'google/gemini-3-flash-preview': 'Gemini 3 Flash',
        'openai-codex/gpt-5.3-codex': 'Codex GPT-5.3',
        'openai-codex/gpt-5.2-codex': 'Codex GPT-5.2',
    };
    return map[id] || id;
}

function renderAll(data) {
    const mc = data.model;
    let mh = `<div class="model-row active"><span class="rank">Primary</span><span class="name">${shortModel(mc.primary)}</span><span class="badge badge-active">Active</span></div>`;
    mc.fallbacks.forEach((f, i) => {
        mh += `<div class="model-row standby"><span class="rank">Fallback ${i+1}</span><span class="name">${shortModel(f)}</span><span class="badge badge-standby">Standby</span></div>`;
    });
    document.getElementById('model-config').innerHTML = mh;

    const th = data.tokens;
    let tokenHtml = '';
    th.tokens.forEach(t => {
        const cls = t.status === 'ok' ? 'tok-ok' : t.status === 'warning' ? 'tok-warn' : 'tok-expired';
        tokenHtml += `<div class="token-item"><span class="token-name">${t.name}</span><span class="token-status ${cls}">${t.label}</span></div>`;
    });
    if (th.cooldowns && th.cooldowns.length > 0) {
        th.cooldowns.forEach(c => {
            tokenHtml += `<div class="cooldown-bar">${c.provider}: ${c.remaining_min > 0 ? c.remaining_min + 'm cooldown' : c.errors + ' errors'}</div>`;
        });
    }
    document.getElementById('token-health').innerHTML = tokenHtml;

    const gw = data.gateway;
    const gwColor = gw.running ? 'var(--green)' : 'var(--red)';
    const tgColor = gw.telegram ? 'var(--green)' : 'var(--red)';
    document.getElementById('gateway-status').innerHTML = `
        <div class="gw-metric"><div class="value" style="color:${gwColor}">${gw.running ? 'UP' : 'DOWN'}</div><div class="label">Gateway</div></div>
        <div class="gw-metric"><div class="value" style="color:${tgColor}">${gw.telegram ? 'OK' : 'OFF'}</div><div class="label">Telegram</div></div>
        <div class="gw-metric"><div class="value" style="color:var(--text-bright)">18789</div><div class="label">Port</div></div>
        <div class="gw-metric"><div class="value" style="color:var(--text-bright)">15s</div><div class="label">Refresh</div></div>
    `;

    const ss = data.sessions;
    let sh = '';
    ss.forEach(s => {
        sh += `<div class="session-row"><span class="sid">${s.id}</span><span class="time">${s.ago}</span></div>`;
    });
    document.getElementById('sessions').innerHTML = sh || '<div style="padding:12px;color:var(--text-dim)">No sessions</div>';

    const logs = data.logs;
    let lh = '';
    logs.forEach(l => {
        lh += `<div class="log-group"><div class="log-label">${l.file}</div><div class="log-lines"><pre>${l.lines.join('\n')}</pre></div></div>`;
    });
    document.getElementById('logs').innerHTML = lh || '<div style="color:var(--text-dim)">No logs</div>';
}

async function runAction(action) {
    const el = document.getElementById('action-result');
    el.classList.add('visible');
    el.innerHTML = '<pre>Running...</pre>';
    try {
        const resp = await fetch('/api/action', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({action}) });
        const data = await resp.json();
        el.innerHTML = `<pre>${data.output || data.error || 'Done'}</pre>`;
        setTimeout(fetchData, 2000);
    } catch (e) {
        el.innerHTML = `<pre style="color:var(--red)">Error: ${e.message}</pre>`;
    }
}

fetchData();
setInterval(fetchData, 15000);
</script>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress access logs

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        elif self.path == "/api/status":
            data = {
                "model": get_model_config(),
                "tokens": get_token_health(),
                "gateway": get_gateway_status(),
                "sessions": get_sessions(),
                "logs": get_recent_logs(),
                "timestamp": int(time.time() * 1000),
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/action":
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length)) if content_length else {}
            action = body.get("action", "")

            scripts = {
                "switch-sonnet": "bash ~/Desktop/🦀/scripts/model-switch.sh sonnet",
                "switch-opus": "bash ~/Desktop/🦀/scripts/model-switch.sh opus",
                "switch-gemini": "bash ~/Desktop/🦀/scripts/model-switch.sh gemini",
                "switch-codex": "bash ~/Desktop/🦀/scripts/model-switch.sh codex",
                "failover": "bash ~/Desktop/🦀/scripts/auto-failover.sh",
                "token-fix": "bash ~/Desktop/🦀/scripts/token-refresh.sh fix",
                "restart": "clawdbot gateway restart",
            }

            cmd = scripts.get(action)
            if cmd:
                try:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True, timeout=120,
                        env={**os.environ, "HOME": str(Path.home())}
                    )
                    output = result.stdout + result.stderr
                    response = {"output": output[:2000], "success": result.returncode == 0}
                except subprocess.TimeoutExpired:
                    response = {"output": "Command timed out", "success": False}
                except Exception as e:
                    response = {"error": str(e), "success": False}
            else:
                response = {"error": f"Unknown action: {action}", "success": False}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), DashboardHandler)
    print(f"🦞 Bella Dashboard running at http://localhost:{PORT}")
    print(f"   Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        server.server_close()
