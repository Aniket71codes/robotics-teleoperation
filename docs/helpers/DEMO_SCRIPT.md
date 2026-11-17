# 20-minute video and demo script

Recorded as an online meeting (Meet/Teams/Zoom), every camera on for the whole recording, gallery view,
no cuts (Project Instructions §3C). Accepted length 18-22 min. Aim for 20:00.

## Before recording (T-30 min)
- [ ] Everyone has the latest `main` and `python -m pytest` passes.
- [ ] Demo PC (Priyam's or Harsh's): broker running (`mosquitto -c config/mosquitto.conf`), 4 terminals
      open and large font (≥ 18 pt), windows arranged: T1 server, T2 shell, T3 `mosquitto_sub`, T4 spare.
- [ ] Run the whole demo once. Then `reset` the robot.
- [ ] Slides PDF open on the presenter's screen; a timer visible to the presenter.
- [ ] Fallback: if anything fails live, run `python -m teleop.cli --script macros/goto_square.tlm`
      (known-good) and say what went wrong. Never fake output.

## Timeline

| Time | Who | What |
|---|---|---|
| 00:00-01:00 | All | Each member, camera on: "I am <name>, SAP ID <id>." |
| 01:00-04:00 | Akshat | Slides 1-3, 8: problem, objectives, robot and environment model |
| 04:00-07:00 | Aniket | Slides 4, 5, 7: existing solutions, novelty, architecture |
| 07:00-08:00 | Priyam | Slide 6: syllabus mapping |
| 08:00-10:00 | Harsh | Slides 9, 11: protocol and shell, simulation setup |
| 10:00-11:00 | Priyam | Slide 10: controller design and tuning |
| 11:00-17:00 | Priyam + Harsh | Slide 12: **live demo** (below) |
| 17:00-19:00 | Yeshang | Slides 13-15: results, comparison, contribution |
| 19:00-20:00 | All | Slides 16-17: one sentence each on conclusion; thank you |

## Live demo (6 minutes): Priyam explains, Harsh types

| Clock | Terminal | Command (Harsh types) | What Priyam says |
|---|---|---|---|
| 11:00 | T1 | `python -m teleop.server --backend mock --transport tcp --port 9000` | "This is the robot. It runs a 20 Hz loop and waits for an operator." (If CoppeliaSim is verified: `--backend coppelia`, and show the scene.) |
| 11:20 | T2 | `python -m teleop.cli --port 9000` then `ping`, `status` | "We are connected over TCP. The round trip is under a millisecond on one PC." |
| 11:40 | T2 | `move 1` → `turn 90` → `goto 1 1` (with `wait` in between) | "Each command is closed-loop on the robot with a heading PID. The result line shows the final error, about 3 cm." |
| 12:40 | T2 | `macro macros/safety_demo.tlm` | "We drive at the box and never send stop. The safety layer slows down from 0.8 m and stops at 0.30 m." Point at OBSTACLE. |
| 13:40 | T2 | `vel 0.2 0`, then close the shell window | "Now the operator disappears. Watch the robot terminal: one second later the watchdog stops the robot." Point at the T1 log line. |
| 14:20 | T1/T2 | Ctrl+C T1; `python -m teleop.server --transport mqtt --qos 1`; T3 `mosquitto_sub -h 127.0.0.1 -t 'teleop/#' -v`; T2 `python -m teleop.cli --transport mqtt --qos 1` | "Same robot, now over MQTT through the Mosquitto broker. T3 shows every message on the topics." |
| 15:00 | T2 | `rtt 10`, `goto 0 0`, `wait` | "QoS 1 with Nagle switched off: about 1-2 ms on one PC." |
| 15:30 | T4 | `python -m teleop.netem --listen 1890 --target 127.0.0.1:1883 --delay 200 --jitter 50 --loss 0.05`, then T2 `quit` and reconnect with `--port 1890`, `rtt 10` | "Now a bad network: 200 ms each way and 5 % loss. The round trip jumps to about half a second." |
| 16:20 | T2 | `goto 1 0`, `wait` | "Goto still arrives at the same 3 cm accuracy. Only the start is late. That is supervisory control." |
| 16:50 | n/a | back to slides | "In the results Yeshang shows what happens when you steer directly over this link." |

## After recording
- [ ] Length between 18:00 and 22:00; everybody visible all the time.
- [ ] Upload to YouTube as **Unlisted**, and open the link in a private window to test it.
- [ ] Put the link in the report Appendix and on slide 17.
