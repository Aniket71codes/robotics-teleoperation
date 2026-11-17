# Priyam Paliwal: Robot control: kinematics, PID, move/turn/goto, safety layer, tuning, live demo

## 1. Your role in one paragraph
You own **how the robot moves and how it stays safe**: the differential-drive maths, the PID
controller, the four motion primitives (`move`, `turn`, `goto`, `vel`), the safety layer (obstacle
slow-down/stop with hysteresis, link watchdog, stale-command guard), the gain tuning study, and the
**live demo** in the video.

## 2. Files you own
| File | What it does |
|---|---|
| `teleop/kinematics.py` | wheel speeds ↔ (v, ω), exact arc integration, saturation, rate limit |
| `teleop/pid.py` | PID with anti-windup and output limit |
| `teleop/controller.py` | move / turn / goto / vel, results (reached, preempted, timeout, …) |
| `teleop/safety.py` | obstacle guard (+ hysteresis), watchdog check, stale check |
| `teleop/config.py` (ControlGains, SafetyParams) | gains and safety limits |
| `experiments/pid_tuning.py` | the tuning study |
| `tests/test_kinematics_pid.py`, `tests/test_control_safety.py` | tests |

## 3. Everyday analogy
Driving a car to a parking spot. **Kinematics** is knowing that turning the steering wheel left makes the
car curve left. **PID** is how you steer: P = "the further I'm off, the harder I turn"; D = "I'm coming back
fast, ease off before I overshoot"; I = "I keep drifting right, add a bit of constant left" (and if
you overdo I, you weave, which is what our tuning study shows). **goto** is "look at the spot, turn
towards it, drive slower as you get close". The **safety layer** is the car's automatic emergency
brake: whatever the driver says, it brakes before the wall, and if the driver faints (link lost),
it stops the car.

## 4. How it works (one page)
```
 differential drive:  v = r(ωR+ωL)/2      ω = r(ωR−ωL)/b      r = 0.0975 m, b = 0.331 m
                      ωL = (v − ωb/2)/r   ωR = (v + ωb/2)/r    (inverse, used every tick)

 move d:  travelled = (p − p0)·heading0 ;  v = clip(1.2·(d − travelled), ±speed)
          ω = PID(heading0 − θ)                          done: |remaining| < 3 cm for 0.15 s
 turn a:  ω = clip(PID(θ_target − θ), ±rate)              done: |error| < 1.5° for 0.15 s
 goto x,y: e = atan2(y−Y, x−X) − θ ;  ω = PID(e)
          v = min(speed, 1.2·dist) · max(0, cos e)²       (turn first, drive when facing goal)
 vel v,w: pass through (clamped: v ≤ 0.7, reverse ≤ 0.2 m/s, |ω| ≤ 2 rad/s)

 safety (every tick, after the controller):
   front sonar d:  d ≥ 0.8 → full speed ;  0.3 < d < 0.8 → scale (d−0.3)/0.5, min 0.05 m/s creep
                   d ≤ 0.3 → v = 0 (turning still allowed); stays blocked until d ≥ 0.35 (hysteresis)
   blocked > 2 s during move/goto → result "blocked"
   no message > 1 s → stop, LINK_LOST       motion command older than 1 s → rejected "stale"
```

## 5. Five-minute manual test
```bash
python -m teleop.server --port 9000
python -m teleop.cli --port 9000
teleop> turn 90          # result reached, error < 1.5 deg
teleop> goto 1 1         # result reached, error ≈ 3 cm
teleop> macro macros/safety_demo.tlm     # stops at obstacle 0.30 m, state OBSTACLE, no creeping
python experiments/pid_tuning.py          # prints the 5 gain sets
```

## 6. Task checklist
| Task | Done when |
|---|---|
| Re-run tuning; choose the heading Kd from the data (P Kp=3 settles in 1.38 s vs 1.67 s for the PD used in runs) | config changed or kept with a written reason; S2 re-run if changed |
| Fix the systematic 2.5-3 cm stop-short of move/goto | mean final error < 2 cm over 10 gotos, tests green |
| 20-random-goals test | passes |
| Optional final heading for goto | old commands unchanged |
| Rear-sonar and hysteresis tests | pass |
| Live demo rehearsed twice with a timer | under 6 minutes |
| Report Sections 5 and 7 | `check_report.py` passes |

