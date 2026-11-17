# Aniket Singh Bisht: MQTT transport, Mosquitto, latency TCP vs MQTT, architecture diagram

## 1. Your role in one paragraph
You own **the MQTT path**: the paho-mqtt transport (topics, QoS 0/1, persistent sessions, Last Will,
retained status), the Mosquitto broker set-up, and the **latency comparison of TCP versus MQTT QoS 0
and QoS 1**, including the Nagle ablation (S0), which is one of the project's novelty points. You also own
the **architecture diagram** and the novelty text.

## 2. Files you own
| File | What it does |
|---|---|
| `teleop/transport/mqtt.py` | `MqttServer` (robot) and `MqttClient` (operator), QoS, LWT, TCP_NODELAY |
| `config/mosquitto.conf`, `tools/mosquitto/run_mosquitto.sh` | broker configuration and the no-sudo Linux launcher |
| `tests/test_mqtt.py` | MQTT tests (skip without a broker) |
| `experiments/scenarios.py` → `s0_nagle`, and the S1 analysis | latency experiments |
| `docs/MQTT_SETUP.md`, `docs/ARCHITECTURE.md`, `docs/NOVELTY.md` | docs |
| `report/diagrams.py` → `architecture()` | the architecture figure |

## 3. Everyday analogy
TCP is a **phone call**: robot and operator are directly connected, and if the line drops the call is
over. MQTT is a **post office with PO boxes** (the broker). The operator posts letters to box
`teleop/p3dx/cmd`, and the robot has a key to that box. **QoS 0** is a postcard: cheap, and if the
post office is closed it is thrown away. **QoS 1** is registered mail: the post office signs for it
(PUBACK), and if you are away it keeps your mail until you return (persistent session). The **Last
Will** is a sealed letter you leave at the post office saying "if I vanish, tell the robot I'm gone".

## 4. How it works (one page)
```
 operator (MqttClient)                 Mosquitto broker                   robot (MqttServer)
 ─────────────────────                 ────────────────                   ──────────────────
 CONNECT  will=operator:"offline"  ──►  stores the will                 ◄── CONNECT will=status:"offline"
 SUBSCRIBE telem, event, status                                           SUBSCRIBE cmd, operator
 PUBLISH cmd {"seq":4,...} qos1   ──►  PUBACK ◄──┐   forwards  ──►  on_message → server inbox
                                                  └ (QoS 1 only)
          ◄── forwards ◄──  PUBLISH event {"type":"ack","seq":4} ◄── robot
          ◄── forwards ◄──  PUBLISH telem 10 Hz                  ◄── robot
 operator's socket dies ─X                broker publishes the will:
                                          operator = "offline"  ──►  robot stops at once (LINK_LOST)
```
**QoS 1 while the link is down:** paho keeps the message in its queue and sends it after reconnecting.
The broker keeps messages for a persistent subscriber. After a 3 s outage, 150 old `vel` commands
arrived late (S4). The robot's stale-command guard rejected 125 of them.

**Nagle:** paho never sets TCP_NODELAY, and Mosquitto has `set_tcp_nodelay false` by default. With
Nagle on, a small packet waits until the previous one is ACKed, and the receiver delays its ACK by up to
~40 ms. Result: 55 ms per QoS 1 ping on one PC. With both sides fixed it is 1.2 ms (S0).

## 5. Five-minute manual test
```bash
tools/mosquitto/run_mosquitto.sh 1883        # or: mosquitto -c config/mosquitto.conf -v
mosquitto_sub -h 127.0.0.1 -t 'teleop/#' -v  # optional, shows all traffic
python -m teleop.server --transport mqtt --qos 1
python -m teleop.cli --transport mqtt --qos 1
teleop> rtt 20              # ~1-2 ms on localhost
teleop> vel 0.2 0           # then kill the shell window (not 'quit')
```
The server must log `link lost (operator_offline)` or `(watchdog)`. Then run
`python -m pytest tests/test_mqtt.py -v` (9 tests, QoS 0 and 1).

## 6. Task checklist
| Task | Done when |
|---|---|
| Install Mosquitto on your own OS and repeat the manual test | works; MQTT_SETUP.md updated |
| Re-run S0 on your laptop | table added to RESULTS.md, with your OS named |
| Test: QoS 1 commands queued during an outage are rejected as stale | test passes with a broker |
| Username/password support | works with a `password_file` broker |
| (stretch) TLS | works on 8883 with a self-signed certificate |
| Real two-laptop Wi-Fi latency (TCP vs QoS 0 vs QoS 1) | CSV and a paragraph in RESULTS.md |
| Editable architecture diagram | `docs/img/architecture.drawio` committed |
| Report Sections 3 and 4 | `check_report.py` passes |

