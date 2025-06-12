# RTLS Simulator: Mock RTLS Data Streaming via MQTT & ROS

## Overview

**RTLS Simulator** is a Python-based framework for simulating Real-Time Location System (RTLS) data streams in an industrial/warehouse context.  
It generates realistic mock data (position, movement, zone events, battery, signal strength, etc.) for vehicles, assets, and people within user-defined zones—publishing these streams via **MQTT** in real time.

This system is designed for rapid prototyping, integration testing, robotics development, and as a learning tool for edge computing, IoT, and ROS-based (Robot Operating System) environments.

- **Supports:**  
  - Docker-based local deployment (including all dependencies)
  - MQTT protocol (Mosquitto broker by default)
  - Integration with ROS (publishes `Pose` messages for robot consumption)
  - Customizable tags/zones/anomaly simulation

---

## Key Features

- **Mock RTLS Generator:** Realistic movement, zone detection, events, and anomaly simulation for multiple tag types (vehicles, people, assets).
- **MQTT Publisher:** Streams live RTLS data and alerts to a broker.
- **Subscriber Example:** Converts MQTT RTLS data into ROS `geometry_msgs/Pose` for downstream robotics applications.
- **Dockerized Stack:** Includes Mosquitto broker, publisher, and subscriber; all reproducible with Docker Compose.
- **Extensive Configurability:** All tag, zone, and movement parameters can be easily changed via YAML config files.
- **Testing:** Comes with pytest-based unit tests for the generator and MQTT client.
- **Web UI:** Optionally includes MQTT Explorer for real-time topic monitoring.

---

## Repository Structure

```
config/                # YAML configs for RTLS tags, zones, movement parameters
examples/              # Example scripts for publisher and subscriber logic
mosquitto/             # Mosquitto broker configs
mqtt-explorer-config/  # MQTT Explorer web UI settings
src/                   # Main source code: models, generator, mqtt client, entrypoint
tests/                 # Unit tests for all core logic
docker-compose.yml     # Main docker-compose stack for all services
Makefile               # Make commands for building/running/testing
quick-start.sh         # Single-command launcher for local setup
requirements.txt       # Python dependencies
DOCKER_SETUP.md        # Full Docker and deployment guide
```

---

## How It Works

### 1. **RTLS Data Generation**

- **Zones** and **Tags** (assets, people, vehicles) are defined in YAML configs.
- The RTLS generator simulates movement, boundary collisions, zone transitions, battery drain, signal variation, and random anomalies.
- Each tag is updated at a configurable rate (default: every 1 second).

### 2. **Publishing Data (MQTT)**

- The publisher sends:
  - Tag location updates: `rtls/location/<tag_id>`
  - Zone occupancy lists: `rtls/zone/<zone_id>/tags`
  - Zone transition alerts: `rtls/alerts`
  - System status: `rtls/status`
- Messages are JSON, using schemas defined in `src/models.py`.

### 3. **Consuming Data (Examples & ROS Integration)**

- The subscriber example listens on MQTT and republishes locations as ROS `Pose` messages on `/rtls_pose`.
- Demonstrates integration with real robots (ROS Noetic).

### 4. **Dockerized Stack**

- Runs all components (broker, publisher, subscriber, MQTT Explorer) as containers, pre-networked.
- Includes Makefile and bash scripts for easy management.

---

## Getting Started

### **Quick Start with Docker Compose**

```bash
# 1. Clone this repo
git clone https://github.com/yourusername/rtls_simulator.git
cd rtls_simulator

# 2. (Linux/Mac/WSL) Run quick-start script
./quick-start.sh

# 3. (Alternative) Manually build & launch
docker-compose build
docker-compose up -d

# 4. See live data in logs
docker-compose logs -f rtls-subscriber
```

### **Web UI for MQTT**

- Open [http://localhost:4000](http://localhost:4000) (MQTT Explorer, optional).
- Connect to `mosquitto:1883` to browse topics.

### **ROS Integration**

```bash
# Attach to the subscriber container
docker exec -it rtls-subscriber bash
source /opt/ros/noetic/setup.bash
rostopic echo /rtls_pose
```

---

## Configuration

- **Zones, tags, movement:**  
  Edit `config/docker-config.yaml` (or `config/config.yaml` for local use).
- **MQTT Broker:**  
  Change settings in the same config or `mosquitto/config/mosquitto.conf`.
- **Add/remove tags/zones:**  
  Just update the YAML and restart the publisher.

---

## Developer Guide

### **Core Modules**

- `src/rtls_generator.py` – Simulates RTLS tag physics, anomalies, and zone detection.
- `src/mqtt_client.py` – Wraps MQTT publish logic for locations, zones, alerts, and status.
- `src/models.py` – Dataclasses for tag, zone, and message schemas.
- `src/main.py` – Main publisher entrypoint, loads config, runs the publishing loop.
- `examples/publisher_example.py` – Scripted example of custom publishing and batch updates.
- `examples/subscriber_example.py` – Example: converts MQTT updates to ROS `Pose` messages.

### **Testing**

Run all tests (in Docker, recommended):
```bash
make test
```
or
```bash
docker-compose run --rm rtls-publisher pytest tests/
```

---

## Advanced Usage

- **Modify movement behavior:**  
  Tweak the logic in `src/rtls_generator.py`.
- **Simulate anomalies:**  
  Publisher can trigger low battery, weak signal, fast movement, out-of-bounds, etc.
- **Write custom subscribers:**  
  Subscribe to topics like `rtls/location/#` to get all tag updates.

---

## Production Notes

- Supports authentication and persistent MQTT storage for production (see `DOCKER_SETUP.md`).
- Easily extensible for other RTLS formats, time-series DB sinks, cloud relays, or analytics pipelines.
- Designed for edge device, robotics, and digital twin scenarios.

---

## Example Data Output

**Sample Location Message (MQTT Topic: `rtls/location/tag_001`):**
```json
{
  "tag_id": "tag_001",
  "timestamp": "2025-06-11T21:50:11.823Z",
  "location": {"x": 51.2, "y": 24.7, "z": 0.0},
  "zone_id": "warehouse_a",
  "speed": 2.31,
  "heading": 23.2,
  "battery": 98,
  "rssi": -69
}
```

**Sample Zone Alert (MQTT Topic: `rtls/alerts`):**
```json
{
  "tag_id": "tag_001",
  "tag_name": "Forklift 1",
  "timestamp": "2025-06-11T21:50:19.141Z",
  "event_type": "entered",
  "zone_id": "loading_dock",
  "zone_name": "Loading Dock"
}
```

---

## License

MIT License

---

## Authors

- Original code by [ATreeFrog](mailto:ATreeFrog@RobotsAreEvil.com) and contributors.
- See [setup.py](setup.py) for more.

---

*For more usage tips, production deployment, or extending this project, see [`DOCKER_SETUP.md`](DOCKER_SETUP.md) in this repository.*

---