## 7. Your commit plan
| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `exp/priyam-pid-default` | `exp(control): re-run tuning; choose heading Kd from data` | `teleop/config.py`, `results/` | tuning table supports the choice |
| 2 | `fix/priyam-goto-undershoot` | `fix(control): reduce systematic 2-3 cm stop-short in move/goto` | `controller.py`, `config.py` | mean final error < 2 cm |
| 3 | `test/priyam-goto-random` | `test(control): 20 random reachable goals are all reached` | `tests/test_control_safety.py` | passes |
| 4 | `feat/priyam-goto-heading` | `feat(control): optional final heading 'goto x y [speed] [theta]'` | `protocol.py`, `controller.py`, tests | old tests pass |
| 5 | `test/priyam-safety-rear` | `test(safety): rear sonar blocks reversing; hysteresis edges` | tests | pass |
| 6 | `feat/priyam-slow-turn` | `feat(safety): limit turn rate near obstacles` | `safety.py`, tests | S5 unchanged |
| 7 | `docs/priyam-demo` | `docs(demo): live demo runbook and fallback plan` | `docs/helpers/DEMO_SCRIPT.md` | rehearsed |
| 8 | `docs/priyam-report` | `docs(report): write Sections 5 and 7` | `report/content.py` | check_report passes |

Hint for #2: the stop-short happens because v = 1.2·remaining becomes tiny near the goal, and "done"
triggers at 3 cm. Try `pos_tolerance 0.015` with a minimum approach speed of 0.03 m/s. Check that
`test_move_reaches_distance` still passes.

## 8. Figures and evidence you produce
`fig_pid_step.png`, Table T_pid, `fig_safety.png`, Table T_safety, `diag_control_loop.png`,
`diag_states.png`, and the safety-demo transcript in HOW_TO_RUN.md.

## 9. Report sections you write
**5 Syllabus Mapping and Theory** and **7 Methodology and Algorithms** (about 5 pages), plus your row in
Section 10, your reflection in Section 11 and your Declaration signature. Fill the syllabus unit
numbers from the official syllabus.

## 10. Likely viva questions
1. **Derive v and ω from the wheel speeds.** Each wheel moves at r·ωwheel. The centre moves at the average,
   v = r(ωR+ωL)/2. The difference turns the robot about the axle, ω = r(ωR−ωL)/b.
2. **Why scale both wheels when one saturates?** It keeps the ratio ωR/ωL, so the robot follows the same
   arc, only slower. Clipping one wheel would change the curve.
3. **What do P, I and D each do, and why did you not use I?** P reacts to the present error, I to the
   accumulated past error, D to the trend. The heading loop has no steady disturbance, so I only caused
   wind-up: 7° overshoot, and only 4 of 10 turns settled.
4. **What is anti-windup?** Clamping the integral so it cannot grow huge while the output is saturated.
   Otherwise it overshoots badly when the error finally shrinks.
5. **Why cos² in goto?** If the goal is behind or beside the robot, driving forward would curve away.
   cos² gives full speed when facing the goal and zero at 90° or more, so the robot turns first.
6. **Why is the slow zone + creep + hysteresis needed?** Without slowing down, it would brake hard from
   full speed. Without creep, the linear slow-down approaches the stop line forever and never arrives.
   Without hysteresis, 5 mm sonar noise around 0.30 m makes it stop-go-stop (our regression test counts
   more than 5 toggles without it, and exactly 1 with it).
7. **Why is a late `stop` accepted but a late `move` rejected?** Executing an old motion command moves the
   robot based on old information, which is dangerous. Stopping late is always safe.
8. **Why did supervisory `goto` survive the bad network but `vel` steering did not?** `goto` closes the
   loop on the robot at 20 Hz, and only the goal crosses the network. With `vel`, the loop goes through the
   human and the network: the operator reacts to a pose that is 0.4-1 s old and over-corrects. RMS error
   was 4 cm vs 20-23 cm at C3.
9. **How fast does the robot stop after link loss?** The watchdog fires 1.0-1.1 s after the last message.
   The robot coasts about 25 cm at 0.25 m/s (S4).
10. **What limits the accuracy of turn and goto?** The 1.5° and 3 cm tolerances, the motor lag, and the
    approach speed. The measured final errors were 0.95° and 2.7 cm.

## 11. Slides and demo part
* **Slides 6, 10 and 12** (Syllabus Mapping, Controller Design/Tuning, Live Demonstration).
* You lead the **live demo** (about 6 min). Harsh types in the shell. Follow `docs/helpers/DEMO_SCRIPT.md`.

## 12. Small, safe extension tasks
final heading for goto, turn-rate limit near obstacles, speed-scheduled heading gain, and a figure-eight
path-following test.
