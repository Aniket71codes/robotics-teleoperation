"""Text of the project report.

Each member edits the sections they write (see the Writing Allocation).  Markup
understood by build_report.py inside any text:

    {cite:key}  or {cite:a,b}   -> [n] / [n], [m]   (numbered by first citation)
    {fig:key}                   -> Figure n
    {tab:key}                   -> Table n
    {eq:key}                    -> (n)
    **bold**                    -> bold run

Every measured number is read from results/summary.json or results/tables, so
the report always matches the data.  All of it comes from the MOCK backend.
"""

from __future__ import annotations

import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "results", "figures")
S = json.load(open(os.path.join(ROOT, "results", "summary.json")))


def tab_csv(name, cols=None):
    with open(os.path.join(ROOT, "results", "tables", name + ".csv")) as fh:
        rows = list(csv.reader(fh))
    if cols is None:
        return rows[0], rows[1:]
    idx = [rows[0].index(c) for c in cols]
    return [rows[0][i] for i in idx], [[r[i] for i in idx] for r in rows[1:]]


def f1(x):
    return f"{x:.1f}"


TR = ["tcp", "mqtt_q0", "mqtt_q1"]
TN = {"tcp": "TCP", "mqtt_q0": "MQTT QoS 0", "mqtt_q1": "MQTT QoS 1"}

# ------------------------------------------------------------------ metadata (placeholders!)
META = {
    "title": "Networked Teleoperation of a Robot through Shell Commands",
    "project_no": "<Project No.>",
    "group_no": "<Group No.>",
    "batch": "B3-B4",
    "members": [("Akshat Kumar Angi", "<SAP ID>"), ("Harsh Varma", "<SAP ID>"),
                ("Aniket Singh Bisht", "<SAP ID>"), ("Priyam Paliwal", "<SAP ID>"),
                ("Yeshang Soni", "<SAP ID>")],
    "github": "https://github.com/<group-repository>",
    "youtube": "https://youtu.be/<video-id>",
}

# ------------------------------------------------------------------ references (IEEE)
REFS = {
    "sheridan": 'T. B. Sheridan, Telerobotics, Automation, and Human Supervisory Control. Cambridge, MA, USA: MIT Press, 1992.',
    "ferrell": 'W. R. Ferrell, "Remote manipulation with transmission delay," IEEE Transactions on Human Factors in Electronics, vol. HFE-6, no. 1, pp. 24-32, 1965.',
    "niemeyer": 'G. Niemeyer and J.-J. E. Slotine, "Telemanipulation with time delays," The International Journal of Robotics Research, vol. 23, no. 9, pp. 873-890, 2004.',
    "mqtt": 'A. Banks and R. Gupta, Eds., MQTT Version 3.1.1, OASIS Standard, Oct. 2014.',
    "mqtt5": 'A. Banks, E. Briggs, K. Borgendale, and R. Gupta, Eds., MQTT Version 5.0, OASIS Standard, Mar. 2019.',
    "mosquitto": 'R. A. Light, "Mosquitto: server and client implementation of the MQTT protocol," Journal of Open Source Software, vol. 2, no. 13, p. 265, 2017.',
    "ros": 'M. Quigley, K. Conley, B. Gerkey, J. Faust, T. Foote, J. Leibs, R. Wheeler, and A. Y. Ng, "ROS: an open-source Robot Operating System," in Proc. ICRA Workshop on Open Source Software, Kobe, Japan, 2009.',
    "thangavel": 'D. Thangavel, X. Ma, A. Valera, H.-X. Tan, and C. K.-Y. Tan, "Performance evaluation of MQTT and CoAP via a common middleware," in Proc. IEEE 9th Int. Conf. Intelligent Sensors, Sensor Networks and Information Processing (ISSNIP), Singapore, 2014.',
    "tcp": 'J. Postel, "Transmission Control Protocol," RFC 793, Internet Engineering Task Force, Sep. 1981.',
    "nagle": 'J. Nagle, "Congestion control in IP/TCP internetworks," RFC 896, Internet Engineering Task Force, Jan. 1984.',
    "rto": 'V. Paxson, M. Allman, J. Chu, and M. Sargent, "Computing TCP\'s retransmission timer," RFC 6298, Internet Engineering Task Force, Jun. 2011.',
    "vrep": 'E. Rohmer, S. P. N. Singh, and M. Freese, "V-REP: a versatile and scalable robot simulation framework," in Proc. IEEE/RSJ Int. Conf. Intelligent Robots and Systems (IROS), Tokyo, Japan, 2013, pp. 1321-1326.',
    "netem": 'S. Hemminger, "Network emulation with NetEm," in Proc. Linux Conference Australia (linux.conf.au), Canberra, Australia, 2005.',
    "brooks": 'R. A. Brooks, "A robust layered control system for a mobile robot," IEEE Journal on Robotics and Automation, vol. 2, no. 1, pp. 14-23, 1986.',
    "siegwart": 'R. Siegwart, I. R. Nourbakhsh, and D. Scaramuzza, Introduction to Autonomous Mobile Robots, 2nd ed. Cambridge, MA, USA: MIT Press, 2011.',
    "astrom": 'K. J. Åström and R. M. Murray, Feedback Systems: An Introduction for Scientists and Engineers. Princeton, NJ, USA: Princeton University Press, 2008.',
    "siciliano": 'B. Siciliano and O. Khatib, Eds., Springer Handbook of Robotics, 2nd ed. Cham, Switzerland: Springer, 2016.',
    "coulter": 'R. C. Coulter, "Implementation of the pure pursuit path tracking algorithm," Robotics Institute, Carnegie Mellon University, Pittsburgh, PA, USA, Tech. Rep. CMU-RI-TR-92-01, 1992.',
    "zmq": 'Coppelia Robotics, "ZeroMQ remote API," CoppeliaSim User Manual. [Online]. Available: https://manual.coppeliarobotics.com/',
}

# ------------------------------------------------------------------ numbers used in the text
nag_def, nag_fix = S["S0|False|False"]["median"], S["S0|True|True"]["median"]
nag_one = (S["S0|False|True"]["median"], S["S0|True|False"]["median"])
s2_extra = {t: (S[f"S2|{t}|C3_200ms_5pct"]["time"] / S[f"S2|{t}|C0_ideal"]["time"] - 1) * 100 for t in TR}
s3_c3 = {t: S[f"S3|{t}|C3_200ms_5pct"] for t in TR}
s3_c0 = S["S3|tcp|C0_ideal"]
s4 = {t: S[f"S4|{t}"] for t in TR}
s5_min = min(S[f"S5|{t}|{c}"]["min"] for t in TR for c in ("C0_ideal", "C1_50ms", "C2_100ms_1pct", "C3_200ms_5pct"))
s5_wd = sum(10 - S[f"S5|{t}|C3_200ms_5pct"]["stopped_at_box"] for t in TR)
up = {t: S[f"S1|{t}|C0_ideal"]["up"] for t in TR}
xte_ratio = min(s3_c3[t]["xte"] for t in TR) / s3_c0["xte"]

ABSTRACT = (
    "Robots in warehouses, hospitals and inspection sites are often driven remotely over networks that add "
    "delay, jitter and loss. This project builds a teleoperation system in which an operator types shell "
    "commands (move, turn, goto, vel, stop, status, ping, reset) that travel over a TCP socket or over MQTT "
    "(QoS 0 or 1) to a simulated Pioneer P3-DX differential-drive robot. The robot executes "
    "them with PID motion primitives and protects itself with an on-board safety layer: a sonar obstacle stop, "
    "a one-second link watchdog and a stale-command guard. A reproducible impairment proxy emulated four "
    "network conditions, up to 200 ± 50 ms delay with 5 % loss, and 550 trials (10 per cell) were run on a "
    "mock simulator; a CoppeliaSim backend was written but is not yet verified. Supervisory goto "
    f"commands reached all 480 goals with 2.7 cm error and at most {max(s2_extra.values()):.0f} % extra time, "
    "whereas direct velocity steering by a synthetic operator lost accuracy "
    f"{xte_ratio:.0f}-fold on the worst link. The novelty includes a measured Nagle pitfall (QoS 1 round trip "
    f"{nag_def:.1f} ms with default settings, {nag_fix:.1f} ms when fixed), evidence that QoS 1 replays stale "
    "commands after an outage, and zero collisions in all trials."
)
KEYWORDS = "teleoperation, MQTT, TCP, network delay, PID control, differential drive, safety watchdog, CoppeliaSim."

