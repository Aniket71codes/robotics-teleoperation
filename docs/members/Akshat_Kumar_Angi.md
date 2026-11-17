# Akshat Kumar Angi: Simulation, robot backends, server loop, repository

## 1. Your role in one paragraph
You own **the robot side**: the simulated robot (mock and CoppeliaSim), and the server loop that
connects network, controller, safety and robot 20 times a second. You also own the **GitHub
repository** (create it, add the team, protect `main`) and the **meeting log**. Your biggest open task
is to **verify the CoppeliaSim backend on a real CoppeliaSim**. It is written but has never been run.

## 2. Files you own
| File | What it does |
|---|---|
| `teleop/server.py` | the 20 Hz robot loop, command handling, watchdog trigger, telemetry |
| `teleop/backends/base.py` | the interface every robot backend implements |
| `teleop/backends/mock.py` | pure-Python P3-DX: kinematics, motor lag, 16 sonars, walls, collisions |
| `teleop/backends/coppelia.py` | CoppeliaSim backend over the ZMQ Remote API (**unverified**) |
| `teleop/config.py` (RobotParams, ServerParams) | robot geometry, loop rates |
| `scenes/` | the CoppeliaSim scene you will build |
| `docs/SCENE_SETUP.md`, `docs/helpers/MEETING_LOG.md` | scene guide + checklist, meeting log |

## 3. Everyday analogy
The server is a **restaurant kitchen's head chef**. Orders (commands) arrive on slips at any time,
but the chef works in fixed rounds: every 50 ms they collect the new slips, check that the waiter is
still there (watchdog), look at the stove (sensors), decide what to cook (controller), make sure nobody
gets burned (safety), cook one step (backend step) and call out what's ready (telemetry). The mock
backend is a **practice kitchen**; CoppeliaSim is the **real kitchen**. Same chef, same recipes, and only
the stove changes.

## 4. How it works (one page)
```
 network thread                        control thread (every 50 ms)
 ─────────────                         ──────────────────────────────────────────
 msg arrives ──► last_rx = now         1. take all msgs from inbox → validate → stale? → ack
   ping? → reply pong at once          2. silent > 1.0 s ?  → stop, LINK_LOST
   hb?   → done                        3. pose, sonars = backend.get_pose(), get_sonar()
   else  → inbox.put(msg) ─────────►   4. v, w = controller.step(pose)      (Priyam)
                                       5. v, w = safety.filter(v, w, sonar)  (Priyam)
                                       6. ramp v, w → wheel speeds → backend.set_wheel_speeds
                                       7. backend.step(0.05)   mock: integrate | Coppelia: sim.step()
                                       8. every 2nd tick: send telemetry
```
Why two threads? The network can deliver at any moment. The control loop must run at a steady rate.
A queue joins them, so only the control thread ever touches the robot, and no locks are needed.

**Mock backend in 4 lines:** wheel speed follows the command with a 0.08 s lag → (v, ω) from the wheel
speeds → pose moves along an exact arc → if the new pose overlaps a wall, it is blocked and counted as a
collision. Each sonar casts 3 rays over a 15° cone and reports the nearest hit (max 1.0 m) plus 5 mm noise.

## 5. Five-minute manual test
```bash
python -m teleop.server --backend mock --port 9000          # terminal 1
python -m teleop.cli --port 9000                             # terminal 2
teleop> status            # pose 0,0,0, IDLE
teleop> move 1            # result: reached, x ≈ 1.0
teleop> reset             # back to 0,0
teleop> vel 0.3 0         # then close terminal 2 with Ctrl+D
```
Terminal 1 must print `link lost (watchdog): stopping robot` about 1 s after you leave.
Then `python -m pytest tests/test_control_safety.py -k mock` → passes.

## 6. Task checklist
| Task | Done when |
|---|---|
| Create GitHub repo, add 4 collaborators, protect `main` | everyone can push a branch; `main` needs 1 approval |
| Import the scaffold as ONE neutral commit | `git log` shows a single `chore: import project scaffold` commit |
| Install CoppeliaSim, build the scene (SCENE_SETUP.md §2) | `scenes/teleop_p3dx.ttt` opens with the room and P3-DX, child script removed |
| Run the verification checklist (SCENE_SETUP.md §4) | all 11 rows have a result |
| Fix names/geometry found in the checklist | `move 1.0` within ±3 cm, `turn 90` within ±2° in CoppeliaSim |
| Run S2 and S5 on CoppeliaSim | `results/raw/*_coppeliasim.csv` exist, labelled `coppeliasim` |
| Keep the meeting log | one row per meeting, decisions recorded |
| Write report Abstract, 1, 2, References | `check_report.py` passes |

