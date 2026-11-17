# Networked Teleoperation of a Robot through Shell Commands

CSAI4014 Algorithms for Intelligent Systems and Robotics · UPES · B.Tech CSE (AI & ML) Sem VII · Batch B3-B4

An operator types shell commands (`move`, `turn`, `goto`, `vel`, `stop`, `status`, `ping`, `reset`)
in a terminal. The commands travel over a network, either a **TCP socket** or **MQTT** (QoS 0 or 1 through
Mosquitto), to a simulated **Pioneer P3-DX** differential-drive robot. The robot executes them with
**PID control**, protects itself with an on-board **safety layer** (sonar obstacle stop, link-loss
watchdog, stale-command guard, MQTT Last Will), and streams **telemetry** back: pose, state, obstacle
distance and goal results.

The study compares TCP, MQTT QoS 0 and MQTT QoS 1 under emulated delay, jitter, packet loss and link
outages. It includes an operator-in-the-loop steering test that uses a synthetic driver model.

```
 operator shell ──TCP or MQTT──► [impairment proxy] ──► robot server (20 Hz) ──► mock P3-DX / CoppeliaSim
      ▲                                                    │ controller → safety → wheels
      └──────────── ack · result · telemetry (10 Hz) ◄─────┘
```

## Status: what is verified and what is not

| Part | Status |
|---|---|
| Mock backend (pure Python), TCP, MQTT QoS 0/1, shell, safety, proxy | **Tested**: 68 automated tests pass, MQTT tests run against Mosquitto 2.0.18 |
| Experiments, figures, tables (`results/`) | **Real runs on the mock backend**, labelled `backend: mock` everywhere |
| CoppeliaSim backend (`teleop/backends/coppelia.py`) | **Written but not run: to be verified on a real CoppeliaSim by the team** (see `docs/SCENE_SETUP.md`) |

## Quick start (mock robot, two terminals)

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# terminal 1: the robot
python -m teleop.server --backend mock --transport tcp --port 9000
# terminal 2: the operator
python -m teleop.cli --transport tcp --host 127.0.0.1 --port 9000
teleop> move 1
teleop> turn 90
teleop> goto 1 1
teleop> status
```

The full step-by-step guide for Windows, Linux and macOS covers the MQTT demo, the CoppeliaSim demo,
tests and experiments: **[docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md)**.

## Command language

| Command | Meaning |
|---|---|
| `move <dist> [speed]` | drive straight `dist` m (negative = back) at `speed` m/s (default 0.3) |
| `turn <deg> [rate]` | rotate in place (positive = left) at `rate` deg/s (default 60) |
| `goto <x> <y> [speed]` | drive to a world point (go-to-goal with heading PID) |
| `vel <v> <w>` | raw velocity: `v` m/s, `w` deg/s, held until changed or stopped |
| `stop` · `status` · `ping` · `reset` | stop, print telemetry, measure round trip, reset the simulation |
| shell only: `wait [s]` `watch [s]` `rtt [n]` `log start/stop` `macro <file>` `history` `help` `quit` | local helpers |

The wire format is described in [docs/PROTOCOL.md](docs/PROTOCOL.md).

## Folder structure

```
teleop/                 the Python package
  protocol.py           command parser + JSON message format             (Harsh)
  client.py, cli.py     operator API and interactive shell               (Harsh)
  transport/tcp.py      TCP socket transport                             (Harsh)
  transport/mqtt.py     MQTT transport, QoS, LWT, TCP_NODELAY            (Aniket)
  server.py             robot-side 20 Hz loop                            (Akshat)
  backends/mock.py      pure-Python P3-DX + room simulator               (Akshat)
  backends/coppelia.py  CoppeliaSim ZMQ Remote API backend (UNVERIFIED)  (Akshat)
  kinematics.py, pid.py, controller.py, safety.py                        (Priyam)
  netem.py              delay / jitter / loss / outage proxy             (Yeshang)
  config.py             every tunable number
experiments/            scenarios.py, run_experiments.py, analyze.py, pid_tuning.py (Yeshang; S0 by Aniket)
results/                raw CSVs, traces, tables, figures, summary.json (generated)
tests/                  pytest suite (MQTT tests skip without a broker)
macros/                 .tlm command files for the shell
config/mosquitto.conf   broker configuration
scenes/                 CoppeliaSim scene notes (the .ttt is made by the team)
report/                 build_report.py (Word + PDF), check_report.py, diagrams.py, output
docs/                   how to run, architecture, protocol, setup, troubleshooting, syllabus, novelty
docs/members/           one guide per team member (role, files, tasks, commit plan, viva Q&A)
docs/helpers/           slide outline, demo script, checklist, meeting log, peer sheet
scripts/git_author_stats.py   commits and files per author (report Section 10)
COMMIT_PLAN.md          ordered commit plan for all five members
```

## Main results (mock backend, 10 trials per cell)

Measured numbers are summarised in [docs/RESULTS.md](docs/RESULTS.md) and in the report (Section 9).
The tables are in `results/tables/` and the figures in `results/figures/`.

## Team

| Member | Package |
|---|---|
| Akshat Kumar Angi | Simulation: scene, backends, server loop; repo owner; meeting log |
| Harsh Varma | Operator side: protocol, TCP connection, shell; run documentation |
| Aniket Singh Bisht | MQTT transport, Mosquitto, latency TCP vs MQTT QoS 0/1, architecture diagram |
| Priyam Paliwal | Robot control: kinematics, PID, move/turn/goto, safety layer, tuning, live demo |
| Yeshang Soni | Network impairment, experiment runner, metrics, plots, results notes |
