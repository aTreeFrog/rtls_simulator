#!/bin/bash

echo "Debugging Mosquitto MQTT Broker"
echo "================================"

# Clean up first
echo "1. Cleaning up old containers..."
docker-compose down
docker rm -f mqtt-broker 2>/dev/null

# Check if port 1883 is already in use
echo ""
echo "2. Checking if port 1883 is already in use..."
if lsof -Pi :1883 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "ERROR: Port 1883 is already in use!"
    echo "Please stop any other MQTT brokers running on your system."
    lsof -Pi :1883 -sTCP:LISTEN
    exit 1
else
    echo "Port 1883 is free ✓"
fi

# Create directories with proper permissions
echo ""
echo "3. Creating directories with proper permissions..."
mkdir -p mosquitto/config mosquitto/data mosquitto/log
chmod -R 777 mosquitto/

# Start only mosquitto
echo ""
echo "4. Starting Mosquitto container..."
docker-compose up -d mosquitto

# Wait a bit
sleep 5

# Check mosquitto logs
echo ""
echo "5. Mosquitto logs:"
echo "==================="
docker-compose logs mosquitto

# Check if mosquitto is running
echo ""
echo "6. Container status:"
docker ps -a | grep mosquitto

# Try to connect manually
echo ""
echo "7. Testing MQTT connection..."
docker run --rm --network mqtt-rtls_rtls-network eclipse-mosquitto mosquitto_sub -h mosquitto -t 'test' -C 1 -E -v || echo "Connection test failed"

echo ""
echo "8. Checking container health:"
docker inspect mqtt-broker --format='{{json .State.Health}}' | jq