# Docker Setup Guide for MQTT RTLS API

This guide explains how to run the entire MQTT RTLS system using Docker.

## Prerequisites

- Docker Engine (20.10 or newer)
- Docker Compose (2.0 or newer)
- Make (optional, for using Makefile commands)

## Quick Start

1. **Clone the repository and navigate to the project directory:**
```bash
git clone https://github.com/yourusername/rtls_simulator.git
cd rtls_simulator
```

2. **Create necessary directories:**
I did all this in powershell wsl 
```bash
mkdir -p mosquitto/config mosquitto/data mosquitto/log
mkdir -p mqtt-explorer-config
chmod +x start.sh stop.sh
chmod +x quick-start.sh
./quick-start.sh
```


3. **Start all services: IF USING MAKEUP NOT SURE IF THIS WORKS ANYMORE**
```bash
# Using Make
make up

# Or using docker-compose directly
docker-compose up -d
```

4. **View the logs:**
```bash
# All services
make logs

# Or specific service
docker-compose logs -f rtls-subscriber

to see the pose messages inside ros image do this in sequence
docker exec -it rtls-subscriber bash
source /opt/ros/noetic/setup.bash
rostopic echo /rtls_pose
```

## Services Overview

The Docker setup includes the following services:

### 1. Mosquitto MQTT Broker
- **Container**: `mqtt-broker`
- **Ports**: 
  - `1883` - MQTT protocol
  - `9001` - WebSocket protocol
- **Health Check**: Automatically monitored

### 2. RTLS Publisher
- **Container**: `rtls-publisher`
- **Purpose**: Generates and publishes mock RTLS data
- **Config**: Uses `config/docker-config.yaml`

### 3. RTLS Subscriber
- **Container**: `rtls-subscriber`
- **Purpose**: Example subscriber that displays incoming RTLS data
- **Output**: Prints formatted RTLS updates to console

### 4. MQTT Explorer (Optional)
- **Container**: `mqtt-explorer`
- **Port**: `4000`
- **Access**: http://localhost:4000
- **Purpose**: Web-based MQTT client for monitoring

## Using the System

### View Real-time Data

1. **Check subscriber logs to see RTLS data:**
```bash
docker-compose logs -f rtls-subscriber
```

You should see output like:
```
[10:30:45] Location Update - Tag: tag_001
  Position: (45.2, 23.8, 1.5)
  Zone: warehouse_a, Speed: 2.3 m/s, Battery: 85%
------------------------------------------------------------
[10:30:45] ALERT - Zone Transition
  Forklift 1 entered Loading Dock
------------------------------------------------------------
```

2. **Use MQTT Explorer:**
- Open http://localhost:4000 in your browser
- Connect to `mosquitto:1883` (or `localhost:1883` from host)
- Browse the topic tree to see all RTLS data

### Available Commands

Using Make:
```bash
make build      # Build Docker images
make up         # Start all services
make down       # Stop all services
make logs       # View logs from all services
make clean      # Remove containers and volumes
make restart    # Restart all services
make status     # Show status of all services
make shell      # Open shell in publisher container
make test       # Run tests in Docker
```

Without Make:
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove everything
docker-compose down -v
```

## Configuration

### Modify RTLS Settings

Edit `config/docker-config.yaml` to:
- Add/remove tags
- Modify zones
- Adjust update intervals
- Change movement parameters

After changes, restart the publisher:
```bash
docker-compose restart rtls-publisher
```

### Add Custom Subscribers

Create a new service in `docker-compose.yml`:
```yaml
my-subscriber:
  build: .
  container_name: my-subscriber
  depends_on:
    mosquitto:
      condition: service_healthy
  volumes:
    - ./my_scripts:/app/my_scripts
  networks:
    - rtls-network
  command: python /app/my_scripts/custom_subscriber.py
```

## Monitoring and Debugging

### View Individual Service Logs
```bash
# Publisher logs
docker-compose logs -f rtls-publisher

# Broker logs
docker-compose logs -f mosquitto

# Subscriber logs
docker-compose logs -f rtls-subscriber
```

### Check Service Health
```bash
make status
# or
docker-compose ps
```

### Access Container Shell
```bash
# Publisher container
docker-compose exec rtls-publisher /bin/bash

# Run Python commands
docker-compose exec rtls-publisher python
```

## Production Deployment

For production use:

1. **Enable MQTT Authentication:**
   - Create password file: `mosquitto_passwd -c mosquitto/config/passwords username`
   - Update `mosquitto.conf` to disable anonymous access
   - Update `docker-config.yaml` with credentials

2. **Use Environment Variables:**
   ```yaml
   environment:
     - MQTT_BROKER=${MQTT_BROKER:-mosquitto}
     - MQTT_USERNAME=${MQTT_USERNAME}
     - MQTT_PASSWORD=${MQTT_PASSWORD}
   ```

3. **Add Persistent Volumes:**
   ```yaml
   volumes:
     - mqtt-data:/mosquitto/data
     - mqtt-logs:/mosquitto/log
   ```

4. **Set Resource Limits:**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 256M
   ```

## Troubleshooting

### Services Won't Start
- Check if ports 1883, 9001, or 4000 are already in use
- Verify Docker daemon is running
- Check logs: `docker-compose logs`

### No Data Appearing
- Ensure Mosquitto is healthy: `docker-compose ps`
- Check publisher logs for errors
- Verify network connectivity between containers

### Permission Issues
- Ensure mosquitto directories have correct permissions
- Run: `chmod -R 755 mosquitto/`

### Reset Everything
```bash
make clean
# or
docker-compose down -v
rm -rf mosquitto/data/* mosquitto/log/*
```

## Next Steps

- Modify the RTLS generator to match your specific use case
- Implement custom subscribers for your application
- Add data persistence with a time-series database
- Set up monitoring with Prometheus/Grafana
- Deploy to Kubernetes for scalability