# ------------------------------------------------------------------ the body
# Block types: ("h1", text) ("h2", text) ("p", text) ("bullets", [..]) ("numbered", [..])
# ("fig", key, file, caption, width_cm) ("table", key, caption, header, rows, widths_cm)
# ("eq", key, latex) ("code", [lines]) ("pagebreak",)

BODY = []
add = BODY.append

# ================================================================== 1
add(("h1", "1. Introduction"))
add(("h2", "1.1 Background"))
add(("p", "A teleoperated robot is a machine that does the physical work in one place while a person decides "
          "what it should do from another place. The idea is old: the first master-slave manipulators were built "
          "to handle radioactive material behind a wall, and Sheridan's classic text describes how the human, "
          "the communication channel and the remote machine form one control loop {cite:sheridan}. When the "
          "channel adds delay, this loop changes character. Ferrell showed already in 1965 that operators who see "
          "the result of their action late fall back to a slow \"move and wait\" strategy {cite:ferrell}, and "
          "later work on bilateral telemanipulation showed that delay can even make the closed loop unstable "
          "{cite:niemeyer}."))
add(("p", "Today the channel is usually an ordinary computer network: Wi-Fi in a warehouse, a 4G/5G link to "
          "an inspection robot, or the Internet between a hospital and a remote expert. Such networks do not "
          "give a fixed delay. They add jitter (the delay changes from packet to packet), lose packets that "
          "then have to be retransmitted, and sometimes drop the connection completely for a few seconds. A "
          "teleoperation system therefore has to answer two practical questions. First, how should commands be "
          "carried, as a direct TCP connection or through a publish/subscribe broker such as MQTT "
          "{cite:mqtt}? Second, what should the robot do when the commands arrive late, twice, or not at all?"))
add(("h2", "1.2 Why it matters in industry"))
add(("p", "Remote operation is used where sending a person is slow, expensive or dangerous: nuclear and "
          "chemical plants, pipeline and tunnel inspection, mining, agriculture, and the remote assistance of "
          "autonomous delivery robots that get stuck. In logistics, a single operator often supervises a whole "
          "fleet and only steps in when a robot asks for help. MQTT is popular in these settings because one "
          "broker connects many robots, dashboards and loggers, and because of features such as retained status "
          "messages and the \"Last Will\" that reports a client that vanished {cite:mqtt,mosquitto}. Robot "
          "software stacks such as ROS also use publish/subscribe {cite:ros}. Engineers choosing between these "
          "options need numbers, not only feature lists: what does each option cost in latency and bandwidth, "
          "and how does it behave when the network fails?"))
add(("p", "Safety is the second industrial concern. A robot must never depend on the operator's \"stop\" "
          "arriving in time. Industrial practice therefore puts the last line of defence on the robot itself: "
          "protective stops from range sensors, and a communication watchdog that stops the machine when the "
          "control link is silent for too long. This project builds both into the robot and measures whether "
          "they work the same way for every transport."))
add(("h2", "1.3 Scope of this report"))
add(("p", "We built a complete teleoperation chain in Python: an operator shell with its own small command "
          "language, two interchangeable transports (TCP socket and MQTT with QoS 0 or 1), a robot server with "
          "PID motion primitives and a safety layer, a pure-Python simulator of a Pioneer P3-DX, and a "
          "CoppeliaSim backend for the real simulator. A network-impairment proxy lets us repeat the same delay, "
          "jitter, loss and outage for every transport. The report follows the order of the course "
          "template: the problem and objectives (Section 2), related work (Section 3), what is new (Section 4), "
          "theory (Section 5), design (Section 6), algorithms (Section 7), set-up (Section 8), results "
          "(Section 9), and the team's contribution and learning (Sections 10 and 11). All measured results were "
          "produced with the mock simulator. The CoppeliaSim backend is written but still has to be verified by "
          "the team, and we state this wherever it matters."))

# ================================================================== 2
add(("h1", "2. Problem Statement and Objectives"))
add(("h2", "2.1 Problem statement"))
add(("p", "Design and evaluate a system in which an operator drives a simulated differential-drive robot by "
          "typing shell commands that travel over a network, such that (a) the robot executes the commands "
          "accurately, (b) the robot stays safe when the network is slow, lossy or disconnected, and (c) the "
          "effect of the transport (TCP socket, MQTT QoS 0, MQTT QoS 1) and of the network quality on latency, "
          "task performance and safety is measured under identical, repeatable conditions."))
add(("h2", "2.2 Objectives"))
add(("numbered", [
    "Implement a command language with eight commands (move, turn, goto, vel, stop, status, ping, reset) and "
    "an operator shell with history, macros, wait, watch and telemetry logging.",
    "Implement two interchangeable transports, a TCP socket and MQTT with QoS 0 and QoS 1, and measure their "
    "round-trip time and byte overhead under four network conditions (10 trials each).",
    "Implement PID-based motion primitives that reach a commanded goal within 5 cm and 2°.",
    "Implement an on-robot safety layer that keeps a clearance of at least 25 cm to obstacles and stops the "
    "robot within 1.5 s of a link failure, with zero collisions in all trials.",
    "Compare supervisory control (goto) with direct control (vel) under the same network conditions, "
    "including an operator-in-the-loop steering test, and analyse the behaviour during a 3 s outage.",
]))
add(("h2", "2.3 Assumptions and limits"))
add(("bullets", [
    "Flat floor and static obstacles; the robot pose is known (simulator ground truth, no localisation error).",
    "One operator controls one robot at a time; operator and robot clocks are synchronised (needed by the "
    "stale-command check; on one PC this is automatic).",
    "Network impairments are emulated on the operator's link by our proxy, on one PC; loss is modelled as TCP "
    "retransmission delay, because both transports run over TCP.",
    "The operator in the steering test is a deterministic model (pure pursuit with 0.2 s reaction time), not a "
    "human; human trials are planned work.",
    "All reported numbers come from the mock simulator; the CoppeliaSim backend is not yet verified.",
]))

# ================================================================== 3
add(("h1", "3. Literature and Industry Review"))
add(("h2", "3.1 Teleoperation under delay"))
add(("p", "Sheridan introduced the term supervisory control for systems in which the human gives goals and "
          "the remote machine closes the low-level loop itself {cite:sheridan}. This contrasts with direct "
          "(manual) control, where every motion of the joystick is copied to the robot. Ferrell's experiments "
          "with delayed remote manipulation showed that operators compensate for delay by making a move and "
          "waiting to see the result, which makes the task several times slower {cite:ferrell}. Niemeyer and "
          "Slotine studied force-reflecting telemanipulation with time delay and showed how passivity-based "
          "wave variables keep the loop stable {cite:niemeyer}. Our robot has no force feedback, so the stability "
          "problem is milder. The practical lesson for us is the same, though: the longer and more variable the "
          "delay, the more of the control loop should run on the robot."))
add(("h2", "3.2 Communication middleware for robots"))
add(("p", "TCP gives a reliable, ordered byte stream between two end points {cite:tcp}. Reliability comes from "
          "retransmission: a lost segment is sent again after a retransmission timeout (RTO), which by the "
          "standard is at least one second and in Linux practice at least 200 ms {cite:rto}. Two TCP details "
          "matter for small control messages. Data that is never lost can still arrive late, because a lost "
          "segment blocks everything behind it (head-of-line blocking). And Nagle's algorithm delays small "
          "packets to merge them {cite:nagle}. MQTT is a lightweight publish/subscribe protocol on top of TCP, "
          "standardised by OASIS {cite:mqtt}. Clients publish to topics on a broker. QoS 0 delivers at most "
          "once, QoS 1 at least once with an acknowledgement (PUBACK), and QoS 2 exactly once with a four-step "
          "handshake. Mosquitto is a widely used open-source broker {cite:mosquitto}. ROS uses its own "
          "publish/subscribe transport and is the most common robot middleware in research {cite:ros}. "
          "Thangavel et al. compared MQTT with CoAP through a common middleware under emulated loss and found "
          "that the better protocol depends on the loss rate and message size {cite:thangavel}. Such studies "
          "measure messages, not robot tasks."))
