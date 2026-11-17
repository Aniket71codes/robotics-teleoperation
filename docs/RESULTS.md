# Results notes

Owner: **Yeshang Soni** (S0: Aniket Singh Bisht, PID tuning: Priyam Paliwal).

**Every number on this page comes from runs on the mock backend** (pure-Python P3-DX simulator,
`backend=mock` in every CSV row). None comes from CoppeliaSim. The runs were made on 2026-11-14 on one
Linux x86_64 PC (Python 3.12.3, Mosquitto 2.0.18), with 16 trials in parallel. Raw rows are in
`results/raw/`, tables in `results/tables/`, figures in `results/figures/`, and run metadata in
`results/run_info.json`. Regenerate everything with `python experiments/run_experiments.py`,
`python experiments/pid_tuning.py` and `python experiments/analyze.py`.

## Set-up

* **Transports:** TCP socket; MQTT QoS 0; MQTT QoS 1. MQTT goes through a local Mosquitto with
  `set_tcp_nodelay true`, and the clients set `TCP_NODELAY`.
* **Network conditions** (applied to the operator's link by `teleop/netem.py`, in each direction):
  C0 none · C1 50 ± 10 ms · C2 100 ± 25 ms + 1 % segment loss · C3 200 ± 50 ms + 5 % segment loss.
  Loss is modelled as a TCP retransmission (RTO ≥ 200 ms, doubling), because both transports run over TCP.
* **Trials:** 10 per cell. 550 network trials in total (S0 40, S1 120, S2 120, S3 120, S4 30, S5 120),
  plus 50 PID turns.
* **Re-runs:** S2 and S5 were re-run after two changes: (a) the safety-layer hysteresis fix, and (b) the
  S2 operator re-sending a goal that was rejected as stale or aborted by the watchdog. S4 was re-run
  after the robot started ignoring duplicate (session, seq) commands; its counts did not change. The other scenarios
  never bring the robot within the 0.30 m stop line, so (a) does not affect them.

## S0 Nagle ablation
MQTT QoS 1 ping round trip on localhost, 10 trials × 30 pings per combination (`fig_nagle.png`).

| Broker TCP_NODELAY | Client TCP_NODELAY | Trials | Median RTT (ms, mean ± sd) | Mean of max RTT (ms) |
|---|---|---|---|---|
| off (default) | off (paho default) | 10 | 55.2 ± 7.3 | 85.3 |
| off (default) | on | 10 | 41.7 ± 0.1 | 45.9 |
| on | off (paho default) | 10 | 41.8 ± 0.3 | 43.5 |
| on | on | 10 | 1.2 ± 0.1 | 2.0 |

**Finding:** both sides must switch off Nagle's algorithm. With the defaults (paho never sets
`TCP_NODELAY`; Mosquitto's `set_tcp_nodelay` is `false`), each QoS 1 round trip costs about 40-55 ms even
on one machine. Fixing only one side is not enough. Fixing both brings it to 1.2 ms.

## S1 Round-trip latency
50 pings at 5 Hz per trial (`fig_rtt_box.png`, `fig_rtt_cdf.png`). "Up/Down" is the measured byte rate on
the operator link, including heartbeats (4 Hz) and telemetry (10 Hz).

| Transport | Condition | Trials | Replies | Median RTT (ms) | Mean (ms) | P95 (ms) | Max (ms) | Up (B/s) | Down (B/s) |
|---|---|---|---|---|---|---|---|---|---|
| TCP socket | C0: none | 10 | 500/500 | 1.0 | 1.0 | 1.3 | 1.5 | 495 | 1675 |
| MQTT QoS 0 | C0: none | 10 | 500/500 | 1.8 | 1.8 | 2.4 | 4.6 | 720 | 2091 |
| MQTT QoS 1 | C0: none | 10 | 500/500 | 2.2 | 2.2 | 3.1 | 4.8 | 799 | 2157 |
| TCP socket | C1: 50±10 ms | 10 | 500/500 | 103.5 | 102.1 | 125.5 | 146.3 | 494 | 1676 |
| MQTT QoS 0 | C1: 50±10 ms | 10 | 500/500 | 103.6 | 102.7 | 126.0 | 144.3 | 720 | 2091 |
| MQTT QoS 1 | C1: 50±10 ms | 10 | 500/500 | 108.7 | 109.3 | 129.3 | 150.7 | 799 | 2158 |
| TCP socket | C2: 100±25 ms, 1% | 10 | 500/500 | 205.9 | 217.7 | 323.1 | 528.7 | 467 | 1656 |
| MQTT QoS 0 | C2: 100±25 ms, 1% | 10 | 500/500 | 212.2 | 220.6 | 291.0 | 682.7 | 677 | 2056 |
| MQTT QoS 1 | C2: 100±25 ms, 1% | 10 | 500/500 | 229.1 | 244.4 | 436.3 | 802.1 | 709 | 2084 |
| TCP socket | C3: 200±50 ms, 5% | 10 | 500/500 | 464.4 | 586.7 | 1078.2 | 2669.8 | 267 | 1513 |
| MQTT QoS 0 | C3: 200±50 ms, 5% | 10 | 499/500 | 484.9 | 647.0 | 1442.3 | 2795.5 | 394 | 1823 |
| MQTT QoS 1 | C3: 200±50 ms, 5% | 10 | 500/500 | 622.9 | 761.4 | 1539.4 | 2802.1 | 429 | 1855 |

**Findings**
* Without impairment TCP is fastest (median 1.0 ms), because MQTT adds a broker hop (1.8 / 2.2 ms).
  Once there is real delay, that difference is lost in the network delay (C1: 103.5 / 103.6 / 108.7 ms).
* With loss, QoS 1 has the longest tail (C3 p95: TCP 1078 ms, QoS 0 1442 ms, QoS 1 1539 ms). Its extra
  PUBACK packets share the same lossy TCP stream, so they add head-of-line blocking.
* MQTT costs more bytes: at C0 the uplink is 495 B/s (TCP), 720 B/s (QoS 0) and 799 B/s (QoS 1), which
  is +45 % and +61 %.
* Only one of the 6000 pings got no reply within 5 s (MQTT QoS 0, C3).

## S2 Supervisory control: `goto` around a 2 m square
Four `goto` goals at 0.4 m/s. The operator re-sends a goal that was rejected as stale or aborted by the
watchdog (`fig_square_time.png`, `fig_square_paths.png`).

| Transport | Condition | Trials | Completion (s) | Goals reached | First try | Re-sent goals | Mean goal error (cm) | Path (m) | Watchdog trips | Collisions |
|---|---|---|---|---|---|---|---|---|---|---|
| TCP socket | C0: none | 10 | 27.20 ± 0.00 | 40/40 | 40/40 | 0 | 2.7 | 7.96 | 0 | 0 |
| TCP socket | C1: 50±10 ms | 10 | 27.48 ± 0.05 | 40/40 | 40/40 | 0 | 2.7 | 7.96 | 0 | 0 |
| TCP socket | C2: 100±25 ms, 1% | 10 | 27.93 ± 0.09 | 40/40 | 40/40 | 0 | 2.7 | 7.96 | 0 | 0 |
| TCP socket | C3: 200±50 ms, 5% | 10 | 29.82 ± 0.87 | 40/40 | 39/40 | 1 | 2.7 | 7.96 | 1 | 0 |
| MQTT QoS 0 | C0: none | 10 | 27.20 ± 0.00 | 40/40 | 40/40 | 0 | 2.7 | 7.96 | 0 | 0 |
| MQTT QoS 0 | C1: 50±10 ms | 10 | 27.50 ± 0.06 | 40/40 | 40/40 | 0 | 2.7 | 7.96 | 0 | 0 |
| MQTT QoS 0 | C2: 100±25 ms, 1% | 10 | 27.94 ± 0.10 | 40/40 | 40/40 | 0 | 2.7 | 7.96 | 0 | 0 |
| MQTT QoS 0 | C3: 200±50 ms, 5% | 10 | 30.17 ± 1.28 | 40/40 | 39/40 | 1 | 2.7 | 7.96 | 2 | 0 |
| MQTT QoS 1 | C0: none | 10 | 27.20 ± 0.00 | 40/40 | 40/40 | 0 | 2.7 | 7.96 | 0 | 0 |
| MQTT QoS 1 | C1: 50±10 ms | 10 | 27.53 ± 0.04 | 40/40 | 40/40 | 0 | 2.7 | 7.96 | 0 | 0 |
| MQTT QoS 1 | C2: 100±25 ms, 1% | 10 | 28.09 ± 0.15 | 40/40 | 39/40 | 1 | 2.7 | 7.96 | 1 | 0 |
| MQTT QoS 1 | C3: 200±50 ms, 5% | 10 | 32.18 ± 2.40 | 40/40 | 30/40 | 11 | 2.8 | 7.96 | 14 | 0 |

**Findings:** every one of the 480 goals was reached, with the same 2.7 cm final error and the same
7.96 m path under every condition, because the control loop is closed on the robot. Delay only adds
time: +10 % (TCP), +11 % (QoS 0) and +18 % (QoS 1) at C3. Most of that is re-sending: at C3, QoS 1
needed 11 re-sent goals and tripped the watchdog 14 times, against 1 and 1-2 for the other two.
Queued QoS 1 retransmissions make the heartbeat gaps longer.

## S3 Direct control: synthetic operator steering with `vel`
A pure-pursuit operator **model** (not a human). It sends `vel` at 5 Hz, based on the pose it last saw
plus 0.2 s reaction time, along an L-shaped 7.0 m lane (`fig_operator_bars.png`, `fig_operator_paths.png`).
The time limit is 60 s.

| Transport | Condition | Finished | Time (s) | RMS XTE (cm) | Max XTE (cm) | Min clearance (m) | Stale rejected | Watchdog trips | Collisions |
|---|---|---|---|---|---|---|---|---|---|
| TCP socket | C0: none | 10/10 | 20.2 ± 0.0 | 3.9 ± 0.0 | 11.6 | 1.02 | 0 | 0 | 0 |
| TCP socket | C1: 50±10 ms | 10/10 | 20.5 ± 0.1 | 4.1 ± 0.3 | 12.6 | 1.02 | 0 | 0 | 0 |
| TCP socket | C2: 100±25 ms, 1% | 10/10 | 22.3 ± 0.2 | 3.9 ± 0.7 | 11.1 | 1.01 | 0 | 0 | 0 |
| TCP socket | C3: 200±50 ms, 5% | 5/10 | 53.2 ± 8.2 | 20.1 ± 3.1 | 44.4 | 0.78 | 82 | 11 | 0 |
| MQTT QoS 0 | C0: none | 10/10 | 20.2 ± 0.0 | 3.9 ± 0.0 | 11.6 | 1.02 | 0 | 0 | 0 |
| MQTT QoS 0 | C1: 50±10 ms | 10/10 | 20.6 ± 0.2 | 3.9 ± 0.4 | 12.8 | 1.02 | 0 | 0 | 0 |
| MQTT QoS 0 | C2: 100±25 ms, 1% | 10/10 | 22.3 ± 0.2 | 3.6 ± 0.9 | 10.8 | 1.02 | 0 | 0 | 0 |
| MQTT QoS 0 | C3: 200±50 ms, 5% | 8/10 | 52.3 ± 9.6 | 21.4 ± 8.2 | 44.4 | 0.83 | 75 | 16 | 0 |
| MQTT QoS 1 | C0: none | 10/10 | 20.2 ± 0.0 | 3.9 ± 0.0 | 11.6 | 1.02 | 0 | 0 | 0 |
| MQTT QoS 1 | C1: 50±10 ms | 10/10 | 20.5 ± 0.1 | 4.0 ± 0.4 | 12.8 | 1.01 | 0 | 0 | 0 |
| MQTT QoS 1 | C2: 100±25 ms, 1% | 10/10 | 22.4 ± 0.4 | 3.8 ± 0.3 | 10.4 | 1.01 | 0 | 1 | 0 |
| MQTT QoS 1 | C3: 200±50 ms, 5% | 2/10 | 57.9 ± 7.0 | 23.4 ± 5.8 | 51.4 | 0.83 | 142 | 24 | 0 |

**Findings:** up to C2 the operator tracks as well as with no delay (RMS cross-track error 3.6-4.1 cm,
22 s). At C3 direct control breaks down. Error grows about 5× (20-23 cm RMS, up to 51 cm). Only 5, 8 and
2 of 10 runs finish within 60 s. The robot weaves (`fig_operator_paths.png`). Between 75 and 142 late
`vel` commands are rejected by the stale guard, and the watchdog trips 11-24 times, which stops the robot
and breaks the feedback loop further. The same link that costs `goto` 10-18 % makes `vel` steering
unusable.

## S4 Link outage (3 s) during `vel 0.25`
C1 link. The operator keeps sending `vel` at 5 Hz and `ping` at 2 Hz through the outage. The link comes
back with all connections reset (`fig_outage_timeline.png`).

| Transport | Trials | Stop after outage start (s) | Coast (cm) | Cmds sent in outage | Lost | Rejected stale | Executed late | Pings answered late | Resume after link back (s) | Collisions |
|---|---|---|---|---|---|---|---|---|---|---|
| TCP socket | 10 | 1.07 ± 0.03 | 25.0 | 150 | 150 | 0 | 0 | 0/50 | 0.35 | 0 |
| MQTT QoS 0 | 10 | 1.04 ± 0.08 | 24.9 | 150 | 150 | 0 | 0 | 0/50 | 0.35 | 0 |
| MQTT QoS 1 | 10 | 1.06 ± 0.07 | 25.3 | 150 | 0 | 125 | 25 | 50/50 | 0.33 | 0 |

**Findings**
* The watchdog stops the robot 1.0-1.1 s after the link fails, after about 25 cm of coasting, the same
  for every transport. Safety does not depend on the transport.
* TCP and QoS 0 lose every command sent during the outage. QoS 1 delivers all of them after the
  reconnect. The stale guard rejects 125 of the 150 delivered commands. The 25 that are executed late
  were sent in the last second of the outage, so they were still younger than the 1.0 s limit. Without
  the guard, QoS 1 would have replayed 3 s of old joystick commands.
* All three resume driving 0.33-0.35 s after the link returns.

## S5 Obstacle safety without any operator `stop`
The operator commands `vel 0.5` straight at the box and never stops (`fig_safety.png`).

| Transport | Condition | Trials | Stopped by obstacle guard | Mean clearance at stop (cm) | Worst clearance (cm) | Watchdog trips | Collisions |
|---|---|---|---|---|---|---|---|
| TCP socket | C0: none | 10 | 10/10 | 29.4 | 29.0 | 0 | 0 |
| TCP socket | C1: 50±10 ms | 10 | 10/10 | 29.7 | 29.2 | 0 | 0 |
| TCP socket | C2: 100±25 ms, 1% | 10 | 10/10 | 29.5 | 29.0 | 0 | 0 |
| TCP socket | C3: 200±50 ms, 5% | 10 | 10/10 | 29.3 | 29.0 | 0 | 0 |
| MQTT QoS 0 | C0: none | 10 | 10/10 | 29.6 | 29.3 | 0 | 0 |
| MQTT QoS 0 | C1: 50±10 ms | 10 | 10/10 | 29.6 | 28.9 | 0 | 0 |
| MQTT QoS 0 | C2: 100±25 ms, 1% | 10 | 10/10 | 29.7 | 29.3 | 0 | 0 |
| MQTT QoS 0 | C3: 200±50 ms, 5% | 10 | 8/10 | 29.6 | 29.2 | 3 | 0 |
| MQTT QoS 1 | C0: none | 10 | 10/10 | 29.6 | 29.1 | 0 | 0 |
| MQTT QoS 1 | C1: 50±10 ms | 10 | 10/10 | 29.7 | 29.1 | 0 | 0 |
| MQTT QoS 1 | C2: 100±25 ms, 1% | 10 | 10/10 | 29.5 | 29.2 | 0 | 0 |
| MQTT QoS 1 | C3: 200±50 ms, 5% | 10 | 6/10 | 29.7 | 29.3 | 6 | 0 |

**Findings:** 0 collisions in all 120 runs. Every run that reached the box stopped between 28.9 and 30.2 cm from
it (target 30 cm), independent of transport and network. In 6 runs at C3 (QoS 0: 2, QoS 1: 4) a delay
spike over 1 s tripped the watchdog first, which also stopped the robot safely, before it reached the box.

## PID tuning (heading loop, no network)
`turn` to 10 angles (30-165°) per gain set, with the server's acceleration limit (`fig_pid_step.png`).

| Gain set | Turns | Mean overshoot (deg) | Max overshoot (deg) | Mean settling time to ±2 deg (s) | Mean final error (deg) | Reached |
|---|---|---|---|---|---|---|
| P Kp=1.0 | 10 | 0.00 | 0.00 | 3.70 | 1.23 | 10/10 |
| P Kp=3.0 | 10 | 0.02 | 0.16 | 1.38 | 0.29 | 10/10 |
| P Kp=8.0 | 10 | 20.46 | 22.57 | 2.56 | 0.92 | 10/10 |
| PD Kp=3.0 Kd=0.15 | 10 | 0.00 | 0.00 | 1.67 | 0.75 | 10/10 |
| PID Kp=3 Ki=1 Kd=0.15 | 10 | 7.27 | 8.12 | 5.57 | 1.50 | 4/10 |

**Findings:** Kp = 8 overshoots by about 20°. Adding Ki = 1 causes integrator wind-up (7° overshoot,
only 4/10 turns settle inside the tolerance). P with Kp = 3 settles fastest (1.38 s, essentially no
overshoot). The PD set used in all network runs (Kp 3, Kd 0.15) is 0.3 s slower but also has no overshoot.
Re-checking the default gain is task 1 of Priyam's commit plan.

## Across all scenarios
* **Collisions: 0** in all 550 network trials.
* **What did not work / limits:** direct `vel` steering at C3; QoS 1 tail latency under loss; the mock
  has no wheel slip or inertia beyond a first-order motor lag; the operator in S3 is a model, not a
  person; and the proxy models loss as TCP retransmission at chunk level (no congestion window).