## 7. Your commit plan
| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `main` (setup) | `chore: import project scaffold (AI-assisted draft, see COMMIT_PLAN.md)` | everything | `pytest` green on a fresh clone |
| 2 | `feat/akshat-scene` | `feat(scene): add CoppeliaSim P3-DX scene matching the mock room` | `scenes/teleop_p3dx.ttt`, `scenes/README.md` | rows 1-2 of the checklist |
| 3 | `fix/akshat-coppelia-handles` | `fix(coppelia): use the object paths and API calls found in the real scene` | `teleop/backends/coppelia.py` | server prints "ready" with `--backend coppelia` |
| 4 | `fix/akshat-geometry` | `fix(config): set wheel radius and base measured in CoppeliaSim` | `teleop/config.py` | rows 5-6 |
| 5 | `test/akshat-coppelia-smoke` | `test(coppelia): smoke test that skips unless COPPELIA=1` | `tests/test_coppelia.py` | skips without CoppeliaSim |
| 6 | `feat/akshat-loop-rate` | `feat(server): report achieved loop rate and warn below 18 Hz` | `teleop/server.py`, tests | new test |
| 7 | `feat/akshat-exp-backend` | `feat(exp): --backend option so scenarios can run on CoppeliaSim` | `experiments/*.py` | mock runs unchanged |
| 8 | `exp/akshat-coppelia-runs` | `exp(coppelia): S2 and S5, 10 trials each, on CoppeliaSim` | `results/` | rows labelled `coppeliasim` |
| 9 | `docs/akshat-checklist` | `docs(scene): record verification checklist results and screenshots` | `docs/SCENE_SETUP.md` | all rows filled in |
| 10 | `docs/akshat-meetings` | `docs(log): meeting log entries 1-N` | `docs/helpers/MEETING_LOG.md` | complete |

Hint for #7: `experiments/scenarios.py` → `System.__init__` builds `MockBackend(...)`. Add a
`backend` field to `Trial`, and create `CoppeliaBackend()` when it is `"coppelia"`. Run with
`--workers 1` (one CoppeliaSim instance).

## 8. Figures and evidence you produce
* screenshots of the CoppeliaSim scene (report Figure in Section 8 and slide 8);
* the filled-in verification checklist;
* CoppeliaSim versions of the S2 and S5 tables, if you complete task 8.

## 9. Report sections you write
**Abstract, 1 Introduction, 2 Problem Statement and Objectives, References** (about 5 pages), plus
your row in Section 10, your reflection in Section 11 and your Declaration signature. The draft text is
in `report/content.py`. Rewrite it in your own words.

## 10. Likely viva questions
1. **Why does the server use a queue between the network thread and the control loop?** So that only
   one thread touches the controller and the robot. Commands can arrive at any time, but they are applied
   at the start of a tick, so the loop stays deterministic and needs no locks.
2. **Why is `ping` answered in the network thread?** Then ping RTT measures only the network. If it
   waited for the tick, every ping would include 0-50 ms of extra waiting.
3. **What happens if the loop falls behind?** It runs the next tick at once. If it is more than 0.5 s
   behind (laptop asleep), it resets its schedule instead of running many ticks in a burst.
4. **What does the mock model, and what does it not?** It models kinematics, first-order motor lag,
   cone sonars with noise, and collisions. It does not model wheel slip, inertia, or sonar cross-talk.
5. **Why stepping (synchronous) mode in CoppeliaSim?** The simulation advances only when we call
   `sim.step()`, so one server tick = one 50 ms sim step, exactly like the mock. Results are repeatable
   and the simulation never runs ahead of the controller.
6. **Why must the P3-DX child script be removed?** The stock model runs a Braitenberg obstacle-avoidance
   script that writes the motor speeds too. Two controllers would fight over the motors.
7. **How does the robot know its pose?** The mock knows the true pose. In CoppeliaSim we read the base
   pose with `sim.getObjectPosition/Orientation`, which is ground truth. A real robot would use odometry
   with drift. That is listed as future work.
8. **What is a collision in the mock?** The new pose's body circle (radius 0.26 m) would overlap a wall
   segment or cylinder. The move is refused for that step and counted. All 550 trials had 0.
9. **Why 20 Hz?** It matches CoppeliaSim's default 50 ms step. It is fast compared with the robot's
   dynamics (motor lag 0.08 s), and slow enough for Python and the network.
10. **How would you move this to a real P3-DX?** Write a third backend with the same 6 methods
    (e.g. through ROS 2 `cmd_vel` and the sonar topics). The server, controller, safety and network
    code do not change.

## 11. Slides and demo part
* **Slides 1, 2, 3 and 8** (Title, Problem and Motivation, Objectives, Robot and Environment Model).
* In the video you introduce the team and the problem (about 4 min). During the live demo, show the
  CoppeliaSim window if the backend is verified. Otherwise say clearly that the demo uses the mock robot.

## 12. Small, safe extension tasks
* print the achieved loop rate at shutdown (commit 6);
* add a second obstacle layout to `World` and a `--world` flag;
* add odometry noise to the mock (pose drift), then compare `goto` accuracy.