add(("p", "Version 5.0 of MQTT added features that touch the problems studied here {cite:mqtt5}. A publisher "
          "can attach a Message Expiry Interval, after which the broker discards a message that it has not yet "
          "delivered, and a session expiry that limits how long the broker keeps state for a disconnected "
          "client. These features act inside the broker. A message that waits in the publishing client's own "
          "queue, or arrives just before it expires, still reaches the robot late. Our work uses MQTT 3.1.1, the "
          "version most often deployed on small robots and in the paho client defaults, and puts the age check "
          "on the robot, where it covers every path a late command can take."))
add(("h2", "3.3 Industry practice"))
add(("p", "Commercial remote-operation systems follow a common pattern even where their details are not "
          "published. Mobile robots in warehouses and hospitals run their own navigation and obstacle "
          "avoidance, and a remote operator gives goals or approves an action instead of steering continuously. "
          "Remote assistance for autonomous vehicles works the same way: the human chooses a path or confirms a "
          "manoeuvre, and the vehicle executes it with its own controllers. Robot drivers commonly stop the "
          "motors when no velocity command has arrived for a short time, which is the same idea as our link "
          "watchdog. On the communication side, MQTT is widely used for fleet telemetry and dashboards because "
          "one broker serves many robots and clients, while direct sockets or ROS topics carry the low-latency "
          "control traffic. The open question for a designer is where to draw the line between the two, and how "
          "each behaves when the network degrades. Answering it needs repeatable measurements on one software "
          "stack, which is the approach taken in this project."))
add(("h2", "3.4 Simulation and network emulation"))
add(("p", "CoppeliaSim (formerly V-REP) is a robot simulator with a distributed control architecture and "
          "many ready-made robot models, including the Pioneer P3-DX used here {cite:vrep}. Its ZeroMQ remote "
          "API lets an external Python program step the simulation synchronously {cite:zmq}. For networks, Linux "
          "offers NetEm, a kernel queueing discipline that adds delay, jitter, loss and reordering to real "
          "packets {cite:netem}. It needs administrator rights and works only on Linux, which is why we wrote a "
          "portable user-space proxy with the same parameters (Section 7)."))
add(("h2", "3.5 Comparison and gap"))
add(("p", "{tab:lit} summarises the approaches. Two gaps remain for a small teleoperated robot. First, "
          "transport comparisons usually stop at message latency and do not show what happens to the robot's "
          "task or safety. Second, the behaviour during an outage, when an \"at least once\" protocol delivers "
          "a backlog of old motion commands, is rarely measured. This project addresses both gaps with one "
          "software stack and one repeatable impairment model."))
add(("table", "lit", "Comparison of existing approaches",
     ["Approach", "Strength", "Limitation"],
     [["Direct control (joystick copy) {cite:sheridan,ferrell}", "Simple, intuitive", "Degrades sharply with delay"],
      ["Supervisory control {cite:sheridan}", "Robust to delay", "Needs on-robot autonomy"],
      ["Raw TCP socket {cite:tcp}", "Lowest overhead, ordered", "Point-to-point; no queueing or status"],
      ["MQTT broker {cite:mqtt,mosquitto}", "Fleet-friendly, LWT, QoS", "Extra hop; QoS 1 can replay old data"],
      ["Message-level MQTT studies {cite:thangavel}", "Quantify latency/loss", "No robot task or safety metrics"],
      ["Kernel NetEm emulation {cite:netem}", "Packet-level, realistic", "Linux and root only"]],
     [5.2, 4.2, 5.6]))

# ================================================================== 4
add(("h1", "4. Novelty"))
add(("p", "The following points are new compared with the textbook examples and the studies in Section 3. "
          "Each is supported by our own measurements in Section 9 (mock backend, 10 trials per cell)."))
add(("numbered", [
    "**One robot stack, three transports, one impairment model.** TCP, MQTT QoS 0 and MQTT QoS 1 drive the "
    "same server, controller and safety layer through the same seeded delay/jitter/loss/outage proxy. The "
    "comparison covers task outcomes (goal time, tracking error, commands lost or replayed), not only "
    "latency: 550 trials in six scenarios (Section 9).",
    f"**A measured Nagle pitfall for robot MQTT.** With the default settings of paho-mqtt and Mosquitto, every "
    f"QoS 1 round trip took {nag_def:.1f} ms on a single PC. Fixing only one side gave {nag_one[0]:.1f} ms or "
    f"{nag_one[1]:.1f} ms. Switching Nagle off on both sides gave {nag_fix:.1f} ms ({{tab:nagle}}).",
    f"**\"At least once\" is unsafe for motion without a staleness guard.** After a 3 s outage, QoS 1 delivered "
    f"all {s4['mqtt_q1']['during']:.0f} queued velocity commands. Our robot-side age check rejected "
    f"{s4['mqtt_q1']['stale']:.0f} of them, and only the {s4['mqtt_q1']['late']:.0f} sent in the last second "
    f"were executed. TCP and QoS 0 lost all of them ({{tab:outage}}).",
    f"**Supervisory versus direct control under identical impairments, with an operator-in-the-loop model.** "
    f"goto reached all 480 goals with unchanged 2.7 cm accuracy and at most {max(s2_extra.values()):.0f} % "
    f"extra time on the worst link. Pure-pursuit steering through vel commands had about {xte_ratio:.0f} "
    f"times larger tracking error, and only {min(s3_c3[t]['finished'] for t in TR)}-"
    f"{max(s3_c3[t]['finished'] for t in TR)} of 10 runs finished ({{tab:square}}, {{tab:operator}}).",
    f"**Network-independent on-robot safety, verified across transports.** The obstacle guard (with "
    f"hysteresis against sonar chatter) and the 1 s watchdog behaved the same for every transport: zero "
    f"collisions in 550 trials, closest approach {s5_min:.1f} cm for a 30 cm stop distance, and a stop "
    f"{min(s4[t]['stop'] for t in TR):.2f}-{max(s4[t]['stop'] for t in TR):.2f} s after a link failure "
    f"({{tab:safety}}).",
]))

add(("p", "**Why these points matter.** Points 2 and 3 are practical warnings for anyone who builds a robot on "
          "MQTT. The default libraries add a latency that nobody asked for, and the \"reliable\" QoS level "
          "delivers commands that are no longer valid. Both are invisible in a quick test on a good network and "
          "only show up when they are measured. Point 4 turns the textbook advice of supervisory control "
          "{cite:sheridan} into numbers for this robot and these links: how much a goal-level command loses "
          "(time, not accuracy) and how much direct steering loses (accuracy, completion and time). Point 5 shows "
          "that the safety mechanisms do not depend on which transport the team chooses, so the transport can be "
          "chosen for latency, bandwidth and fleet features alone."))
add(("p", "**What is not new.** The individual building blocks are standard: differential-drive kinematics, "
          "PID control, pure pursuit, TCP sockets, MQTT and a watchdog are all textbook material. The "
          "contribution is the combination into one tested stack, the repeatable side-by-side measurement under "
          "identical impairments, and the specific findings listed above, each backed by our own data in "
          "Section 9."))

# ================================================================== 5
add(("h1", "5. Syllabus Mapping and Theory"))
add(("h2", "5.1 Syllabus topics used"))
add(("p", "{tab:syllabus} lists the course topics used in the project and where each one appears. The unit "
          "numbers are to be filled in from the official CSAI4014 syllabus."))
