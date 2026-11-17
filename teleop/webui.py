"""Web UI bridge for the teleoperation system.

Connects to a running robot server and serves a browser dashboard.

Usage::

    # 1. Start the robot server (separate terminal):
    python -m teleop.server --backend mock --transport tcp --port 9000

    # 2. Start the web UI:
    python -m teleop.webui --robot-port 9000

    # 3. Browser opens automatically at http://localhost:8080
"""

from __future__ import annotations

import argparse
import json
import queue
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import List

from .client import OperatorClient
from .protocol import ProtocolError
from .transport import make_client

# ---------------------------------------------------------------------------
# HTML dashboard (embedded so the module is self-contained)
# ---------------------------------------------------------------------------
_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>P3-DX Teleoperation</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f1117;--bg2:#161b22;--bg3:#1c2130;--border:#2d3447;
  --primary:#58a6ff;--success:#3fb950;--warn:#d29922;--danger:#f85149;
  --text:#e6edf3;--muted:#8b949e;--radius:7px;
}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  background:var(--bg);color:var(--text);height:100vh;
  display:grid;grid-template-rows:48px 1fr 160px;
  grid-template-areas:"hdr""main""log";overflow:hidden;font-size:13px;
}

/* ---- Header ---- */
header{
  grid-area:hdr;display:flex;align-items:center;gap:10px;
  padding:0 16px;background:var(--bg2);border-bottom:1px solid var(--border);
}
.dot{width:9px;height:9px;border-radius:50%;background:var(--danger);flex-shrink:0;transition:background .3s}
.dot.on{background:var(--success)}
header h1{font-size:14px;font-weight:600;flex:1;letter-spacing:.01em}
.badge{
  padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700;
  background:var(--bg3);border:1px solid var(--border);letter-spacing:.05em;
  transition:all .2s;
}
.badge.MOVING,.badge.GOTO{color:var(--primary);border-color:var(--primary)}
.badge.TURNING{color:var(--warn);border-color:var(--warn)}
.badge.STOPPED{color:var(--danger);border-color:var(--danger)}
.badge.IDLE{color:var(--muted)}
#hz,#rtt{font-size:11px;color:var(--muted);min-width:60px;text-align:right}

/* ---- Main ---- */
main{grid-area:main;display:grid;grid-template-columns:1fr 310px;overflow:hidden}

/* ---- Map ---- */
.map-wrap{position:relative;overflow:hidden;background:#090c14}
#map{width:100%;height:100%;display:block;cursor:crosshair}
#map.dragging{cursor:grabbing}
.map-btns{
  position:absolute;bottom:12px;right:12px;display:flex;flex-direction:column;gap:5px;
}
.map-btn{
  width:30px;height:30px;background:rgba(22,27,34,.92);
  border:1px solid var(--border);border-radius:6px;
  color:var(--text);font-size:16px;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:background .15s;user-select:none;
}
.map-btn:hover{background:var(--bg3)}
.kbd-hint{
  position:absolute;bottom:12px;left:12px;
  font-size:10px;color:rgba(139,148,158,.5);pointer-events:none;
}
.map-coords{
  position:absolute;top:8px;left:8px;
  font-size:11px;color:rgba(139,148,158,.7);pointer-events:none;
  font-variant-numeric:tabular-nums;
}

/* ---- Sidebar ---- */
.sidebar{border-left:1px solid var(--border);overflow-y:auto;display:flex;flex-direction:column;gap:1px;background:var(--border)}
.panel{background:var(--bg2);padding:12px 14px}
.panel-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:10px}

/* ---- Telemetry ---- */
.tgrid{display:grid;grid-template-columns:1fr 1fr;gap:8px 12px}
.titem{display:flex;flex-direction:column;gap:1px}
.tlabel{font-size:10px;color:var(--muted)}
.tval{font-size:17px;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:-.02em;line-height:1.1}
.tunit{font-size:10px;color:var(--muted);font-weight:400}
.obs-bar{height:4px;background:var(--bg3);border-radius:2px;overflow:hidden;margin-top:8px}
.obs-fill{height:100%;border-radius:2px;background:var(--success);transition:width .15s,background .3s}

