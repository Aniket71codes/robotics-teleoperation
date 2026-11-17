# PROMPT FOR CLAUDE CODE

> Setup: create an empty folder, run `git init`, copy the two PDFs (project instructions and sample report) into `docs/reference/`,
> start Claude Code in that folder and paste everything below the line.

---

You are a senior robotics/software engineer and technical writer. Read both PDFs in `docs/reference/` first: they define the report format, the submission rules and the grading rubric.
Then build the **complete project** below on your own: code, tests, experiments, documentation, member work packages and the final report. Decide the folder and file structure yourself and document it.
Work in phases (code, experiments, docs, report, checks) and do not stop to ask permission at each step.

## Project
**Title:** Networked Teleoperation of a Robot through Shell Commands
**Platform:** CoppeliaSim + Python socket / MQTT (paho) command-line client
**Course:** CSAI4014 Algorithms for Intelligent Systems and Robotics, UPES, B.Tech CSE (AI & ML), Sem VII, Batch B3-B4

**What it does:** an operator types shell commands (move, turn, goto to a point, raw velocity, stop, status, ping, reset) in a terminal. The commands travel over a network
(TCP socket or MQTT) to a simulated differential-drive robot (Pioneer P3-DX in CoppeliaSim), which executes them with PID control and a safety layer (obstacle stop, link-loss watchdog) and sends telemetry back
(pose, state, obstacle distance, goal result). The study compares TCP and MQTT (QoS 0 and 1) under emulated network delay, jitter and packet loss, including an operator-in-the-loop steering test.

## What I need
1. **Working, tested code.** Because CoppeliaSim is probably not installed in your sandbox, include a pure-Python mock simulator so everything runs and is tested without it; also write the real CoppeliaSim backend (ZMQ Remote API) and mark it "to be verified on a real CoppeliaSim by the team".
   Include automated tests; MQTT tests may skip when no broker is available (try to install Mosquitto and run them).
2. **Real experiments.** Run the experiments (transport x delay/loss x scenarios, at least 10 trials each) and produce plots and a comparison table. Never invent numbers: every figure/table must come from a run you executed, labelled with the backend (mock or CoppeliaSim).
3. **Documentation.** A README, and a step-by-step **how to run** guide (Windows, Linux, macOS; mock demo, MQTT demo, CoppeliaSim demo, tests, experiments, where each output is saved), plus architecture, protocol, scene setup, Mosquitto setup, troubleshooting, syllabus mapping and novelty notes.
4. **Member work packages and commit plans** (below).
5. **The project report** (Word + PDF) exactly in the sample report's format (below).
6. **Helper material:** a 17-slide outline with presenters, a 20-minute demo/video script, a submission checklist, and templates for the meeting log and the peer-assessment sheet.

## Team and work split (5 members, one package each)
Create one guide per member (plain English, so the member can explain it in the viva): role summary, which files they own, a task checklist with "done when" criteria,
**their own commit plan**, the figures/evidence they produce, the report sections they write, 8-10 likely viva questions with short answers, and their slides and demo part.

| Member | Package |
|---|---|
| **Akshat Kumar Angi** | Simulation: CoppeliaSim scene, robot backends (mock + CoppeliaSim), the server loop that connects everything; creates the GitHub repo, keeps the meeting log |
| **Harsh Varma** | Operator side: the command language/protocol, the TCP socket connection, and the command-line shell (history, macros, `wait`, `log`, `watch`); the run documentation |
| **Aniket Singh Bisht** | MQTT transport, Mosquitto setup, latency measurements TCP vs MQTT QoS 0/1, architecture diagram |
| **Priyam Paliwal** | Robot control: kinematics, PID, move/turn/goto, safety layer, tuning, and the live demo |
| **Yeshang Soni** | Network-impairment emulation, experiment runner, metrics, plots and results notes |

**For every member's guide:** explain the module with a simple everyday analogy and a one-page "how it works" diagram, add a step-by-step manual test that member can run in 5 minutes,
keep the code clear, well commented and easy to read aloud, and give small, safe extension tasks (for example Harsh: a `watch` command, tab-completion, two more macro files, CLI tests).

## Commit rules (important)
The grading requires every member's work to be traceable to commits **from their own GitHub account**. So:
* Do **not** create commits under the members' names or emails, and do not rewrite history to simulate their work. Make at most one neutral scaffold commit, and only if I ask.
* In `COMMIT_PLAN.md` and in each member guide give each member an ordered list of suggested commits: branch name, Conventional-Commit message, files touched, and the test that must pass first.
  Aim for 6-10 meaningful commits per member for work they still really have to do (verification, small extensions, tuning, tests, docs, experiment runs).
* Provide the Git workflow (branches, pull requests, review by a teammate) and a script that prints commits and files changed per author, for report Section 10.

## Report (from the sample report; verify every rule by rendering the PDF and looking at the pages)
* Word file (python-docx) converted to PDF with LibreOffice; fall back to LaTeX only if a rule cannot be met. Extract the UPES logo from the sample PDF for the title page.
* A4 portrait; margins left 3.0 cm, others 2.5 cm; single-line border on **every** page incl. the title page; Times New Roman; body 12 pt, 1.5 spacing, justified; headings 14 pt bold, subheadings 12 pt bold.
* Page numbers bottom centre except on the title page; Roman numerals (i, ii, ...) for front pages, Arabic from Section 1. Real Index with page numbers, then List of Figures and List of Tables. Numbered, captioned figures/tables, each mentioned in the text.
* 25-35 pages; at least 8 real IEEE references cited in order; Novelty (Section 4) and Contribution (Section 10) present.
* Same title page as the sample (only the title, Project/Group/Batch and members change). Use `B3-B4` for the batch; use placeholders for Project No., Group No. and SAP IDs.
* Order: Title, Declaration, Index, Lists, Writing Allocation, Abstract (150-200 words with real results), 1 Introduction, 2 Problem and Objectives, 3 Literature, 4 Novelty, 5 Syllabus and Theory, 6 System Design,
  7 Methodology and Algorithms, 8 Simulation Setup, 9 Results and Analysis, 10 Contribution, 11 Co-learning Reflection, 12 Conclusion, References, Appendix (GitHub/YouTube link placeholders, meeting log, peer sheets).
* **Writing split (about 5 pages each):** Akshat: Abstract, 1, 2, References. Aniket: 3, 4. Priyam: 5, 7. **Harsh: 6, 8.** Yeshang: 9, 12, Appendix. Everyone: own row in 10, own reflection in 11, Declaration.
* Write full, specific text from the real code and results (no filler or leftover instruction text). Section 10 is pre-filled from each member's real module with the signature column blank. In Section 11 give each member only a heading and a short template; do **not** invent their personal experiences.
* Use only real, verifiable references (for example V-REP/CoppeliaSim paper, the OASIS MQTT spec, Mosquitto paper, a telerobotics text, Astrom and Murray, Siegwart, Siciliano and Khatib); omit any detail you cannot verify.
* Write `check_report` that verifies page count, citations of every figure/table/reference, abstract length and leftover placeholders, and show its output.

## Done means
Tests pass; the two-terminal demo in the run guide works exactly as written (paste real output); experiments, plots and table exist; every member guide has a commit plan; the report passes your checks and your visual review.
At the end, print a summary: what was built, what was tested and how, what was **not** tested (the CoppeliaSim backend), which numbers came from which backend, and what each member must still do and commit themselves.
Ask me only for things you cannot know: SAP IDs, project and group numbers, faculty name, GitHub URL, and whether CoppeliaSim is available.