add(("table", "syllabus", "AISR syllabus topics used in this project",
     ["Syllabus topic", "Unit", "Where it is used"],
     [["Mobile robot kinematics (differential drive)", "<unit>", "kinematics.py; mock simulator"],
      ["Feedback control: PID, saturation, anti-windup", "<unit>", "pid.py, controller.py; tuning study"],
      ["Go-to-goal control and path following", "<unit>", "goto primitive; pure-pursuit operator model"],
      ["Range sensors (sonar) and noise", "<unit>", "16-sonar model; obstacle guard"],
      ["Reactive and layered architectures", "<unit>", "safety layer overrides operator commands"],
      ["Finite-state machines", "<unit>", "IDLE / MOVING / OBSTACLE / LINK_LOST"],
      ["Robot communication, client-server and publish-subscribe", "<unit>", "TCP and MQTT transports"],
      ["Teleoperation and networked control", "<unit>", "supervisory vs direct control (S2, S3)"],
      ["Robot simulation", "<unit>", "mock backend; CoppeliaSim ZMQ backend"]],
     [7.0, 1.6, 6.4]))
add(("h2", "5.2 Differential-drive kinematics"))
add(("p", "The P3-DX has two driven wheels of radius r on one axle of length b (wheel base) and a passive "
          "caster, the most common wheeled mobile-robot layout {cite:siciliano}. If the wheels turn at angular speeds ωL and ωR, the forward speed v and turn rate ω of the "
          "robot follow from {eq:fk}, and the controller uses the inverse {eq:ik} every tick {cite:siegwart}. "
          "With r = 0.0975 m and b = 0.331 m, a wheel limit of 12 rad/s corresponds to about 1.17 m/s. When a "
          "command would exceed it, both wheel speeds are scaled by the same factor, so the robot keeps the same "
          "curvature."))
add(("eq", "fk", r"v = \frac{r(\omega_R+\omega_L)}{2}, \qquad \omega = \frac{r(\omega_R-\omega_L)}{b}"))
add(("eq", "ik", r"\omega_L = \frac{v-\omega b/2}{r}, \qquad \omega_R = \frac{v+\omega b/2}{r}"))
add(("p", "The pose (x, y, θ) is advanced with the exact solution for constant v and ω over one step Δt "
          "{eq:arc}. The robot moves on a circle of radius v/ω, and on a straight line when ω = 0. This is "
          "more accurate than the simple Euler update when the robot turns."))
add(("eq", "arc", r"x' = x + \frac{v}{\omega}\left[\sin(\theta+\omega\Delta t)-\sin\theta\right],\;\; "
                  r"y' = y - \frac{v}{\omega}\left[\cos(\theta+\omega\Delta t)-\cos\theta\right],\;\; "
                  r"\theta' = \theta+\omega\Delta t"))
add(("h2", "5.3 PID control"))
add(("p", "Heading is controlled by a PID controller {eq:pid} {cite:astrom}. The error e is the wrapped "
          "difference between the target heading and the current heading. The integral is clamped (anti-windup) "
          "and the output is limited to the robot's maximum turn rate. For move and goto the forward speed is a "
          "proportional law on the remaining distance d, v = min(vmax, Kd·d) with Kd = 1.2 per second, so the robot "
          "slows down smoothly at the goal."))
add(("eq", "pid", r"u(t) = K_p\,e(t) + K_i\int_0^t e(\tau)\,d\tau + K_d\,\frac{de(t)}{dt}"))
add(("h2", "5.4 Go-to-goal and pure pursuit"))
add(("p", "For goto, the heading error is e = atan2(yg − y, xg − x) − θ. The forward speed is multiplied by "
          "max(0, cos e)², so the robot turns on the spot while the goal is beside or behind it, and drives at "
          "full speed only when it faces the goal {eq:goto}. The synthetic operator in the steering experiment "
          "uses pure pursuit {cite:coulter}: it picks a look-ahead point at distance L on the reference lane and "
          "commands the curvature that leads there {eq:pp}, where α is the angle to the look-ahead point."))
add(("eq", "goto", r"\omega = \mathrm{PID}(e), \qquad v = \min(v_{max},\,K_d\,d)\,\max(0,\cos e)^2"))
add(("eq", "pp", r"\omega = \frac{2\,v\,\sin\alpha}{L}"))
add(("h2", "5.5 Network delay model"))
add(("p", "With a one-way delay D, jitter σ and the same impairment in both directions, a request/reply "
          "round trip takes about 2D plus the processing time. A segment that is lost is delivered after a "
          "retransmission timeout, RTO = max(200 ms, 2D + 4σ) in our model, doubling for every further loss "
          "of the same segment, following the structure of RFC 6298 {cite:rto}. Because TCP delivers bytes "
          "in order, every message behind a delayed segment waits as well. This head-of-line blocking produces "
          "the long tails seen in Section 9."))

# ================================================================== 6
add(("h1", "6. System Design"))
add(("h2", "6.1 Architecture"))
add(("p", "{fig:arch} shows the complete system. On the operator PC, the shell turns typed lines into "
          "commands, and the operator client gives each command a sequence number and a session id, sends it, "
          "and matches the replies. The command crosses the network either directly over TCP or through the "
          "Mosquitto broker. In the experiments the impairment proxy sits on this link. On the robot side, the "
          "transport server puts incoming messages into a queue. The robot server takes them out once per "
          "control tick, the motion controller computes (v, ω), the safety layer may reduce or block it, and "
          "the backend moves the robot, either the mock simulator or CoppeliaSim. Telemetry, acknowledgements "
          "and results travel back the same way."))
add(("fig", "arch", "diag_architecture.png", "System architecture of the teleoperation chain", 13.5))
add(("h2", "6.2 Robot and environment model"))
add(("p", "The robot is a Pioneer P3-DX: a differential-drive base with a ring of 16 ultrasonic sonars, "
          "eight facing forward and eight backward. {tab:robot} lists the parameters used by both backends. The "
          "mock environment is a 7 m × 6 m room with a 0.6 m box 3.9 m in front of the start pose and a "
          "cylinder near one wall. The same layout is described for CoppeliaSim in the scene guide. The mock "
          "simulates first-order motor lag (each wheel follows its command with a 0.08 s time constant), "
          "exact arc integration, collisions, and sonars as three rays over a 15° cone with 5 mm Gaussian noise."))
add(("table", "robot", "Robot, sensor and control parameters",
     ["Parameter", "Value", "Parameter", "Value"],
     [["Wheel radius r", "0.0975 m", "Control / sim step", "50 ms (20 Hz)"],
      ["Wheel base b", "0.331 m", "Telemetry rate", "10 Hz"],
      ["Body radius", "0.26 m", "Max forward / reverse", "0.7 / 0.2 m/s"],
      ["Wheel speed limit", "12 rad/s", "Max turn rate", "2 rad/s"],
      ["Motor time constant", "0.08 s", "Accel. limit v / ω", "1.0 m/s² / 4 rad/s²"],
      ["Sonars", "16, range 1.0 m", "Heading PID Kp / Ki / Kd", "3.0 / 0 / 0.15"],
      ["Stop / slow distance", "0.30 / 0.80 m", "Watchdog timeout", "1.0 s"],
      ["Release margin", "0.05 m", "Max command age", "1.0 s"]],
     [4.0, 3.4, 4.4, 3.2]))
add(("h2", "6.3 Command language and messages"))
add(("p", "{tab:commands} defines the eight robot commands. Every argument is a number. The parser rejects "
          "unknown commands, missing or non-numeric arguments, and non-positive speeds with a clear message, "
          "and the robot reuses exactly the same parser to validate what it receives. On the wire each command "
          "is one JSON object such as {\"type\":\"cmd\",\"seq\":7,\"sid\":\"3fa2c1d0\",\"t\":…,\"cmd\":\"goto\","
          "\"args\":{\"x\":1,\"y\":1,\"speed\":0.3}}. The robot answers with an ack (accepted or rejected with "
          "a reason), a pong for ping, a result when a goal finishes (reached, stopped, preempted, blocked, "
          "link_lost or timeout), and telemetry at 10 Hz. {fig:seq} shows one goto exchange."))
