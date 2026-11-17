# Harsh Varma: Operator side: protocol, TCP connection, command-line shell, run documentation

## 1. Your role in one paragraph
You own **everything the operator touches**: the command language (`move 1 0.3`), the JSON messages
that carry it, the TCP socket connection, and the interactive shell with history, macros, `wait`,
`log` and `watch`. You also own **docs/HOW_TO_RUN.md**. It must work exactly as written on Windows,
Linux and macOS, so you check it on a real laptop.

## 2. Files you own
| File | What it does |
|---|---|
| `teleop/protocol.py` | grammar of the 8 commands, JSON message builders, line framing for TCP, validation |
| `teleop/transport/tcp.py` | TCP server (robot) and client (operator), exclusive control, auto-reconnect |
| `teleop/transport/base.py` | the two small interfaces that TCP and MQTT both implement |
| `teleop/client.py` | operator API: seq numbers, acks/results, heartbeat, telemetry log |
| `teleop/cli.py` | the interactive shell |
| `macros/*.tlm` | command files for the shell |
| `docs/HOW_TO_RUN.md`, `docs/PROTOCOL.md`, `docs/TROUBLESHOOTING.md` | run documentation |
| tests: `tests/test_protocol.py`, shell tests in `tests/test_system_tcp.py` | |

## 3. Everyday analogy
The operator side is **ordering food by phone**. The *command language* is the menu: you can only order
dishes on it, with the right options ("move, 1 metre, at 0.3"). The *JSON message* is the order slip the
restaurant writes down, with an order number (`seq`) so they can say "order 7 is ready". *TCP* is the
phone line: whatever you say arrives, in order, or the line drops. The *shell* is you with a notepad:
it remembers what you ordered before (history), reads out a saved list (macro), waits until order 7
arrives (`wait`), and keeps glancing at the delivery tracker (`watch`).

## 4. How it works (one page)
```
 you type:  goto 2 1
      │ parse_command()    → {"cmd":"goto","args":{"x":2,"y":1,"speed":0.3}}   (errors shown at once)
      ▼
 OperatorClient.send_command()
      │ seq += 1 ; remember Pending(seq) ; make_cmd(seq, sid, time)
      ▼
 TcpClient.send()  → b'{"type":"cmd","seq":4,...}\n'   (TCP_NODELAY: no 40 ms Nagle wait)
      ▼  ………… network ………… (robot validates, checks age, starts goto)
 reader thread ← b'{"type":"ack","seq":4,"ok":true}\n'   LineBuffer splits the byte stream on \n
      │ pending[4].ack = … ; event.set()     → shell prints "<- ack #4 goto ok (1.2 ms)"
      ◄ later: {"type":"result","seq":4,"outcome":"reached"}  → printed at once; `wait` returns
 heartbeat thread: {"type":"hb"} every 0.25 s   (robot watchdog stays happy)
```
Key ideas to explain: **framing** (TCP is a byte stream, so `\n` marks message ends); **matching by
seq**; **the same parser on both sides** (`validate_cmd` reuses `parse_command`), so a bad client
cannot crash the robot; **exclusive control** (a second operator is refused while the first is active).

## 5. Five-minute manual test
```bash
python -m teleop.server --port 9000                    # terminal 1
python -m teleop.cli --port 9000                       # terminal 2
teleop> help
teleop> move abc            # error: dist must be a number
teleop> macro macros/goto_square.tlm
teleop> log start /tmp/t.csv
teleop> watch 3
teleop> log stop
teleop> history
python -m teleop.cli --port 9000                       # terminal 3, while 2 is still open
                                                        # → "robot busy: another operator has control"
```
Then `python -m pytest tests/test_protocol.py tests/test_system_tcp.py`.

## 6. Task checklist
| Task | Done when |
|---|---|
| Run every command in HOW_TO_RUN.md on your own OS | output matches; differences fixed in the guide |
| Ask one teammate on another OS to follow the guide without help | they finish Demo A and B alone |
| Tab-completion | `mo<TAB>` completes to `move`; `macro mac<TAB>` completes the path |
| Two more macro files + a test that every macro parses | test passes |
| CLI tests for error paths | new tests pass |
| `repeat` / `!n` | tests pass |
| Report Sections 6 and 8 | `check_report.py` passes |

