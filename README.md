# openleadr-kickstarter

Based on openleadr-python for learning purposes

> **Note running the project locally works but the docker-compose is not working (probably a network miss configuration).**

## 🔌 OpenADR 2.0b & OpenLEADR: Quick Primer for Devs

> This project is meant for testing purposes only not production ready. Some shorcut where made to make this project as
> small as possible while providing has much feature has possible

### ✅ OpenADR Overview

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
| ------------------- | ------------------------------------------- |
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

### 1. 🧠 Define the Use Case

For learning/testing: let’s simulate a utility (VTN) broadcasting a demand reduction event to a building (VEN) that
accepts it.

---

### 2. 🚀 How to Run

Assuming Docker is already installed...

```bash
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

```bash
pip install -e .
```