add(("table", "commands", "Command language",
     ["Command", "Arguments (default)", "Meaning"],
     [["move", "dist [speed=0.3]", "drive straight dist metres (negative = back)"],
      ["turn", "angle [rate=60]", "rotate in place, degrees (+ = left)"],
      ["goto", "x y [speed=0.3]", "drive to a world point"],
      ["vel", "v w", "raw velocity, m/s and deg/s, held until replaced"],
      ["stop / status", "-", "stop at once / reply with telemetry"],
      ["ping / reset", "-", "round-trip check / reset simulation"]],
     [2.6, 4.2, 8.2]))
add(("fig", "seq", "diag_sequence.png", "Message sequence for one goto command", 11.0))
add(("h2", "6.4 Transports"))
add(("p", "**TCP.** The robot listens on port 9000. Messages are newline-delimited JSON, because TCP is a byte "
          "stream and one read may return half a message or several. TCP_NODELAY is set on both ends. Only "
          "one operator has control at a time: a second operator is refused with an error unless the first has "
          "been silent for more than one second. The client reconnects automatically every 0.25 s after a drop."))
add(("p", "**MQTT.** Robot and operator both connect to the broker and use the topics in {tab:topics}. With "
          "QoS 1 both use a persistent session, so the broker and the client library keep messages across a "
          "reconnect. Each side registers a retained Last Will (\"offline\"), and the robot stops as soon as the "
          "operator's will is published. Because paho-mqtt does not disable Nagle's algorithm, our transport "
          "sets TCP_NODELAY on its socket, and the broker is configured with set_tcp_nodelay true."))
add(("p", "**Error handling on both sides.** Every message is checked twice: the operator's parser refuses a "
          "malformed line before anything is sent, and the robot validates again, because a buggy or "
          "malicious client could send anything. A line longer than 64 KiB is discarded, so a client that "
          "never sends a newline cannot exhaust the robot's memory. Invalid JSON, unknown commands, missing "
          "arguments and a non-integer sequence number are answered with ok = false and a reason, and never "
          "reach the controller. A new motion command pre-empts the running one, and the old goal receives the "
          "result \"preempted\", so the operator always learns how every command ended. Pressing Ctrl+C in the "
          "shell sends stop instead of quitting, because an operator who panics presses Ctrl+C."))
add(("table", "topics", "MQTT topics (robot id p3dx)",
     ["Topic", "Direction", "Content"],
     [["teleop/p3dx/cmd", "operator → robot", "commands and heartbeats"],
      ["teleop/p3dx/telem", "robot → operator", "telemetry, 10 Hz"],
      ["teleop/p3dx/event", "robot → operator", "ack, pong, result"],
      ["teleop/p3dx/status", "robot → all (retained)", "online / offline (Last Will)"],
      ["teleop/p3dx/operator", "operator → robot (retained)", "online / offline (Last Will)"]],
     [4.6, 4.6, 5.8]))
add(("h2", "6.5 Software structure"))
add(("p", "The Python package teleop has one module per concern: protocol, client and cli (operator side), "
          "transport/tcp and transport/mqtt, server, controller, pid, kinematics, safety, backends/mock and "
          "backends/coppelia, and netem. Two small abstract interfaces decouple the parts. A RobotBackend has "
          "six methods (reset, set_wheel_speeds, step, get_pose, get_sonar, get_wheel_speeds), and a transport "
          "has start/connect, send and close. Changing from mock to CoppeliaSim or from TCP to MQTT is a "
          "command-line flag. All tunable numbers are in one configuration file."))
add(("p", "The repository contains 68 automated tests (pytest). They cover four levels: unit tests of the "
          "kinematics, PID, parser and line framing; closed-loop tests of the controller and the safety layer "
          "on the mock robot (for example, that a robot driven at a wall stops between 20 and 35 cm from it, and "
          "that hysteresis removes stop/go chatter); end-to-end tests over real TCP sockets (stale commands, "
          "duplicates, watchdog, exclusive control, proxy delay, loss and outage); and MQTT tests for QoS 0 "
          "and QoS 1 against a real Mosquitto broker, including the Last Will. The MQTT tests skip "
          "automatically when no broker is running, so the suite also works on a laptop without Mosquitto."))

# ================================================================== 7
add(("h1", "7. Methodology and Algorithms"))
add(("h2", "7.1 The robot control loop"))
add(("p", "The robot server runs a fixed-rate loop at 20 Hz ({fig:loop}). A network thread receives messages "
          "at any time and only places them in a queue. A ping is answered directly from the network thread, so "
          "the measured round trip contains no waiting for the next tick. All other processing happens in the "
          "control thread, which is the only thread that touches the controller and the robot, so no locks are "
          "needed. If the loop falls more than 0.5 s behind schedule (for example after the computer slept), it "
          "resynchronises instead of running a burst of ticks."))
add(("fig", "loop", "diag_control_loop.png", "One tick of the 20 Hz robot control loop", 8.0))
add(("p", "The command handling at the start of each tick follows this pseudo-code:"))
add(("code", [
    "for msg in inbox:",
    "    args = validate(msg)                  # same parser as the operator; else ack(ok=false)",
    "    if (msg.sid, msg.seq) already seen:   # MQTT QoS 1 may deliver twice",
    "        ack(ok=true, 'duplicate ignored'); continue",
    "    if msg.cmd is motion and now - msg.t > 1.0 s:",
    "        ack(ok=false, 'stale'); continue  # a late STOP is always accepted",
    "    if msg.cmd == stop:   result(cancel('stopped'))",
    "    elif motion command:  result(controller.start(msg))   # old goal -> 'preempted'",
    "    ack(ok=true)",
    "if now - last_message > 1.0 s:  stop robot; state = LINK_LOST; result('link_lost')",
]))
add(("h2", "7.2 Motion primitives"))
add(("p", "move keeps the starting heading with the heading PID and measures progress as the projection of the "
          "displacement on that heading. turn computes a target heading once and drives the wrapped error to "
          "zero, limited to the requested rate. goto uses the go-to-goal law {eq:goto} with the goal recomputed "
          "every tick, so a robot pushed off course still arrives. A goal is reached when the error stays "
          "inside 3 cm (or 1.5° for turn) for 0.15 s. Each goal has a timeout of twice its nominal duration "
          "plus a margin. Speeding up is limited to 1 m/s², but slowing down is immediate, so a stop is never "
          "delayed by the ramp."))
add(("code", [
    "goto(xg, yg, vmax):",
    "  every 50 ms:",
    "    d = |(xg, yg) - (x, y)|;  e = wrap(atan2(yg - y, xg - x) - θ)",
    "    if d < 3 cm for 0.15 s: return 'reached'",
    "    ω = PID(e)                        (clipped to ±2 rad/s)",
    "    v = min(vmax, 1.2 d) · max(0, cos e)^2",
    "    (v, ω) -> safety -> ramp -> wheel speeds",
]))
add(("h2", "7.3 Safety layer and robot states"))
add(("p", "The safety layer runs after the controller and can only reduce motion. This is the layered idea "
          "of Brooks, where a lower, simpler layer can override a higher one {cite:brooks}. When moving forward it "
          "looks at the four front sonars (±10° and ±30°). Below 0.80 m it scales the speed linearly down to "
          "zero at 0.30 m, keeping a minimum creep of 0.05 m/s so that the robot really reaches the stop line "
          "instead of approaching it forever. At 0.30 m forward motion is blocked, but turning on the spot is "
          "still allowed so the operator can steer away. The block is released only when the obstacle is 5 cm "
          "further away (hysteresis). Without this, 5 mm of sonar noise around the stop line made the robot "
          "stop and start repeatedly: our regression test counts more than five stop/go toggles in 25 s without "
          "hysteresis and exactly one with it. A move or goto that stays blocked for 2 s is aborted with the "
          "result \"blocked\". Reversing is checked the same way with the rear sonars. {fig:states} shows the "
          "resulting states."))
