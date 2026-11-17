# Syllabus mapping

> The official CSAI4014 unit numbers are not in our reference files. Each row names the topic as it is
> usually taught. **Before submission, the team writes the matching unit number from the official
> syllabus into the "Unit" column** (report Section 5 uses the same table).

| Topic | Unit | Where it is used | File / experiment |
|---|---|---|---|
| Mobile robot kinematics (differential drive, unicycle model, forward/inverse kinematics) | `<unit>` | wheel speeds ↔ (v, ω); exact arc integration of the pose | `kinematics.py`, `backends/mock.py` |
| Feedback control, PID, anti-windup, saturation | `<unit>` | heading PID for move/turn/goto; P-control on remaining distance; tuning study | `pid.py`, `controller.py`, `experiments/pid_tuning.py` |
| Motion primitives and go-to-goal / point stabilisation | `<unit>` | `goto` (heading PID plus cos² speed scaling) | `controller.py` |
| Path following (pure pursuit) | `<unit>` | synthetic operator model in S3 | `experiments/scenarios.py` (OperatorModel) |
| Robot sensors: range sensing (ultrasonic sonar), sensor noise | `<unit>` | 16-sonar ring, cone rays, Gaussian noise; obstacle distance | `backends/mock.py`, `safety.py` |
| Reactive / layered control architectures, behaviour priority | `<unit>` | safety layer overrides operator commands (obstacle stop, watchdog) | `safety.py`, `server.py` |
| Finite-state machines for robot behaviour | `<unit>` | IDLE / MOVING / OBSTACLE / LINK_LOST | `server.py` |
| Teleoperation, networked control, effect of delay | `<unit>` | supervisory (goto) versus direct (vel) control under delay, jitter, loss | S2, S3 |
| Robot communication and middleware (client-server, publish-subscribe, QoS) | `<unit>` | TCP sockets versus MQTT QoS 0/1, Last Will, retained messages | `transport/`, S0, S1, S4 |
| Fault tolerance and safety in robot systems | `<unit>` | watchdog, stale-command guard, exclusive control | S4, S5 |
| Robot simulation (CoppeliaSim, simulator-in-the-loop) | `<unit>` | mock simulator plus CoppeliaSim backend (ZMQ Remote API, stepping mode) | `backends/` |
| Experimental evaluation, metrics and statistics | `<unit>` | median, p95, mean ± sd, CDF over 10 trials per cell | `experiments/analyze.py` |
