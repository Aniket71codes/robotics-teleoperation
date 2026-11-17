# Mosquitto setup

Owner: **Aniket Singh Bisht**

## Install

| OS | Command |
|---|---|
| Ubuntu / Debian | `sudo apt install mosquitto mosquitto-clients` |
| Fedora | `sudo dnf install mosquitto` |
| macOS (Homebrew) | `brew install mosquitto` |
| Windows | Download the installer from https://mosquitto.org/download/ and install to `C:\Program Files\mosquitto`. Tick "Service" only if you want it to auto-start. |

**Linux without sudo (used on the development machine).** The Ubuntu 24.04 packages were downloaded
and unpacked into the project. This needs no root:
```bash
mkdir -p tools/mosquitto && cd tools/mosquitto
apt-get download mosquitto libmosquitto1 libcjson1 libwebsockets19t64 libdlt2
for f in *.deb; do dpkg -x "$f" root; done && rm *.deb
cd ../.. && tools/mosquitto/run_mosquitto.sh 1883          # nodelay on (default)
tools/mosquitto/run_mosquitto.sh 1885 false                  # nodelay off, for the ablation
```

## Configuration (`config/mosquitto.conf`)
```
listener 1883
allow_anonymous true
set_tcp_nodelay true
```
Start with `mosquitto -c config/mosquitto.conf -v` (`-v` prints every connect and subscribe).

* **Mosquitto 2.x** refuses remote connections unless a `listener` is declared, and refuses anonymous
  clients unless `allow_anonymous true`. For a real network, add `password_file` and TLS.
* **Port conflict:** the Ubuntu package starts a system broker on 1883. Use `sudo systemctl stop mosquitto`
  or pick another port.

## Check that it works
```bash
mosquitto_sub -h 127.0.0.1 -t 'teleop/#' -v        # terminal A: prints all project traffic
mosquitto_pub -h 127.0.0.1 -t teleop/test -m hello  # terminal B
```

## Why `set_tcp_nodelay true` matters (measured)

paho-mqtt does not switch off Nagle's algorithm, and Mosquitto's `set_tcp_nodelay` is `false` by default.
With Nagle on, the small QoS 1 packets wait for the peer's delayed ACK. The project sets `TCP_NODELAY`
on paho's socket (`teleop/transport/mqtt.py`) and enables it in the broker. Experiment S0 measured the
effect on localhost: QoS 1, 10 trials × 30 pings per combination (`results/tables/T_nagle.md`, mock backend):

| Broker TCP_NODELAY | Client TCP_NODELAY | Trials | Median RTT (ms, mean ± sd) | Mean of max RTT (ms) |
|---|---|---|---|---|
| off (default) | off (paho default) | 10 | 55.2 ± 7.3 | 85.3 |
| off (default) | on | 10 | 41.7 ± 0.1 | 45.9 |
| on | off (paho default) | 10 | 41.8 ± 0.3 | 43.5 |
| on | on | 10 | 1.2 ± 0.1 | 2.0 |

Both sides must have Nagle off. If only one side is fixed, the ~40 ms penalty stays.

## QoS levels used in the study
* **QoS 0** (at most once): no PUBACK. A message published while the link is down is dropped by paho
  (`MQTT_ERR_NO_CONN`).
* **QoS 1** (at least once): every PUBLISH is acknowledged with a PUBACK. paho keeps unacknowledged and
  offline messages and resends them after reconnecting. The broker queues messages for a persistent
  session (`clean_session=False`). Duplicates are possible, and the client counts them (`duplicates`).
* QoS 2 is not used: its 4-way handshake adds a round trip, and the robot already de-duplicates by `seq`.