add(("fig", "states", "diag_states.png", "Robot states and transitions", 11.0))
add(("h2", "7.4 Controller tuning"))
add(("p", f"The heading gains were tuned on the mock robot with the same acceleration limit as the server. "
          f"Each gain set turned to ten target angles between 30° and 165° ({{fig:pid}}, {{tab:pid}}). A high "
          f"gain (Kp = 8) overshoots by about {S['PID|P Kp=8.0']['overshoot']:.0f}°, because the motor lag delays "
          f"the response. Adding an integral term (Ki = 1) causes wind-up: "
          f"{S['PID|PID Kp=3 Ki=1 Kd=0.15']['overshoot']:.1f}° overshoot, and only "
          f"{S['PID|PID Kp=3 Ki=1 Kd=0.15']['reached']} of 10 turns settle inside the tolerance. The heading "
          f"loop has no constant disturbance, so it does not need an integral. Proportional control with Kp = 3 "
          f"settled fastest ({S['PID|P Kp=3.0']['settle']:.2f} s). The PD set used in all network experiments "
          f"(Kp = 3, Kd = 0.15) also has no overshoot but settles in {S['PID|PD Kp=3.0 Kd=0.15']['settle']:.2f} s. "
          f"Re-checking this default is an open tuning task."))
add(("fig", "pid", "fig_pid_step.png", "Heading step response for a 90° turn with five gain sets", 10.5))
hdr, rows = tab_csv("T_pid", ["Gain set", "Mean overshoot (deg)", "Mean settling time to ±2 deg (s)",
                              "Mean final error (deg)", "Reached"])
add(("table", "pid", "Heading PID tuning over ten turns per gain set (mock)",
     ["Gain set", "Overshoot (°)", "Settling (s)", "Final error (°)", "Reached"], rows, [5.4, 2.4, 2.4, 2.6, 2.2]))
add(("h2", "7.5 Network impairment proxy"))
add(("p", "The proxy accepts the operator's TCP connection and opens its own connection to the robot server or "
          "the broker. Each direction has a reader that timestamps every received chunk and a writer that "
          "releases it at max(arrival + N(D, σ), previous release), so bytes are never reordered, as in real "
          "TCP. With probability p a chunk is \"lost\" and its release is postponed by one RTO, doubling for each "
          "repeated loss (Section 5.5). An outage discards all data for its duration and then resets every "
          "connection, which forces the clients to reconnect. The random generator is seeded per trial, so "
          "runs can be repeated. Because the proxy works on the operator's link only, MQTT traffic between the "
          "broker and the robot is unimpaired, which matches a robot that has the broker on board or nearby."))
add(("h2", "7.6 Synthetic operator model"))
add(("p", "To test direct control repeatably we replaced the human with a model. Every 0.2 s it takes the "
          "most recent robot pose it has received in telemetry and that is at least 0.2 s old (a human reaction "
          "time). It then computes a pure-pursuit command {eq:pp} towards a point 0.5 m ahead on an L-shaped "
          "7 m lane, at 0.35 m/s, and sends it as a vel command. If the look-ahead point is more than 60° off, "
          "it turns on the spot. The model therefore sees the world late by the network delay plus its own "
          "reaction time, as a human watching a video feed would."))

# ================================================================== 8
add(("h1", "8. Simulation Setup"))
add(("h2", "8.1 Platform and tools"))
add(("p", "All experiments ran on one Linux x86_64 PC with Python 3.12.3, paho-mqtt 2.2.0 and Mosquitto "
          "2.0.18, with 16 trials in parallel worker processes. The robot was the pure-Python mock simulator "
          "described in Section 6.2. The CoppeliaSim backend uses the ZeroMQ remote API in stepping mode, so one "
          "server tick equals one 50 ms simulation step {cite:zmq}. It has been written against the documented "
          "API but not yet run on a real CoppeliaSim. The verification checklist is part of the project "
          "documentation. No number in this report comes from CoppeliaSim."))
add(("h2", "8.2 Network conditions"))
add(("p", "{tab:conditions} lists the four emulated conditions. The delay is one-way and applies in each "
          "direction, so a round trip adds roughly twice the value. C3 represents a poor cellular or congested "
          "Wi-Fi link."))
add(("table", "conditions", "Emulated network conditions (operator link, each direction)",
     ["Condition", "Delay", "Jitter (σ)", "Segment loss", "Typical example"],
     [["C0", "0 ms", "0 ms", "0 %", "same PC / wired LAN"],
      ["C1", "50 ms", "10 ms", "0 %", "good Wi-Fi or regional Internet"],
      ["C2", "100 ms", "25 ms", "1 %", "busy Wi-Fi, long-distance Internet"],
      ["C3", "200 ms", "50 ms", "5 %", "poor cellular link"]],
     [2.2, 2.0, 2.2, 2.6, 6.0]))
add(("h2", "8.3 Scenarios and metrics"))
add(("p", "{tab:scenarios} lists the six scenarios. Every scenario was run with the three transports, and S1, "
          "S2, S3 and S5 under all four conditions, 10 trials per combination: 550 trials in total. Each trial "
          "starts its own robot server, proxy and client on private ports and private MQTT topics, so parallel "
          "trials do not interfere. Two scenarios were re-run after changes found during the work: S5 after the "
          "hysteresis fix (Section 7.3), and S2 after the operator was made to re-send a goal rejected as stale "
          "(without that, one trial waited 60 s for a result that could never come). S4 was re-run after "
          "duplicate suppression was added, and its counts did not change."))
add(("table", "scenarios", "Experiment scenarios",
     ["ID", "Scenario", "Main metrics"],
     [["S0", "Nagle ablation: MQTT QoS 1, TCP_NODELAY on/off on broker and client, C0", "median RTT"],
      ["S1", "50 pings at 5 Hz", "RTT median / p95 / max; bytes per second"],
      ["S2", "goto around a 2 m square (4 goals, 0.4 m/s)", "time, goals reached, re-sent goals, error"],
      ["S3", "synthetic operator steers an L-shaped lane with vel", "finished, time, RMS cross-track error"],
      ["S4", "3 s outage while driving with vel (C1)", "stop delay, coast, commands lost / stale / late"],
      ["S5", "drive at a box with vel 0.5, never send stop", "clearance at stop, collisions"]],
     [1.2, 8.6, 5.2]))
add(("h2", "8.4 Reproducibility and outputs"))
add(("p", "Every trial records its scenario, backend, transport, condition and trial number in the result row, "
          "so no figure can be mistaken for a CoppeliaSim result. Raw rows are written to results/raw (one CSV "
          "file per scenario plus every individual ping), the trajectory of the first trial of each cell to "
          "results/traces, summary tables to results/tables, figures to results/figures, and the date, "
          "software versions and network conditions of each run to results/run_info.json. The proxy's random "
          "generator is seeded with the trial id. The whole result set can therefore be regenerated with two "
          "commands, and a member can re-run a single scenario on their own laptop to compare."))
add(("h2", "8.5 How to run"))
add(("p", "The project README and the run guide give the commands for Windows, Linux and macOS. The basic "
          "two-terminal demonstration is:"))
add(("code", [
    "# terminal 1 (robot) and terminal 2 (operator):",
    "python -m teleop.server --backend mock --transport tcp --port 9000",
    "python -m teleop.cli --transport tcp --host 127.0.0.1 --port 9000",
    "teleop> move 1          teleop> turn 90          teleop> goto 1 1          teleop> status",
    "",
    "mosquitto -c config/mosquitto.conf          # MQTT variant",
    "python -m teleop.server --transport mqtt --qos 1",
    "python -m teleop.cli --transport mqtt --qos 1",
    "",
    "python experiments/run_experiments.py --trials 10    # all scenarios, then:",
    "python experiments/analyze.py                         # tables and figures in results/",
]))

# ================================================================== 9
add(("h1", "9. Results and Analysis"))
add(("p", "All results in this section were produced with the mock backend. Error bars and ± values are one "
          "standard deviation over 10 trials."))
add(("h2", "9.1 Nagle's algorithm and MQTT"))
add(("p", f"Early tests showed QoS 1 round trips of about 40 ms on a single PC, against 1 ms for QoS 0. The "
          f"ablation in {{fig:nagle}} and {{tab:nagle}} explains why. paho-mqtt does not set TCP_NODELAY, and "
          f"Mosquitto's set_tcp_nodelay is off by default. A small QoS 1 packet then waits until the previous "
          f"packet is acknowledged, while the receiver delays its ACK {{cite:nagle}}. With both defaults the "
          f"median was {nag_def:.1f} ms. Fixing either side alone still left about {nag_one[0]:.0f} ms. Only "
          f"fixing both reduced it to {nag_fix:.1f} ms. All later experiments use the fixed configuration."))
