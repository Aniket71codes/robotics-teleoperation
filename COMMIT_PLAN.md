# Commit plan

**Rule:** every commit is made by the member who did the work, from their own GitHub account.
Nobody commits for anybody else, and no history is rewritten. The workflow is in
[docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).

**Starting point.** The project scaffold (code, tests, docs, first experiment results and report
draft) was generated with an AI assistant. **Akshat imports it once as a single neutral commit**,
`chore: import project scaffold`, and the commit message says where it came from. Every commit after
that is real work the member still has to do: verifying, extending, tuning, testing, re-running and
writing. The report's Contribution section must describe these commits, not the scaffold.

Each row below gives the branch, the Conventional-Commit message, the files touched and the check
that **must pass before you commit**. Reviewer pairs: Akshat→Priyam, Harsh→Aniket, Aniket→Harsh,
Priyam→Yeshang, Yeshang→Akshat.

Run `python -m pytest` before every commit. It is the minimum check for all rows.

---

## Akshat Kumar Angi: simulation, backends, server loop, repository

| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `main` (setup) | `chore: import project scaffold (AI-assisted draft, see COMMIT_PLAN.md)` | everything | `pytest` green on a fresh clone |
| 2 | `feat/akshat-scene` | `feat(scene): add CoppeliaSim P3-DX scene matching the mock room` | `scenes/teleop_p3dx.ttt`, `scenes/README.md` | scene opens; checklist rows 1-2 in SCENE_SETUP.md pass |
| 3 | `fix/akshat-coppelia-handles` | `fix(coppelia): use the object paths and API calls found in the real scene` | `teleop/backends/coppelia.py` | `python -m teleop.server --backend coppelia` prints "ready"; rows 3-4 pass |
| 4 | `fix/akshat-geometry` | `fix(config): set wheel radius and base measured in CoppeliaSim` | `teleop/config.py` | `move 1.0` within ±3 cm, `turn 90` within ±2° in CoppeliaSim (rows 5-6) |
| 5 | `test/akshat-coppelia-smoke` | `test(coppelia): smoke test that skips unless COPPELIA=1` | `tests/test_coppelia.py` | skips on CI; passes with CoppeliaSim open |
| 6 | `feat/akshat-loop-rate` | `feat(server): report achieved loop rate and warn below 18 Hz` | `teleop/server.py`, `tests/test_system_tcp.py` | new test asserts that the rate is reported |
| 7 | `feat/akshat-exp-backend` | `feat(exp): --backend option so scenarios can run on CoppeliaSim` | `experiments/scenarios.py`, `experiments/run_experiments.py` | `--scenarios S5_safety --trials 1 --backend mock` unchanged |
| 8 | `exp/akshat-coppelia-runs` | `exp(coppelia): S2 and S5, 10 trials each, on CoppeliaSim` | `results/raw/*_coppeliasim.csv`, figures | every row has `backend=coppeliasim` |
| 9 | `docs/akshat-checklist` | `docs(scene): record verification checklist results and screenshots` | `docs/SCENE_SETUP.md`, `docs/img/` | all 11 rows filled in |
| 10 | `docs/akshat-meetings` | `docs(log): meeting log entries 1-N` | `docs/helpers/MEETING_LOG.md` | dates, attendees and decisions filled in |

## Harsh Varma: protocol, TCP connection, shell, run documentation

| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `docs/harsh-run-verify` | `docs(run): verify HOW_TO_RUN on <your OS> and paste real output` | `docs/HOW_TO_RUN.md` | Demos A, B and C run exactly as written |
| 2 | `feat/harsh-tab-completion` | `feat(cli): tab-completion for command and macro names` | `teleop/cli.py` | manual: `mo<TAB>` → `move` |
| 3 | `test/harsh-cli` | `test(cli): parse errors, wait without goal, watch without telemetry, log usage` | `tests/test_cli.py` | new tests pass |
| 4 | `feat/harsh-macros` | `feat(macros): add figure_eight.tlm and patrol.tlm` | `macros/*.tlm`, `tests/test_cli.py` | test: every macro line parses |
| 5 | `feat/harsh-repeat` | `feat(cli): 'repeat <n> <command>' and '!<n>' history recall` | `teleop/cli.py`, `tests/test_cli.py` | tests for both |
| 6 | `feat/harsh-color` | `feat(cli): colour the state column; --no-color flag` | `teleop/cli.py` | output without colour unchanged (existing tests) |
| 7 | `feat/harsh-hello` | `feat(protocol): hello/version handshake on connect` | `teleop/protocol.py`, `client.py`, `server.py`, tests | old tests and a new mismatch test pass |
| 8 | `docs/harsh-report` | `docs(report): write Sections 6 and 8` | `report/content.py` (Sections 6, 8) | `python report/check_report.py` passes |