/* ---- Controls ---- */
.cs{margin-bottom:11px}
.cs:last-child{margin-bottom:0}
.clabel{font-size:10px;color:var(--muted);margin-bottom:5px}
.crow{display:flex;gap:5px;align-items:center}
input[type=number]{
  width:65px;background:var(--bg3);border:1px solid var(--border);
  border-radius:6px;color:var(--text);padding:5px 7px;
  font-size:12px;font-variant-numeric:tabular-nums;
}
input[type=number]:focus{outline:none;border-color:var(--primary)}
input[type=number]:hover{border-color:#3d4559}
button{
  border:none;border-radius:6px;cursor:pointer;font-size:12px;
  font-weight:600;padding:5px 11px;transition:opacity .1s,transform .08s;
  white-space:nowrap;
}
button:hover{opacity:.85}
button:active{opacity:.7;transform:scale(.97)}
.bp{background:var(--primary);color:#fff}
.bd{background:var(--danger);color:#fff}
.bm{background:var(--bg3);color:var(--text);border:1px solid var(--border)}
.bw{background:var(--warn);color:#000}
.btn-row{display:grid;grid-template-columns:1fr 1fr;gap:5px}
.btn-stop{grid-column:span 2;padding:9px;font-size:14px;letter-spacing:.06em}

/* ---- Log ---- */
.log-panel{
  grid-area:log;background:var(--bg2);border-top:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;
}
.log-hdr{
  padding:5px 14px;font-size:10px;font-weight:700;text-transform:uppercase;
  letter-spacing:.1em;color:var(--muted);border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;flex-shrink:0;
}
.log-hdr button{font-size:10px;padding:2px 7px}
.log-entries{flex:1;overflow-y:auto;padding:2px 0}
.le{
  padding:2px 14px;font-size:11px;font-family:'SF Mono','Fira Code','Cascadia Code',monospace;
  display:flex;align-items:baseline;gap:8px;border-bottom:1px solid rgba(45,52,71,.3);
}
.le:last-child{border-bottom:none}
.lt{color:var(--muted);flex-shrink:0;font-size:10px}
.lc{color:var(--primary);flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lr{flex-shrink:0}
.lr.ok{color:var(--success)}
.lr.bad{color:var(--danger)}
.lr.mid{color:var(--warn)}
.lr.info{color:var(--muted)}
</style>
</head>
<body>

<header>
  <div class="dot" id="dot"></div>
  <h1>Pioneer P3-DX &nbsp;Teleoperation</h1>
  <span class="badge IDLE" id="state-badge">IDLE</span>
  <span id="hz">— Hz</span>
  <span id="rtt"></span>
</header>

<main>
  <div class="map-wrap">
    <canvas id="map"></canvas>
    <div class="map-coords" id="coords">x 0.00  y 0.00</div>
    <div class="map-btns">
      <div class="map-btn" id="zin" title="Zoom in">+</div>
      <div class="map-btn" id="zout" title="Zoom out">−</div>
      <div class="map-btn" id="ctr" title="Centre on robot" style="font-size:13px">⊙</div>
    </div>
    <div class="kbd-hint">WASD / arrows = drive &nbsp;·&nbsp; Space = stop &nbsp;·&nbsp; dbl-click = goto</div>
  </div>

  <div class="sidebar">
    <!-- Telemetry -->
    <div class="panel">
      <div class="panel-title">Telemetry</div>
      <div class="tgrid">
        <div class="titem">
          <span class="tlabel">X</span>
          <span class="tval" id="tx">0.00<span class="tunit"> m</span></span>
        </div>
        <div class="titem">
          <span class="tlabel">Y</span>
          <span class="tval" id="ty">0.00<span class="tunit"> m</span></span>
        </div>
        <div class="titem">
          <span class="tlabel">Heading θ</span>
          <span class="tval" id="tth">0.0<span class="tunit"> °</span></span>
        </div>
        <div class="titem">
          <span class="tlabel">Obstacle</span>
          <span class="tval" id="tobs">—<span class="tunit"> m</span></span>
        </div>
        <div class="titem">
          <span class="tlabel">Linear v</span>
          <span class="tval" id="tv">0.00<span class="tunit"> m/s</span></span>
        </div>
        <div class="titem">
          <span class="tlabel">Angular ω</span>
          <span class="tval" id="tw">0.0<span class="tunit"> °/s</span></span>
        </div>
      </div>
      <div class="obs-bar"><div class="obs-fill" id="obsf" style="width:100%"></div></div>
    </div>

    <!-- Commands -->
    <div class="panel">
      <div class="panel-title">Commands</div>

      <div class="cs">
        <div class="clabel">Move straight &nbsp;<span style="color:var(--muted);font-size:10px">(dist m, speed m/s)</span></div>
        <div class="crow">
          <input type="number" id="mv-d" value="1.0" step="0.5" title="Distance (m)">
          <input type="number" id="mv-s" value="0.3" step="0.1" min="0.05" max="1.0" title="Speed (m/s)">
          <button class="bp" onclick="sendMove()">Move</button>
        </div>
      </div>

      <div class="cs">
        <div class="clabel">Turn in place &nbsp;<span style="color:var(--muted);font-size:10px">(deg, deg/s)</span></div>
        <div class="crow">
          <input type="number" id="tu-d" value="90" step="45" title="Degrees (+ = left)">
          <input type="number" id="tu-r" value="60" step="30" min="10" max="180" title="Rate (°/s)">
          <button class="bp" onclick="sendTurn()">Turn</button>
        </div>
      </div>

      <div class="cs">
        <div class="clabel">Go to point &nbsp;<span style="color:var(--muted);font-size:10px">(x m, y m) or dbl-click map</span></div>
        <div class="crow">
          <input type="number" id="gt-x" value="0.0" step="0.5" title="X (m)">
          <input type="number" id="gt-y" value="0.0" step="0.5" title="Y (m)">
          <button class="bp" onclick="sendGoto()">Goto</button>
        </div>
      </div>

      <div class="cs">
        <div class="clabel">Raw velocity &nbsp;<span style="color:var(--muted);font-size:10px">(m/s, °/s)</span></div>
        <div class="crow">
          <input type="number" id="vl-v" value="0.2" step="0.05" min="-1" max="1" title="Linear (m/s)">
          <input type="number" id="vl-w" value="0" step="10" min="-180" max="180" title="Angular (°/s)">
          <button class="bw" onclick="sendVel()">Set vel</button>
        </div>
      </div>

      <div class="btn-row">
        <button class="bd btn-stop" onclick="cmd('stop')">■ STOP</button>
        <button class="bm" onclick="cmd('ping')">Ping</button>
        <button class="bm" onclick="cmd('status')">Status</button>
        <button class="bm" onclick="cmd('reset')">Reset</button>
      </div>
    </div>
  </div>
</main>

<div class="log-panel">
  <div class="log-hdr">
    <span>Command Log</span>
    <button class="bm" onclick="clearLog()">Clear</button>
  </div>
  <div class="log-entries" id="log"></div>
</div>

<script>
// ── State ─────────────────────────────────────────────────────────────────
const S = {
  pose: [0, 0, 0],   // [x_m, y_m, theta_deg]
  v: 0, w: 0,
  state: 'IDLE', obs: 1.0,
  connected: false,
  trail: [], goal: null,
  scale: 80, panX: 0, panY: 0,
  trackRobot: true,
  tcnt: 0, tt: performance.now(),
  pending: {},       // seq -> {cmd, t0}
};

// ── SSE ───────────────────────────────────────────────────────────────────
function connectSSE() {
  const es = new EventSource('/stream');
  es.onopen  = () => { S.connected = true;  updateHdr(); log('system', 'connected', 'info'); };
  es.onerror = () => { S.connected = false; updateHdr(); };
  es.onmessage = e => {
    const m = JSON.parse(e.data);
    if      (m.type === 'telem')  onTelem(m);
    else if (m.type === 'result') onResult(m);
    else if (m.type === 'ack')    onAck(m);
    else if (m.type === 'pong')   onPong(m);
  };
}

function onTelem(m) {
  const [x, y, th] = m.pose;
  S.pose = [x, y, th * 180 / Math.PI];
  S.v = m.v; S.w = m.w * 180 / Math.PI;
  S.state = m.state; S.obs = m.obstacle ?? 1.0;
  S.trail.push([x, y]);
  if (S.trail.length > 600) S.trail.shift();

  S.tcnt++;
  const now = performance.now();
  if (now - S.tt >= 1000) {
    document.getElementById('hz').textContent =
      (S.tcnt * 1000 / (now - S.tt)).toFixed(1) + ' Hz';
    S.tcnt = 0; S.tt = now;
  }
  updateTelem(); drawMap();
}

function onResult(m) {
  const p = S.pending[m.seq];
  const elapsed = p ? ((performance.now() - p.t0) / 1000).toFixed(2) + 's' : '';
  log(p ? p.cmd : '?', m.outcome, m.outcome === 'reached' ? 'ok' : 'bad', elapsed);
  if (p) {
    if (p.cmd.startsWith('goto')) S.goal = null;
    delete S.pending[m.seq];
  }
}

function onAck(m) {
  const p = S.pending[m.seq];
  if (p && m.ok === false) log(p.cmd, 'rejected', 'bad');
}

function onPong(m) {
  const p = S.pending[m.seq];
  if (p) {
    const ms = (performance.now() - p.t0).toFixed(1);
    document.getElementById('rtt').textContent = 'RTT ' + ms + ' ms';
    log('ping', 'pong ' + ms + ' ms', 'info');
    delete S.pending[m.seq];
  }
}

// ── Commands ──────────────────────────────────────────────────────────────
async function cmd(line) {
  const t0 = performance.now();
  try {
    const r = await fetch('/command', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({cmd: line})
    });
    const d = await r.json();
    if (d.ok) {
      S.pending[d.seq] = {cmd: line, t0};
      log(line, 'ack', 'mid');
    } else {
      log(line, d.error || 'nack', 'bad');
    }
  } catch (err) {
    log(line, String(err), 'bad');
  }
}

function sendMove() {
  const d = +document.getElementById('mv-d').value;
  const s = +document.getElementById('mv-s').value;
  cmd('move ' + d + ' ' + s);
}
function sendTurn() {
  const d = +document.getElementById('tu-d').value;
  const r = +document.getElementById('tu-r').value;
  cmd('turn ' + d + ' ' + r);
}
function sendGoto() {
  const x = +document.getElementById('gt-x').value;
  const y = +document.getElementById('gt-y').value;
  S.goal = [x, y];
  cmd('goto ' + x + ' ' + y);
}
function sendVel() {
  const v = +document.getElementById('vl-v').value;
  const w = +document.getElementById('vl-w').value;
  cmd('vel ' + v + ' ' + w);
}

// ── UI updates ────────────────────────────────────────────────────────────
function updateHdr() {
  document.getElementById('dot').className = 'dot' + (S.connected ? ' on' : '');
}

function updateTelem() {
  const [x, y, th] = S.pose;
  document.getElementById('tx').innerHTML   = x.toFixed(2)  + '<span class="tunit"> m</span>';
  document.getElementById('ty').innerHTML   = y.toFixed(2)  + '<span class="tunit"> m</span>';
  document.getElementById('tth').innerHTML  = th.toFixed(1) + '<span class="tunit"> °</span>';
  document.getElementById('tv').innerHTML   = S.v.toFixed(2)+ '<span class="tunit"> m/s</span>';
  document.getElementById('tw').innerHTML   = S.w.toFixed(1)+ '<span class="tunit"> °/s</span>';
  document.getElementById('tobs').innerHTML = S.obs.toFixed(2)+'<span class="tunit"> m</span>';

  const pct = Math.min(100, S.obs * 100);
  const f = document.getElementById('obsf');
  f.style.width = pct + '%';
  f.style.background = S.obs < 0.3 ? 'var(--danger)' : S.obs < 0.6 ? 'var(--warn)' : 'var(--success)';

  const b = document.getElementById('state-badge');
  b.className = 'badge ' + S.state;
  b.textContent = S.state;
}

// ── Log ───────────────────────────────────────────────────────────────────
function log(c, r, cls, detail) {
  const el = document.getElementById('log');
  const e = document.createElement('div');
  e.className = 'le';
  const now = new Date().toLocaleTimeString('en', {hour12: false, timeStyle: 'medium'});
  e.innerHTML =
    '<span class="lt">' + now + '</span>' +
    '<span class="lc">' + esc(c) + '</span>' +
    '<span class="lr ' + (cls||'info') + '">' + esc(r) + (detail ? ' · ' + esc(detail) : '') + '</span>';
  el.appendChild(e);
  while (el.children.length > 60) el.firstChild.remove();
  el.scrollTop = el.scrollHeight;
}

function clearLog() { document.getElementById('log').innerHTML = ''; }
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// ── Canvas ────────────────────────────────────────────────────────────────
const cv = document.getElementById('map');
const cx = cv.getContext('2d');

function resize() {
  const r = cv.parentElement.getBoundingClientRect();
  cv.width = r.width; cv.height = r.height;
  drawMap();
}

function w2c(wx, wy) {
  const ox = cv.width/2  + S.panX;
  const oy = cv.height/2 + S.panY;
  return [ox + wx * S.scale, oy - wy * S.scale];
}

function drawMap() {
  if (!cv.width) return;
  const W = cv.width, H = cv.height;

  if (S.trackRobot) {
    S.panX = -S.pose[0] * S.scale;
    S.panY =  S.pose[1] * S.scale;
  }
  const ox = W/2 + S.panX;
  const oy = H/2 + S.panY;

  // Background
  cx.fillStyle = '#090c14';
  cx.fillRect(0, 0, W, H);

  // Minor grid (1 m)
  const ms = S.scale;
  cx.strokeStyle = 'rgba(255,255,255,0.038)';
  cx.lineWidth = 1;
  cx.beginPath();
  for (let x = ((ox%ms)+ms)%ms; x < W; x += ms) { cx.moveTo(x,0); cx.lineTo(x,H); }
  for (let y = ((oy%ms)+ms)%ms; y < H; y += ms) { cx.moveTo(0,y); cx.lineTo(W,y); }
  cx.stroke();

  // Major grid (5 m)
  const Ms = ms * 5;
  cx.strokeStyle = 'rgba(255,255,255,0.09)';
  cx.beginPath();
  for (let x = ((ox%Ms)+Ms)%Ms; x < W; x += Ms) { cx.moveTo(x,0); cx.lineTo(x,H); }
  for (let y = ((oy%Ms)+Ms)%Ms; y < H; y += Ms) { cx.moveTo(0,y); cx.lineTo(W,y); }
  cx.stroke();

  // Axes
  cx.strokeStyle = 'rgba(255,255,255,0.18)';
  cx.lineWidth = 1;
  cx.beginPath();
  if (ox>0&&ox<W) { cx.moveTo(ox,0); cx.lineTo(ox,H); }
  if (oy>0&&oy<H) { cx.moveTo(0,oy); cx.lineTo(W,oy); }
  cx.stroke();

  // Metre labels on axes
  cx.fillStyle = 'rgba(139,148,158,0.55)';
  cx.font = '10px sans-serif';
  cx.textAlign = 'center';
  for (let m = -50; m <= 50; m++) {
    if (!m) continue;
    const px = ox + m * ms, py = oy - m * ms;
    if (px > 14 && px < W-14 && oy+14 < H) cx.fillText(m, px, oy+14);
    if (py > 14 && py < H-14 && ox-18 > 0)  cx.fillText(m, ox-18, py+4);
  }

  // Trail
  if (S.trail.length > 1) {
    cx.beginPath();
    const [tx0,ty0] = w2c(...S.trail[0]);
    cx.moveTo(tx0, ty0);
    for (let i=1; i<S.trail.length; i++) {
      const [tx,ty] = w2c(...S.trail[i]);
      cx.lineTo(tx,ty);
    }
    cx.strokeStyle = 'rgba(88,166,255,0.3)';
    cx.lineWidth = 2;
    cx.stroke();
  }

  // Goal marker
  if (S.goal) {
    const [gx,gy] = w2c(...S.goal);
    cx.strokeStyle = '#d29922';
    cx.lineWidth = 2;
    cx.beginPath();
    cx.arc(gx, gy, 9, 0, Math.PI*2);
    cx.stroke();
    cx.beginPath();
    cx.moveTo(gx-14,gy); cx.lineTo(gx+14,gy);
    cx.moveTo(gx,gy-14); cx.lineTo(gx,gy+14);
    cx.stroke();
  }

  // Origin crosshair
  cx.strokeStyle = 'rgba(255,255,255,0.22)';
  cx.lineWidth = 1;
  cx.beginPath();
  cx.moveTo(ox-10,oy); cx.lineTo(ox+10,oy);
  cx.moveTo(ox,oy-10); cx.lineTo(ox,oy+10);
  cx.stroke();

  // Robot
  drawRobot();

  // Scale bar
  const bm = ms>=80 ? 1 : ms>=30 ? 2 : 5;
  const bp = bm * ms;
  const bx = 20, by = H - 20;
  cx.strokeStyle = 'rgba(255,255,255,0.4)';
  cx.lineWidth = 1.5;
  cx.beginPath();
  cx.moveTo(bx,by); cx.lineTo(bx+bp,by);
  cx.moveTo(bx,by-5); cx.lineTo(bx,by+5);
  cx.moveTo(bx+bp,by-5); cx.lineTo(bx+bp,by+5);
  cx.stroke();
  cx.fillStyle = 'rgba(255,255,255,0.45)';
  cx.font = '10px sans-serif';
  cx.textAlign = 'center';
  cx.fillText(bm+'m', bx+bp/2, by-8);
}

function drawRobot() {
  const [rx, ry] = w2c(S.pose[0], S.pose[1]);
  const thR = S.pose[2] * Math.PI / 180;
  const r = Math.max(9, S.scale * 0.22);  // ~0.44m body

  // Glow
  const g = cx.createRadialGradient(rx, ry, 0, rx, ry, r*2.2);
  g.addColorStop(0, 'rgba(88,166,255,0.18)');
  g.addColorStop(1, 'rgba(88,166,255,0)');
  cx.beginPath(); cx.arc(rx, ry, r*2.2, 0, Math.PI*2);
  cx.fillStyle = g; cx.fill();

  // Body
  cx.beginPath(); cx.arc(rx, ry, r, 0, Math.PI*2);
  cx.fillStyle = '#1a2d47'; cx.fill();
  cx.strokeStyle = '#58a6ff'; cx.lineWidth = 2; cx.stroke();

  // Direction arrow
  const ax = rx + Math.cos(thR) * r * 1.5;
  const ay = ry - Math.sin(thR) * r * 1.5;
  cx.beginPath(); cx.moveTo(rx, ry); cx.lineTo(ax, ay);
  cx.strokeStyle = '#58a6ff'; cx.lineWidth = 2.5; cx.stroke();
  // Arrowhead
  cx.beginPath();
  cx.moveTo(ax, ay);
  cx.lineTo(ax + Math.cos(thR+2.6)*7, ay - Math.sin(thR+2.6)*7);
  cx.lineTo(ax + Math.cos(thR-2.6)*7, ay - Math.sin(thR-2.6)*7);
  cx.closePath();
  cx.fillStyle = '#58a6ff'; cx.fill();

  // Centre dot
  cx.beginPath(); cx.arc(rx, ry, 3, 0, Math.PI*2);
  cx.fillStyle = '#fff'; cx.fill();
}

// ── Interactions ──────────────────────────────────────────────────────────
let drag = null;

cv.addEventListener('mousedown', e => {
  drag = {cx: e.clientX, cy: e.clientY, px: S.panX, py: S.panY};
  S.trackRobot = false;
  cv.classList.add('dragging');
});
cv.addEventListener('mousemove', e => {
  if (drag) {
    S.panX = drag.px + (e.clientX - drag.cx);
    S.panY = drag.py + (e.clientY - drag.cy);
    drawMap();
  }
  // Show world coords
  const r = cv.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;
  const ox = cv.width/2 + S.panX, oy = cv.height/2 + S.panY;
  const wx = (mx - ox) / S.scale, wy = -(my - oy) / S.scale;
  document.getElementById('coords').textContent =
    'x ' + wx.toFixed(2) + '  y ' + wy.toFixed(2);
});
cv.addEventListener('mouseup',    () => { drag = null; cv.classList.remove('dragging'); });
cv.addEventListener('mouseleave', () => { drag = null; cv.classList.remove('dragging'); });
cv.addEventListener('wheel', e => {
  e.preventDefault();
  S.scale = Math.max(10, Math.min(250, S.scale * (e.deltaY < 0 ? 1.12 : 0.89)));
  drawMap();
}, {passive: false});

// Double-click → goto that world point
cv.addEventListener('dblclick', e => {
  const r = cv.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;
  const ox = cv.width/2 + S.panX, oy = cv.height/2 + S.panY;
  const wx = ((mx - ox) / S.scale).toFixed(2);
  const wy = (-(my - oy) / S.scale).toFixed(2);
  document.getElementById('gt-x').value = wx;
  document.getElementById('gt-y').value = wy;
  S.goal = [+wx, +wy];
  cmd('goto ' + wx + ' ' + wy);
});

document.getElementById('zin').onclick  = () => { S.scale = Math.min(250, S.scale*1.3); drawMap(); };
document.getElementById('zout').onclick = () => { S.scale = Math.max(10,  S.scale*0.77); drawMap(); };
document.getElementById('ctr').onclick  = () => { S.panX=0; S.panY=0; S.trackRobot=true; drawMap(); };

// ── Keyboard shortcuts ────────────────────────────────────────────────────
const DRIVE_KEYS = new Set(['w','a','s','d','ArrowUp','ArrowDown','ArrowLeft','ArrowRight']);
const held = {};
let velTimer = null;

function tickVel() {
  let v=0, w=0;
  if (held.w || held.ArrowUp)    v += 0.3;
  if (held.s || held.ArrowDown)  v -= 0.3;
  if (held.a || held.ArrowLeft)  w += 45;
  if (held.d || held.ArrowRight) w -= 45;
  if (v||w) cmd('vel '+v+' '+w);
}

document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  const k = e.key;
  if (DRIVE_KEYS.has(k)) {
    e.preventDefault();
    held[k] = true;
    if (!velTimer) { tickVel(); velTimer = setInterval(tickVel, 180); }
  }
  if (k === ' ')   { e.preventDefault(); cmd('stop'); }
  if (k === 'p')   { cmd('ping'); }
  if (k === 'r')   { cmd('reset'); }
});

document.addEventListener('keyup', e => {
  delete held[e.key];
  if (!Object.keys(held).some(k => DRIVE_KEYS.has(k))) {
    if (velTimer) {
      clearInterval(velTimer); velTimer = null;
      cmd('stop');
    }
  }
});

// ── Init ──────────────────────────────────────────────────────────────────
new ResizeObserver(resize).observe(cv.parentElement);
resize();
connectSSE();
log('system', 'Web UI ready', 'info');
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    client: OperatorClient
    sse_clients: List[queue.Queue] = []
    _lock: threading.Lock = threading.Lock()

    def do_GET(self) -> None:
        if self.path in ('/', '/index.html'):
            self._html()
        elif self.path == '/stream':
            self._sse()
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path == '/command':
            self._command()
        else:
            self.send_error(404)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ---- responses ---------------------------------------------------------

    def _html(self) -> None:
        body = _HTML.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _sse(self) -> None:
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self._cors()
        self.end_headers()

        q: queue.Queue = queue.Queue(maxsize=50)
        with _Handler._lock:
            _Handler.sse_clients.append(q)
        try:
            while True:
                try:
                    data = q.get(timeout=15)
                    self.wfile.write(f"data: {json.dumps(data)}\n\n".encode())
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with _Handler._lock:
                try:
                    _Handler.sse_clients.remove(q)
                except ValueError:
                    pass

    def _command(self) -> None:
        try:
            n = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(n) if n else b'{}')
            line = body.get('cmd', '').strip()
            p = _Handler.client.send_line(line)
            if p is None:
                self._json({'ok': False, 'error': 'link down'}, 503)
                return
            p.ack_event.wait(timeout=5)
            self._json({'ok': bool(p.ok), 'seq': p.seq})
            def _wait_result() -> None:
                if p.result_event.wait(timeout=60):
                    _Handler.broadcast({'type': 'result', 'seq': p.seq,
                                        'cmd': line, **p.result})
            threading.Thread(target=_wait_result, daemon=True).start()
        except ProtocolError as exc:
            self._json({'ok': False, 'error': str(exc)}, 400)
        except Exception as exc:
            self._json({'ok': False, 'error': str(exc)}, 500)

    def _json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self) -> None:
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')

    def log_message(self, *_) -> None:
        pass  # silence access log

    @classmethod
    def broadcast(cls, data: dict) -> None:
        with cls._lock:
            clients = list(cls.sse_clients)
        for q in clients:
            try:
                q.put_nowait(data)
            except queue.Full:
                pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(robot_host: str = '127.0.0.1', robot_port: int = 9000,
         web_port: int = 8080, open_browser: bool = True) -> None:
    transport = make_client("tcp", robot_host, robot_port)
    client = OperatorClient(transport)
    client.listeners.append(lambda msg: _Handler.broadcast(msg))
    _Handler.client = client

    print(f"Connecting to robot at {robot_host}:{robot_port} ...", end=' ', flush=True)
    try:
        client.connect(timeout=8)
    except Exception as exc:
        print(f"FAILED\n  {exc}")
        sys.exit(1)
    print("OK")

    server = ThreadingHTTPServer(("127.0.0.1", web_port), _Handler)
    url = f"http://localhost:{web_port}"
    print(f"Web UI: {url}")
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        client.close()
        server.server_close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="P3-DX teleoperation web UI")
    ap.add_argument('--robot-host', default='127.0.0.1', help='Robot server host')
    ap.add_argument('--robot-port', type=int, default=9000, help='Robot server TCP port')
    ap.add_argument('--web-port',   type=int, default=8080, help='Web UI port (default 8080)')
    ap.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    args = ap.parse_args()
    main(args.robot_host, args.robot_port, args.web_port, not args.no_browser)