## 7. Your commit plan
| # | Branch | Commit message | Files | Must pass first |
|---|---|---|---|---|
| 1 | `docs/harsh-run-verify` | `docs(run): verify HOW_TO_RUN on <your OS> and paste real output` | `docs/HOW_TO_RUN.md` | Demos A, B, C run as written |
| 2 | `feat/harsh-tab-completion` | `feat(cli): tab-completion for command and macro names` | `teleop/cli.py` | manual test |
| 3 | `test/harsh-cli` | `test(cli): parse errors, wait without goal, watch without telemetry, log usage` | `tests/test_cli.py` | new tests pass |
| 4 | `feat/harsh-macros` | `feat(macros): add figure_eight.tlm and patrol.tlm` | `macros/`, `tests/test_cli.py` | every macro line parses |
| 5 | `feat/harsh-repeat` | `feat(cli): 'repeat <n> <command>' and '!<n>' history recall` | `teleop/cli.py`, tests | tests pass |
| 6 | `feat/harsh-color` | `feat(cli): colour the state column; --no-color flag` | `teleop/cli.py` | existing tests unchanged |
| 7 | `feat/harsh-hello` | `feat(protocol): hello/version handshake on connect` | `protocol.py`, `client.py`, `server.py`, tests | mismatch test passes |
| 8 | `docs/harsh-report` | `docs(report): write Sections 6 and 8` | `report/content.py` | check_report passes |

Hint for #2: `readline.set_completer(fn)` and `readline.parse_and_bind("tab: complete")`. The
completer gets the text typed so far and a state index; return the state-th match from
`list(COMMANDS) + ["wait", "watch", "macro", ...]`.

## 8. Figures and evidence you produce
* terminal screenshots of the shell (report Section 8 and slide 11);
* the verified run guide;
* the message-sequence diagram (`results/figures/diag_sequence.png`, from `report/diagrams.py`). Explain it.

## 9. Report sections you write
**6 System Design** and **8 Simulation Setup** (about 5 pages), plus your row in Section 10, your
reflection in Section 11 and your Declaration signature.

## 10. Likely viva questions
1. **Why newline-delimited JSON over TCP?** TCP delivers a byte stream, not messages. One `recv()` can
   return half a message or three. A `\n` after every JSON object lets the receiver cut the stream
   into messages (`LineBuffer`). JSON is readable, so we can debug with `nc` or a log.
2. **What is TCP_NODELAY and why set it?** It turns off Nagle's algorithm, which holds small packets
   back to merge them. For a 60-byte command that can add up to about 40 ms (we measured this for MQTT in S0).
3. **What is `seq` for, and why also `sid`?** `seq` matches each reply to its command. `sid` is a random
   session id, so (sid, seq) is unique even after the operator restarts. The robot runs each pair only once.
4. **Why does the robot validate again if the shell already parsed the command?** Never trust the
   network. Another program or a bug could send anything. The robot reuses the same parser, so both sides
   apply identical rules.
5. **What happens if two operators connect?** The second gets `robot busy` and is disconnected, unless
   the first has been silent for more than 1 s.
6. **Why the heartbeat?** Without it, an operator who types nothing for a few seconds would look exactly
   like a dead link to the watchdog.
7. **What does Ctrl+C do in the shell?** It sends `stop` (emergency stop) instead of quitting. `quit` leaves.
8. **What if the connection drops?** The TCP client reconnects every 0.25 s. Commands typed while it is
   down are reported as "not sent". The robot has already stopped (watchdog).
9. **Why is the ack slower (~40-50 ms) than a ping (~1 ms) on localhost?** Commands are applied at the
   start of the next 50 ms tick. Pings are answered immediately by the network thread.
10. **How does `wait` know when to return?** It waits on the `result_event` of the last
    move/turn/goto. The reader thread sets it when the `result` message with the same seq arrives.

## 11. Slides and demo part
* **Slides 9 and 11** (Algorithm 1: command protocol and shell, with the sequence diagram; Simulation
  Setup and how to run).
* In the **live demo** you drive the shell (type the commands) while Priyam explains the robot's
  behaviour. Rehearse with `docs/helpers/DEMO_SCRIPT.md`.

## 12. Small, safe extension tasks
`watch` already exists. Possible extensions: tab-completion, two more macro files, CLI tests,
`repeat`, coloured states, a `hello` handshake, and a `--json` output mode for scripting.