## Aniket Singh Bisht: MQTT, Mosquitto, latency, architecture diagram

| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `docs/aniket-mosquitto` | `docs(mqtt): verify Mosquitto install on <your OS>` | `docs/MQTT_SETUP.md` | `mosquitto_sub`/`pub` check works |
| 2 | `exp/aniket-nagle` | `exp(mqtt): re-run Nagle ablation S0 on own laptop` | `results/raw/S0_nagle_<name>.csv`, `docs/RESULTS.md` | 10 trials per combination |
| 3 | `test/aniket-qos1-outage` | `test(mqtt): QoS 1 commands queued in an outage are rejected as stale` | `tests/test_mqtt.py` | passes with broker; skips without |
| 4 | `feat/aniket-auth` | `feat(mqtt): username/password options and password_file docs` | `teleop/transport/mqtt.py`, `cli.py`, `server.py`, docs | test with a password-protected broker |
| 5 | `feat/aniket-tls` | `feat(mqtt): optional TLS on port 8883` | `teleop/transport/mqtt.py`, docs | manual test with a self-signed certificate |
| 6 | `exp/aniket-wifi` | `exp(net): real two-laptop Wi-Fi latency, TCP vs MQTT QoS 0/1` | `experiments/`, `results/raw/wifi_*.csv` | label `backend=mock, network=real Wi-Fi` |
| 7 | `docs/aniket-architecture` | `docs(arch): editable architecture diagram (draw.io) and export` | `docs/img/architecture.drawio`, `.png` | matches the code |
| 8 | `docs/aniket-report` | `docs(report): write Sections 3 and 4` | `report/content.py` (Sections 3, 4) | check_report passes |

## Priyam Paliwal: kinematics, PID, motion primitives, safety, demo

| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `exp/priyam-pid-default` | `exp(control): re-run tuning; choose heading Kd from data` | `teleop/config.py`, `results/` | tuning table shows the chosen set has the lowest settling time with no overshoot |
| 2 | `fix/priyam-goto-undershoot` | `fix(control): reduce systematic 2-3 cm stop-short in move/goto` | `teleop/controller.py`, `config.py` | `test_control_safety.py` passes; mean final error < 2 cm over 10 gotos |
| 3 | `test/priyam-goto-random` | `test(control): 20 random reachable goals are all reached` | `tests/test_control_safety.py` | new test passes |
| 4 | `feat/priyam-goto-heading` | `feat(control): optional final heading 'goto x y [speed] [theta]'` | `protocol.py`, `controller.py`, tests | old commands unchanged |
| 5 | `test/priyam-safety-rear` | `test(safety): rear sonar blocks reversing; hysteresis edges` | `tests/test_control_safety.py` | new tests pass |
| 6 | `feat/priyam-slow-turn` | `feat(safety): limit turn rate near obstacles` | `teleop/safety.py`, tests | S5 clearance unchanged |
| 7 | `docs/priyam-demo` | `docs(demo): live demo runbook and fallback plan` | `docs/helpers/DEMO_SCRIPT.md` | rehearsed once with a timer |
| 8 | `docs/priyam-report` | `docs(report): write Sections 5 and 7` | `report/content.py` (Sections 5, 7) | check_report passes |

## Yeshang Soni: impairment, experiments, metrics, plots

| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `exp/yeshang-rerun` | `exp: re-run full matrix on own laptop and compare with first run` | `results/`, `docs/RESULTS.md` | 550 trials, 0 failures |
| 2 | `feat/yeshang-ci` | `feat(exp): 95 % bootstrap confidence intervals in tables` | `experiments/analyze.py` | tables regenerate |
| 3 | `feat/yeshang-bandwidth` | `feat(netem): bandwidth limit option --rate-kbps` | `teleop/netem.py`, `tests/test_system_tcp.py` | new test: 1 kB at 8 kbps takes ≈ 1 s |
| 4 | `test/yeshang-netem` | `test(netem): jitter statistics and connection refusal during outage` | `tests/test_netem.py` | new tests pass |
| 5 | `exp/yeshang-watchdog-sweep` | `exp: watchdog timeout sweep 0.5/1/2 s under C3` | `experiments/scenarios.py`, results | 10 trials per value |
| 6 | `feat/yeshang-human-log` | `feat(exp): score a real human run from a 'log start' CSV` | `experiments/score_human.py` | works on a recorded file |
| 7 | `exp/yeshang-human` | `exp: 5 members drive the S3 lane by hand under C0 and C2` | `results/raw/human_*.csv` | labelled `operator=human` |
| 8 | `docs/yeshang-report` | `docs(report): write Sections 9, 12 and Appendix` | `report/content.py` | check_report passes |
