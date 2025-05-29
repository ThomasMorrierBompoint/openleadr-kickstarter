## 🔌 OpenADR 2.0b & OpenLEADR (openleadr-python)

> This project is intended for testing and demonstration purposes only. It is not production-ready.
> Several shortcuts were taken to keep the project lightweight while still showcasing as many features as possible.

## ✅ OpenADR Overview

OpenADR is a standard protocol that automates energy demand-response (DR) signals. It allows:

* **🖥 VTN (Virtual Top Node)** – typically run by the utility/ISO. It sends DR events.
* **🏠 VEN (Virtual End Node)** – typically a building or device. It responds to those events.
* [**OpenLEADR**](https://github.com/OpenLEADR/openleadr-python) is a Python implementation of both VTN and VEN for
  OpenADR 2.0a and 2.0b.

---

## 🧱 OpenADR Architecture Overview

```plaintext
       +---------------------+          +---------------------+
       |      VTN (Server)   | <------> |      VEN (Client)   |
       |  openleadr.VTN      |          |  openleadr.VEN      |
       +---------------------+          +---------------------+

          Utility or ISO                Customer Device / Site
```

OpenADR uses **pull** communication by default (VEN pulls events), optionally supports **push**.

VTN responsibilities:

* Publish DR events
* Handle reports from VENs
* Manage opt-in/opt-out states

VEN responsibilities:

* Register with VTN
* Receive events
* Send telemetry reports (if needed)
* Respond to events (opt in/out, act on signals)

`OpenLEADR` helps you implement both sides easily in **Python**.

---

## ✅ OpenADR Concepts in Practice

| Concept             | Implementation Point                        |
|---------------------|---------------------------------------------|
| Party Registration  | `on_create_party_registration` handler      |
| Events & Signals    | `add_event()` on VTN / `on_event` handler   |
| Telemetry Reporting | `add_report()` on VEN                       |
| Opt-in/Opt-out      | Return 'optIn'/'optOut' from `on_event`     |
| mTLS                | TLS certs and mutual auth in `run()`        |
| Event Scheduling    | Use `dtstart`, `duration`, `signals` params |

---

## ⚙️ Step-by-Step: Running a Basic VTN + VEN

| Goal                                  | How                                             |
|---------------------------------------|-------------------------------------------------|
| One liner setup with minimal config   | Dockerfiles for each component (docker-compose) |
| Simulate a VTN Server                 | Python / OpenADRServer                          |
| Simulate a VEN Client                 | Python / OpenADRClient                          |
| Use a web GUI to interface VTN Server | Wrap VTN event creation logic in a FastAPI GUI  |
| Log data                              | Plug in DB for telemetry                        |
| Local testing                         | Docs / Script for testing                       |

## 1. 🧠 Define the Use Case

For learning/testing: let’s simulate a utility (VTN) broadcasting a demand reduction event to a building (VEN) that
accepts it.

---

## 2. 🚀 How to Run

### Using local environment (Ensure Python 3.7+)

> Check out the `log` folder to compare your logs if they seem off...

```bash
cd openleadr-kickstarter
# python or python3 depending on your system path... usually python3 on macOS/Desbian like system
python -m venv venv
source venv/bin/activate
cd vtn
pip install -r requirements.txt

```

Open a new shell tab

```bash
cd openleadr-kickstarter
# python or python3 depending on your system path... usually python3 on macOS/Desbian like system
python -m venv venv
source venv/bin/activate
cd ven
pip install -r requirements.txt
```

### Using Docker Compose (Currently not working)

```bash
# Not working on my Windows WSL setup and macOS not sure why
# I guess the VTN server is trying to enforce HTTPS for some reason.
# I haven't tested with an SSL certificate yet...
docker compose up --build
```

This:

* 🖥 Create a Virtual Top Node (VTN)
    * Start a VTN that accepts VEN registrations.
    * Sends a one-hour demand-response event after startup.
* 🖥 Create a FastAPI to interface OpenADR VTN
    * Create and schedule events
    * View connected VENs
    * Monitor responses
* 🏠 Create a Virtual End Node (VEN)
    * Start a VEN that accepts VTN demand-response event.

It should do:

* VEN registering with VTN
* VTN sending an event
* VEN responding with "optIn"

---

## 3. 🧪 Testing (VTN + VEN)

To test your Docker Compose Network

Make sure the VEN connects to VTN. Then:

```bash
curl -X POST http://localhost:8000/send_event \
     -H "Content-Type: application/json" \
     -d '{"ven_id": "ven123", "event_id": "event002", "signal_level": 2}'
```

---

## 🧪 What's Next?

Here's how to level up with OpenADR:

| Goal                     | How                                            |
|--------------------------|------------------------------------------------|
| Simulate many VENs       | Script multiple clients using asyncio / Docker |
| Secure deployment        | Use Gunicorn + NGINX + TLS certs               |
| Integrate with BMS / IoT | Connect to BACnet/MQTT APIs from VEN           |

## For Dev installation

To work on the `local_lib`

```bash
pip install -e .
```

## ⚠️ Warning / Disclaimer

> **Running the project locally works, but the docker-compose setup is not working yet.**
> I tested the docker network, and both containers can ping each other, but the HTTP curl is blocked...
>
> I get this error
`ClientConnectorError: Cannot connect to host vtn:8080 ssl:default [Connect call failed ('172.21.0.2', 8080)]`
>
> I guess the VTN server is trying to enforce HTTPS for some reason. I haven't tested with an SSL certificate yet...

```bash
# VTN container: Check if the expected port is open and listening
docker exec -it vtn netstat -tulpn
# tcp        0      0 127.0.0.1:8080          0.0.0.0:*               LISTEN      1/python

# VEN container: DNS resolution - ensure the VTN hostname is resolvable
docker exec -it ven nslookup vtn
#Server:         127.0.0.11
#Address:        127.0.0.11#53
#
#Non-authoritative answer:
#Name:   vtn
#Address: 172.21.0.2

docker exec -it ven ping 172.21.0.2
#64 bytes from 172.21.0.2: icmp_seq=1 ttl=64 time=0.153 ms

docker exec -it ven ping vtn
#64 bytes from vtn.openleadr-kickstarter_openadr-net (172.21.0.2): icmp_seq=1 ttl=64 time=0.125 ms

# VEN container: HTTP connectivity - test if VEN can reach VTN over HTTP
docker exec -it ven curl http://172.21.0.2:8080
#curl: (7) Failed to connect to 172.21.0.2 port 8080 after 0 ms: Couldn't connect to server

docker exec -it ven curl http://vtn:8080
#curl: (7) Failed to connect to vtn port 8080 after 1 ms: Couldn't connect to server
```