add(("fig", "nagle", "fig_nagle.png", "Median MQTT QoS 1 round trip with Nagle on or off at each side", 9.0))
hdr, rows = tab_csv("T_nagle")
add(("table", "nagle", "Nagle ablation, 10 trials × 30 pings per row (mock)",
     ["Broker NODELAY", "Client NODELAY", "Trials", "Median RTT (ms)", "Mean max RTT (ms)"],
     rows, [3.4, 3.6, 1.6, 3.6, 2.8]))
add(("h2", "9.2 Round-trip latency"))
add(("p", f"{{fig:rtt}} and {{tab:latency}} summarise 6000 pings. Without impairment TCP is fastest "
          f"(median {S['S1|tcp|C0_ideal']['median']:.1f} ms) because MQTT adds the broker hop "
          f"({S['S1|mqtt_q0|C0_ideal']['median']:.1f} ms for QoS 0, {S['S1|mqtt_q1|C0_ideal']['median']:.1f} ms "
          f"for QoS 1). Under real delay this difference disappears: at C1 all three are close to the expected "
          f"100 ms. Loss changes the picture. At C3 the medians are {S['S1|tcp|C3_200ms_5pct']['median']:.0f}, "
          f"{S['S1|mqtt_q0|C3_200ms_5pct']['median']:.0f} and {S['S1|mqtt_q1|C3_200ms_5pct']['median']:.0f} ms, "
          f"and the 95th percentiles reach {S['S1|tcp|C3_200ms_5pct']['p95']:.0f}, "
          f"{S['S1|mqtt_q0|C3_200ms_5pct']['p95']:.0f} and {S['S1|mqtt_q1|C3_200ms_5pct']['p95']:.0f} ms "
          f"({{fig:cdf}}). QoS 1 has the longest tail because its PUBACK packets travel in the same lossy, "
          f"ordered stream and add head-of-line blocking. MQTT also costs bandwidth: the uplink carried "
          f"{up['tcp']:.0f}, {up['mqtt_q0']:.0f} and {up['mqtt_q1']:.0f} B/s at C0, which is "
          f"{(up['mqtt_q0'] / up['tcp'] - 1) * 100:.0f} % and {(up['mqtt_q1'] / up['tcp'] - 1) * 100:.0f} % more "
          f"than TCP for the same commands and heartbeats. Only one ping out of 6000 went unanswered within 5 s."))
add(("fig", "rtt", "fig_rtt_box.png", "Ping round-trip time per transport and network condition", 12.0))
add(("fig", "cdf", "fig_rtt_cdf.png", "Distribution of round-trip times under loss (C2, C3)", 11.5))
rows = []
for c, cl in (("C0_ideal", "C0"), ("C1_50ms", "C1"), ("C2_100ms_1pct", "C2"), ("C3_200ms_5pct", "C3")):
    for t in TR:
        d = S[f"S1|{t}|{c}"]
        rows.append([cl, TN[t], f1(d["median"]), f1(d["p95"]), f1(d["max"]), f"{d['up']:.0f}"])
add(("table", "latency", "Ping round-trip time, 10 trials × 50 pings per row (mock)",
     ["Cond.", "Transport", "Median (ms)", "P95 (ms)", "Max (ms)", "Uplink (B/s)"], rows,
     [1.6, 3.4, 2.5, 2.5, 2.5, 2.5]))
add(("h2", "9.3 Supervisory control with goto"))
add(("p", f"In S2 the operator sent four goto goals around a 2 m square. Every one of the 480 goals was "
          f"reached ({{tab:square}}), with the same 2.7 cm mean final error and the same 7.96 m path length "
          f"under every condition. The control loop runs on the robot, so the network can only delay "
          f"the start of each goal; it cannot disturb the motion. On the worst link the square took "
          f"{s2_extra['tcp']:.0f} % (TCP), {s2_extra['mqtt_q0']:.0f} % (QoS 0) and {s2_extra['mqtt_q1']:.0f} % "
          f"(QoS 1) longer ({{fig:sqtime}}). The extra time for QoS 1 comes mostly from re-sent goals: at C3, "
          f"{S['S2|mqtt_q1|C3_200ms_5pct']['retries']:.0f} goals were rejected as stale or aborted by the "
          f"watchdog and had to be sent again, against {S['S2|tcp|C3_200ms_5pct']['retries']:.0f} for TCP. "
          f"The queued QoS 1 retransmissions made the gaps between heartbeats longer than the 1 s watchdog "
          f"more often."))
add(("fig", "sqtime", "fig_square_time.png", "Time for the four-goal square (supervisory control)", 11.0))
hdr, rows = tab_csv("T_square", ["Transport", "Condition", "Completion (s)", "Goals reached", "First try",
                                 "Re-sent goals", "Watchdog trips"])
rows = [[r[0].replace("TCP socket", "TCP"), r[1].split(":")[0]] + r[2:] for r in rows]
add(("table", "square", "Supervisory control: goto square, 10 trials per row (mock)",
     ["Transport", "Cond.", "Time (s)", "Reached", "First try", "Re-sent", "Watchdog"], rows,
     [3.0, 1.4, 2.8, 1.9, 1.9, 1.8, 2.0]))
add(("h2", "9.4 Direct control: operator-in-the-loop steering"))
add(("p", f"In S3 the synthetic operator steered the robot along the lane with vel commands. Up to C2 the "
          f"network made almost no difference: the RMS cross-track error stayed between 3.6 and 4.1 cm and the "
          f"run took about 22 s ({{fig:opbars}}, {{tab:operator}}). At C3 direct control broke down. The RMS "
          f"error grew to {min(s3_c3[t]['xte'] for t in TR):.0f}-{max(s3_c3[t]['xte'] for t in TR):.0f} cm, "
          f"the robot weaved around the lane ({{fig:oppath}}), and only {s3_c3['tcp']['finished']} (TCP), "
          f"{s3_c3['mqtt_q0']['finished']} (QoS 0) and {s3_c3['mqtt_q1']['finished']} (QoS 1) of 10 runs "
          f"finished within 60 s. Two effects add up. The operator corrects based on a pose that is half a "
          f"second or more old and over-steers. And the safety mechanisms intervene: "
          f"{s3_c3['tcp']['stale']:.0f}-{s3_c3['mqtt_q1']['stale']:.0f} late vel commands per ten runs were "
          f"rejected as stale, and the watchdog stopped the robot {s3_c3['tcp']['link_lost']:.0f}-"
          f"{s3_c3['mqtt_q1']['link_lost']:.0f} times. Comparing Sections 9.3 and 9.4 gives the main design "
          f"lesson: on a poor link, send goals, not joystick values."))
add(("fig", "opbars", "fig_operator_bars.png", "Direct steering: tracking error and completion time", 12.0))
hdr, rows = tab_csv("T_operator", ["Transport", "Condition", "Finished", "Time (s)", "RMS XTE (cm)",
                                   "Stale rejected", "Watchdog trips"])
rows = [[r[0].replace("TCP socket", "TCP"), r[1].split(":")[0]] + r[2:] for r in rows]
add(("table", "operator", "Direct steering by the synthetic operator, 10 trials per row (mock)",
     ["Transport", "Cond.", "Finished", "Time (s)", "RMS XTE (cm)", "Stale", "Watchdog"], rows,
     [3.0, 1.4, 1.9, 2.7, 2.9, 1.5, 1.9]))