## 7. Your commit plan
| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `docs/aniket-mosquitto` | `docs(mqtt): verify Mosquitto install on <your OS>` | `docs/MQTT_SETUP.md` | sub/pub check works |
| 2 | `exp/aniket-nagle` | `exp(mqtt): re-run Nagle ablation S0 on own laptop` | `results/raw/`, `docs/RESULTS.md` | 10 trials per combination |
| 3 | `test/aniket-qos1-outage` | `test(mqtt): QoS 1 commands queued in an outage are rejected as stale` | `tests/test_mqtt.py` | passes with broker, skips without |
| 4 | `feat/aniket-auth` | `feat(mqtt): username/password options and password_file docs` | `mqtt.py`, `cli.py`, `server.py`, docs | password broker test |
| 5 | `feat/aniket-tls` | `feat(mqtt): optional TLS on port 8883` | `mqtt.py`, docs | manual TLS test |
| 6 | `exp/aniket-wifi` | `exp(net): real two-laptop Wi-Fi latency, TCP vs MQTT QoS 0/1` | `experiments/`, `results/` | rows labelled `network=real Wi-Fi` |
| 7 | `docs/aniket-architecture` | `docs(arch): editable architecture diagram (draw.io) and export` | `docs/img/` | matches the code |
| 8 | `docs/aniket-report` | `docs(report): write Sections 3 and 4` | `report/content.py` | check_report passes |

Hint for #3: use `ImpairmentProxy` in front of the broker, call `proxy.outage(2.0)`, keep sending
`vel` during it, and after reconnecting assert `server.stats["stale"] > 0`.

## 8. Figures and evidence you produce
`fig_nagle.png`, `fig_rtt_box.png`, `fig_rtt_cdf.png`, Table T_latency, Table T_nagle, the architecture
diagram (`diag_architecture.png`), and the byte-rate numbers (MQTT costs +45 % / +61 % uplink).

## 9. Report sections you write
**3 Literature and Industry Review** and **4 Novelty** (about 5 pages), plus your row in Section 10,
your reflection in Section 11 and your Declaration signature.

## 10. Likely viva questions
1. **Difference between QoS 0, 1 and 2?** 0 = at most once (no ack). 1 = at least once (PUBACK, resent
   until acked, duplicates possible). 2 = exactly once (4-packet handshake). We use 0 and 1. The robot
   ignores duplicates by (sid, seq), so QoS 2's extra round trip is not needed.
2. **What is a persistent session?** `clean_session=False`: the broker remembers the client's
   subscriptions and stores its QoS 1 messages while it is offline. We use it only with QoS 1.
3. **What is the Last Will and Testament?** A message registered at CONNECT, which the broker publishes
   if the client disappears without DISCONNECT. Our robot stops when the operator's will arrives.
4. **When does the broker notice a dead client?** When the TCP connection closes, at once. If packets just
   stop, it notices after 1.5 × keepalive (we use 5 s, or 2 s in experiments). The 1 s watchdog is therefore
   faster for silent failures, and the LWT is a second safety net.
5. **Why was QoS 1 slower than QoS 0 under loss (C3 p95 1539 vs 1442 ms)?** Its PUBACK packets share the
   same lossy TCP stream. More packets mean more chances to wait for a retransmission (head-of-line blocking).
6. **Is QoS 1 "better" for teleoperation?** Not for motion. After an outage it delivers old commands.
   Without our stale guard the robot would have replayed 3 s of joystick input. It is better for
   one-off commands where every message must arrive (e.g. a mission upload), combined with an age check.
7. **Why did MQTT have 1-2 ms RTT and TCP 1.0 ms on localhost?** MQTT goes operator → broker → robot and
   back: two hops instead of one.
8. **Why is the broker a single point of failure, and how is it handled in industry?** If Mosquitto stops,
   nobody talks. Options: broker clustering/bridging, or running the broker on the robot itself.
9. **How did you find the Nagle problem?** QoS 1 RTT was about 40-55 ms on one PC, but QoS 0 was 1 ms. We
   then measured the four combinations of TCP_NODELAY on and off (S0, 10 trials each).
10. **Why MQTT for robots at all?** Decoupling (many subscribers: logger, dashboard, second operator),
    retained status, LWT, standard tooling, and it works through one outbound port behind NAT.

## 11. Slides and demo part
* **Slides 4, 5 and 7** (Existing Solutions, Novelty, System Architecture).
* In the demo: start the broker and run `mosquitto_sub -t 'teleop/#' -v` so viewers can see the messages.

## 12. Small, safe extension tasks
auth, TLS, a `--clean-session` flag, a dashboard subscriber that only reads `telem`, and broker
statistics (`$SYS/#`) in the experiment log.
