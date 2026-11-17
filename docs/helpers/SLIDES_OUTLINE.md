# Slide outline (17 slides including title and end)

Rules (Project Instructions §3): at most 17 slides; headings 28-32 pt; body text at least 20 pt; one idea
per slide; a figure on most slides; the presenter's name in a corner of every slide; own figures
(all figures below are ours, from `results/figures/`). Export as one PDF.

Time budget for the 20-minute video: about 1 min of introductions, about 13 min of slides, about 6 min
of live demo. Each member speaks about 4 minutes.

| # | Title | Content (keep to 3-4 short lines) | Figure | Presenter |
|---|---|---|---|---|
| 1 | Networked Teleoperation of a Robot through Shell Commands | Project No. `<Pxx>`, Group `<Gxx>`, Batch B3-B4, names + SAP IDs, CSAI4014, faculty `<name>` | UPES logo | Akshat |
| 2 | Problem and Motivation | Robots in warehouses, hospitals and inspection are driven remotely over imperfect networks. Delay, jitter and loss make direct driving unsafe. Which transport and which control mode? | photo-free: simple sketch operator → network → robot | Akshat |
| 3 | Objectives | (1) shell command language over TCP and MQTT; (2) PID motion primitives + on-robot safety; (3) compare TCP / QoS 0 / QoS 1 under 4 network conditions, 10 trials each; (4) zero collisions | objectives list with icons | Akshat |
| 4 | Existing Solutions | ROS teleop, MQTT in IIoT, supervisory control (Sheridan). Gap: few side-by-side task-level comparisons that include outages and stale commands | comparison table (report Table 1) | Aniket |
| 5 | Novelty | 5 points from docs/NOVELTY.md, each with its number: Nagle 55→1.2 ms; QoS 1 replays 150 commands, guard rejects 125; goto +10-18 % vs vel steering 5× error; 0 collisions in 550 trials | `fig_nagle.png` small | Aniket |
| 6 | Syllabus Mapping | 5-6 rows from docs/SYLLABUS_MAPPING.md (kinematics, PID, sensors, reactive/safety, FSM, communication) | table | Priyam |
| 7 | System Architecture | operator shell → transport → (proxy/broker) → robot server → controller → safety → backend | `diag_architecture.png` | Aniket |
| 8 | Robot and Environment Model | P3-DX differential drive, 16 sonars, 7 × 6 m room with box and cylinder; kinematics equations; mock vs CoppeliaSim | equations + scene screenshot | Akshat |
| 9 | Algorithm 1: Command Protocol and Shell | grammar, JSON message, seq/sid, ack/result; heartbeat; exclusive control | `diag_sequence.png` | Harsh |
| 10 | Algorithm 2: Controller Design and Tuning | move/turn/goto laws, heading PID, cos² speed; tuning table: P Kp 3 settles 1.38 s, PID wind-up | `fig_pid_step.png` | Priyam |
| 11 | Simulation Setup | Python 3.12, mock + CoppeliaSim backend, Mosquitto 2.0.18, impairment proxy C0-C3, the 4 commands to run it | terminal screenshot | Harsh |
| 12 | Live Demonstration | (switch to screen share; see DEMO_SCRIPT.md) | n/a | Priyam (+ Harsh typing) |
| 13 | Results 1: Latency and Nagle | RTT box plot; the TCP vs MQTT gap disappears under delay; QoS 1 has the longest tail under loss | `fig_rtt_box.png` | Yeshang |
| 14 | Results 2: Control Modes, Outage, Safety | goto vs vel under C3; outage table (lost / stale / late); 0 collisions | `fig_operator_bars.png` + outage table | Yeshang |
| 15 | Team Contribution | 5 rows: member → module → commits (from `scripts/git_author_stats.py`) | table | Yeshang |
| 16 | Conclusion and Industry Use | supervisory commands + on-robot safety + age check; MQTT for fleets/dashboards, TCP for 1:1 low overhead; future: real P3-DX, human trials | none | All (one sentence each) |
| 17 | Thank You / Q&A | GitHub link, contact e-mails | QR code to repo | All |

Presenter total: Akshat 1-3, 8 · Aniket 4, 5, 7 · Priyam 6, 10, 12 (demo) · Harsh 9, 11 (+ typing in the demo) ·
Yeshang 13-15. Put the presenter's name in the bottom-right corner of each slide.
