# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Could not connect: cannot connect to 127.0.0.1:9000` | robot server not running, or a different port | start `python -m teleop.server …` first, and use the same `--port` |
| `cannot reach MQTT broker at 127.0.0.1:1883: Connection refused` | no broker running | start Mosquitto (MQTT_SETUP.md) |
| MQTT client connects but the robot never answers | robot and operator use a different `--robot-id` or `--qos`, or different brokers | use the same values on both sides; check with `mosquitto_sub -t 'teleop/#' -v` |
| `!! robot says: robot busy: another operator has control` | another shell is connected (TCP exclusive control) | close the other shell, or wait 1 s after it goes quiet |
| Every command answers `REJECTED: stale: command is … s old` | clocks of the two PCs differ by more than 1 s (the age check uses wall-clock time) | sync clocks (NTP: `timedatectl set-ntp true`, Windows: *Settings → Time → Sync now*), or start the server with `--max-cmd-age 5` |
| Robot stops by itself and the state shows `LINK_LOST` | no message for 1 s: network stall, shell closed, laptop asleep | expected safety behaviour; send a new command. Raise `--watchdog` only if your link really has >1 s stalls |
| Robot stops before a wall and shows `OBSTACLE` | safety layer (front sonar < 0.30 m) | turn away (`turn 90`) or reverse (`move -0.3`) |
| `move` result is `blocked` | an obstacle blocked the robot for more than 2 s | clear the path or choose another goal |
| `pytest` fails: `No module named 'lark'` / launch_testing | ROS is on `PYTHONPATH` and its pytest plugins load | `unset PYTHONPATH` (or `env -u PYTHONPATH python -m pytest`) |
| QoS 1 round trip about 40 ms on localhost | Nagle's algorithm on the broker | add `set_tcp_nodelay true` to mosquitto.conf |
| `Address already in use` | an old server or broker still runs | stop it (Ctrl+C), or `ss -ltnp \| grep 9000` (Linux) / `netstat -ano \| findstr 9000` (Windows) |
| Windows: `Activate.ps1 cannot be loaded` | PowerShell execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Windows firewall popup | the server listens on 0.0.0.0 | allow on *private* networks only |
| Arrow keys print `^[[A` in the shell | no readline (Windows) | optional: `pip install pyreadline3` |
| CoppeliaSim: `object does not exist` | model path names differ | see SCENE_SETUP.md §3 |
| CoppeliaSim robot moves by itself | built-in Braitenberg child script still attached | remove it (SCENE_SETUP.md §2 step 3) |
| Report PDF not produced | `soffice` not on PATH | install LibreOffice and add it to PATH |
