# Yeshang Soni: Network impairment, experiment runner, metrics, plots, results notes

## 1. Your role in one paragraph
You own **the evidence**: the network-impairment proxy (delay, jitter, loss, outage), the experiment
runner that builds 550 independent trials, the metrics, the analysis script that turns raw CSVs into
tables and figures, and the results notes. If an examiner asks "how do you know?", your files answer it.

## 2. Files you own
| File | What it does |
|---|---|
| `teleop/netem.py` | TCP proxy that delays, jitters, retransmits ("loss") and cuts the link |
| `experiments/scenarios.py` | the 6 scenarios (S0-S5), one trial each, plus the synthetic operator model |
| `experiments/run_experiments.py` | builds the trial matrix and runs it in parallel processes |
| `experiments/analyze.py` | tables (`results/tables`) and figures (`results/figures`) |
| `results/` | all generated data |
| `docs/RESULTS.md` | results notes |

## 3. Everyday analogy
The proxy is a **slow, unreliable postman** who stands between operator and robot. You tell him:
"hold every letter for 100 ms, sometimes 125, sometimes 75 (jitter); and 1 time in 100 pretend you
dropped it, go back to the office and bring it 200 ms later (loss = retransmission)". For an outage
he locks the door for 3 s and throws away everything, then tears up both address books (connections
reset). The experiment runner is a **science-fair judge**: 10 repeats of every combination, same
rules for everybody, and every result written down.

## 4. How it works (one page)
```
             one trial (own process, own ports, own MQTT topics teleop/exp<id>/...)
 OperatorClient ──► ImpairmentProxy(port P) ──► RobotServer (TCP)  or  Mosquitto ──► RobotServer (MQTT)
                    each direction:
                      chunk arrives at t ──► release = max(t + N(delay, jitter), last_release)
                      with prob p: release += RTO (≥200 ms, doubles per repeat)      (TCP never reorders)
                      outage: drop chunks, then reset all connections

 matrix: transports {tcp, mqtt_q0, mqtt_q1} × conditions {C0 none, C1 50±10, C2 100±25+1 %, C3 200±50+5 %}
         × scenarios {S1 ping RTT, S2 goto square, S3 operator steering, S5 obstacle} × 10 trials
         + S4 outage (C1 only) + S0 Nagle ablation (4 combos)            = 550 trials, 16 in parallel
 metrics: RTT median/p95, completion time, goals reached + retries, RMS cross-track error,
          clearance, watchdog trips, commands lost / stale / executed late, collisions
```
Why model loss as delay? Both transports run on TCP, and TCP never loses data: a lost segment is resent
after a timeout. Dropping messages would have been unrealistic.

## 5. Five-minute manual test
```bash
tools/mosquitto/run_mosquitto.sh 1883                   # broker (or mosquitto -c config/mosquitto.conf)
python experiments/run_experiments.py --scenarios S1_latency S4_outage --trials 1 --workers 4
python experiments/analyze.py
```
Open `results/tables/T_latency.md`: C1 must be about 100 ms, C3 several hundred. Then run a proxy by hand
(`python -m teleop.netem --listen 9001 --target 127.0.0.1:9000 --delay 100`) and check `rtt` in the shell.
(The quick run overwrites S1/S4 CSVs. Re-run with `--trials 10` afterwards, or work on a branch.)

## 6. Task checklist
| Task | Done when |
|---|---|
| Re-run the full matrix on your own laptop | 550 trials, 0 failed; differences to the first run noted in RESULTS.md |
| 95 % bootstrap confidence intervals in the tables | tables regenerate with CI columns |
| `--rate-kbps` bandwidth limit in the proxy | test: 1 kB at 8 kbps takes about 1 s |
| netem tests (jitter statistics, refusal during outage) | pass |
| Watchdog-timeout sweep 0.5 / 1 / 2 s under C3 | figure + paragraph: fewer false trips vs longer coast |
| Score a real human run from a `log start` CSV | `experiments/score_human.py` works |
| Each member drives the S3 lane by hand under C0 and C2 | CSVs labelled `operator=human` |
| Report Sections 9, 12, Appendix | `check_report.py` passes |