add(("fig", "oppath", "fig_operator_paths.png", "Paths of the steered robot under C0-C3 (TCP, trial 0)", 6.8))
add(("h2", "9.5 Link outage"))
add(("p", f"In S4 the link failed for 3 s while the operator was holding vel 0.25. For every transport the "
          f"watchdog stopped the robot {min(s4[t]['stop'] for t in TR):.2f}-{max(s4[t]['stop'] for t in TR):.2f} s "
          f"after the failure, after about {s4['tcp']['coast'] * 100:.0f} cm of coasting ({{fig:outage}}, "
          f"{{tab:outage}}). The transports differ in what happens to the 150 commands sent during the outage. "
          f"TCP and QoS 0 lost all of them: TCP wrote them into a connection that was already dead, and paho "
          f"dropped the QoS 0 messages. QoS 1 kept them and delivered all of them after reconnecting, together "
          f"with every ping. The robot's age check rejected {s4['mqtt_q1']['stale']:.0f}, and the "
          f"{s4['mqtt_q1']['late']:.0f} sent in the last second before the link returned were executed. Without "
          f"the check, QoS 1 would have replayed three seconds of old commands. All transports resumed driving "
          f"about a third of a second after the link came back."))
add(("fig", "outage", "fig_outage_timeline.png", "Robot speed around a 3 s link outage", 11.0))
hdr, rows = tab_csv("T_outage", ["Transport", "Stop after outage start (s)", "Coast (cm)", "Lost",
                                 "Rejected stale", "Executed late", "Pings answered late"])
rows = [[r[0].replace("TCP socket", "TCP")] + r[1:] for r in rows]
add(("table", "outage", "Behaviour during a 3 s outage, 10 trials per row, 150 commands sent (mock)",
     ["Transport", "Stop (s)", "Coast (cm)", "Lost", "Stale", "Late", "Pings late"], rows,
     [3.0, 2.6, 2.0, 1.6, 1.6, 1.6, 2.2]))
add(("h2", "9.6 Obstacle safety"))
add(("p", f"In S5 the operator drove straight at the box at 0.5 m/s and never sent stop. There were no "
          f"collisions in 120 runs. Every robot that reached the box stopped between {s5_min:.1f} and 30.2 cm "
          f"from it, for a stop distance of 30 cm, independent of transport and network ({{fig:safety}}, "
          f"{{tab:safety}}). In {s5_wd} runs at C3 a delay spike longer than one second tripped the watchdog "
          f"first, which also stopped the robot safely, before it reached the box. Across all 550 trials the "
          f"mock counted zero collisions."))
add(("fig", "safety", "fig_safety.png", "Closest approach to the box in each run", 11.0))
rows = []
for c, cl in (("C0_ideal", "C0"), ("C1_50ms", "C1"), ("C2_100ms_1pct", "C2"), ("C3_200ms_5pct", "C3")):
    r = [cl]
    for t in TR:
        d = S[f"S5|{t}|{c}"]
        r.append(f"{d['stopped_at_box']}/10, {d['mean']:.1f} cm")
    r.append(str(int(sum(S[f"S5|{t}|{c}"]["coll"] for t in TR))))
    rows.append(r)
add(("table", "safety", "Obstacle guard: runs stopped at the box and mean clearance (mock)",
     ["Cond.", "TCP", "MQTT QoS 0", "MQTT QoS 1", "Collisions"], rows, [1.6, 3.6, 3.6, 3.6, 2.6]))
add(("h2", "9.7 What worked and what did not"))
add(("bullets", [
    "Worked: supervisory commands were accurate on every link; the safety layer prevented every collision; the "
    "watchdog stopped the robot within about 1.1 s; the stale guard and duplicate suppression made QoS 1 safe "
    "for motion; and TCP_NODELAY on both sides made MQTT as fast as TCP apart from the broker hop.",
    "Did not work: direct vel steering on the worst link (C3); QoS 1's tail latency under loss; and our "
    "first S2 script, which waited for results that a rejected command can never produce (fixed and re-run).",
    "Problems found by the experiments and fixed in the code: stop/go chatter at the stop line (hysteresis), "
    "the asymptotic slow-down that never reached the stop line (creep speed), and two operators fighting over "
    "the robot (exclusive control).",
    "Limits: mock backend only; synthetic operator; application-level loss model without congestion control; "
    "one PC, so real Wi-Fi effects such as bursty loss are not covered.",
]))

# ================================================================== 10
add(("h1", "10. Contribution"))
add(("p", "Each member owns one technical module. The table below is filled from the module each member is "
          "responsible for. Every claim must be traceable to that member's own commits in the GitHub "
          "repository (Appendix; commits per author are listed with scripts/git_author_stats.py). Each member "
          "signs their own row in the printed copy."))
CONTRIB = [
    ("Akshat Kumar Angi", "Simulation: mock P3-DX backend (kinematics, motor lag, 16 sonars, collisions), "
     "CoppeliaSim ZMQ backend and scene verification, 20 Hz server loop (server.py); GitHub repository and "
     "meeting log.", "Abstract, 1, 2, References"),
    ("Harsh Varma", "Operator side: command language and JSON protocol (protocol.py), TCP transport with "
     "exclusive control and reconnect, operator client and shell with history, macros, wait, watch, log "
     "(cli.py); run guide.", "6, 8"),
    ("Aniket Singh Bisht", "MQTT transport with QoS 0/1, persistent session, Last Will and TCP_NODELAY "
     "(mqtt.py); Mosquitto set-up; Nagle ablation S0 and TCP vs MQTT latency analysis; architecture diagram.",
     "3, 4"),
    ("Priyam Paliwal", "Robot control: kinematics, PID, move/turn/goto/vel (controller.py), safety layer with "
     "hysteresis, watchdog and stale guard (safety.py); PID tuning study; live demo.", "5, 7"),
    ("Yeshang Soni", "Impairment proxy (netem.py), experiment runner and scenarios S1-S5, synthetic operator "
     "model, metrics, analysis, all result tables and plots (analyze.py); results notes.", "9, 12, Appendix"),
]
add(("contrib",))

# ================================================================== 11
add(("h1", "11. Co-learning Reflection"))
add(("p", "Each member writes 5-8 lines in their own words: what I learned on my own, what I learned from "
          "team-mates, and what I taught others. The headings below are the template. The text must be the "
          "member's own and is intentionally left for each member to write."))
add(("reflections",))

# ================================================================== 12
add(("h1", "12. Conclusion and Future Scope"))
add(("p", f"We built a complete, tested chain for teleoperating a differential-drive robot through typed "
          f"shell commands over TCP or MQTT, and measured it in 550 repeatable trials under emulated network "
          f"conditions. The main findings are: (1) supervisory goto commands keep their accuracy on every link "
          f"and lose at most {max(s2_extra.values()):.0f} % in time, while direct velocity steering fails on a "
          f"200 ms, 5 % loss link; (2) the transport hardly matters for latency once the network adds real "
          f"delay, but MQTT costs 45-61 % more uplink bytes, and QoS 1 has the longest tail under loss; "
          f"(3) MQTT needs TCP_NODELAY on both client and broker, or every QoS 1 exchange costs about "
          f"{nag_def:.0f} ms; (4) QoS 1 replays commands after an outage, so a robot must check the age of "
          f"every motion command; and (5) safety that lives on the robot (obstacle guard, watchdog) behaves "
          f"the same for every transport and prevented every collision."))
add(("p", "**Industrial use.** The same pattern of goal-level commands, a robot-side safety layer, a "
          "communication watchdog and an age check on commands applies to remote assistance of delivery and "
          "warehouse robots, inspection robots on cellular links, and fleet dashboards built on MQTT."))
add(("p", "**Moving to a real robot.** Only a new backend is needed. A real P3-DX (or any differential-drive "
          "robot) can be driven through the same six-method interface, for example via ROS 2 velocity and "
          "sonar topics. The pose would then come from odometry with drift instead of ground truth, and the "
          "watchdog and stale guard need synchronised clocks (NTP) between the two computers."))
add(("p", "**Future work.** Verify the CoppeliaSim backend and repeat S2 and S5 there; run trials with "
          "human operators; measure on real Wi-Fi and cellular links; add bandwidth limits and a watchdog-timeout "
          "sweep to the emulator; add authentication and TLS to the MQTT link; and try a predictive display that "
          "shows the operator where the robot will be after the network delay."))

APPENDIX_INTRO = ("This appendix holds the links, the meeting log, the peer-assessment sheets and the commit "
                  "evidence. The tables below are templates that the team fills in before printing.")