## 7. Your commit plan
| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `exp/yeshang-rerun` | `exp: re-run full matrix on own laptop and compare with first run` | `results/`, `docs/RESULTS.md` | 0 failed trials |
| 2 | `feat/yeshang-ci` | `feat(exp): 95 % bootstrap confidence intervals in tables` | `experiments/analyze.py` | tables regenerate |
| 3 | `feat/yeshang-bandwidth` | `feat(netem): bandwidth limit option --rate-kbps` | `teleop/netem.py`, tests | new test |
| 4 | `test/yeshang-netem` | `test(netem): jitter statistics and connection refusal during outage` | `tests/test_netem.py` | pass |
| 5 | `exp/yeshang-watchdog-sweep` | `exp: watchdog timeout sweep 0.5/1/2 s under C3` | `experiments/scenarios.py`, results | 10 trials per value |
| 6 | `feat/yeshang-human-log` | `feat(exp): score a real human run from a 'log start' CSV` | `experiments/score_human.py` | works on a file |
| 7 | `exp/yeshang-human` | `exp: 5 members drive the S3 lane by hand under C0 and C2` | `results/raw/human_*.csv` | labelled human |
| 8 | `docs/yeshang-report` | `docs(report): write Sections 9, 12 and Appendix` | `report/content.py` | check_report passes |

## 8. Figures and evidence you produce
All `fig_*.png` except the PID figure, all `T_*` tables, `results/summary.json` (every number the
report quotes), `results/run_info.json`.

## 9. Report sections you write
**9 Results and Analysis**, **12 Conclusion and Future Scope**, **Appendix** (about 5 pages), plus
your row in Section 10, your reflection in Section 11 and your Declaration signature.

## 10. Likely viva questions
1. **Why not Linux `tc netem`?** It needs root and only works on Linux. Our proxy runs on every OS, is
   seeded (repeatable), and applies the same impairment to both transports. Limit: it works on data
   chunks, not real IP packets, and has no congestion window.
2. **How is loss modelled and why?** TCP retransmits lost segments, so the application sees delay, not
   loss. A "lost" chunk is released one RTO (≥ 200 ms, the Linux minimum) later, doubling for repeated
   losses, and nothing behind it may overtake it (head-of-line blocking).
3. **Why 10 trials, and what do the error bars show?** 10 per cell was the project requirement. Bars are
   mean ± one standard deviation. Box plots show all 500 pings per cell.
4. **How do you keep 16 parallel trials from disturbing each other?** Each trial has its own process,
   OS-assigned ports and MQTT topic prefix. The only shared parts are the broker and the CPU. CPU load can
   add a little timing noise, so the C0 results (1-2 ms) are the upper bound of local overhead.
5. **Why is the S3 operator a model, not a person?** So that 120 runs are repeatable and identical across
   transports. It is a pure-pursuit driver with 0.2 s reaction time. A real-human run is a planned task (commit 7).
6. **What is cross-track error?** The distance from the robot to the nearest point of the reference lane.
   We report its RMS over the run.
7. **What surprised you in the results?** Nagle: 55 ms vs 1.2 ms. QoS 1 replaying 150 commands after an
   outage. And how differently `goto` (+10-18 % time) and `vel` steering (5× error) react to the same link.
8. **Why were S2, S4 and S5 re-run?** S5 after the hysteresis fix. S2 after we made the operator re-send
   rejected goals (otherwise the script waited 60 s for a result that could never come). S4 after adding
   duplicate suppression. Its counts did not change. All re-runs are documented.
9. **Is any number from CoppeliaSim?** No. Every row says `backend=mock`. CoppeliaSim runs are Akshat's task 8.
10. **What would you add next?** Bandwidth limits, real Wi-Fi measurements, a watchdog sweep, and human operators.

## 11. Slides and demo part
* **Slides 13, 14 and 15** (Results 1, Results 2 and Comparison, Team Contribution).
* During the demo you can show the proxy: restart the shell through port 9001 and type `rtt 10`.

## 12. Small, safe extension tasks
confidence intervals, bandwidth limit, watchdog sweep, a scenario with two obstacles, and a
`--seed` flag for the whole run.
