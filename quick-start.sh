#!/bin/bash

echo "MQTT RTLS API - Quick Start"
echo "==========================="

# Clean up any existing containers
echo "Cleaning up..."
docker-compose down -v 2>/dev/null

# Create directories
echo "Creating directories..."
mkdir -p mosquitto/config mosquitto/data mosquitto/log mqtt-explorer-config

# Set permissions
sudo chmod -R 755 mosquitto/

# Build images
echo "Building Docker images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 10

# Show status
echo ""
echo "Service Status:"
docker-compose ps

echo ""
echo "✅ System is running!"
echo ""
echo "View RTLS data stream:"
echo "  docker-compose logs -f rtls-subscriber"
echo ""
echo "Access MQTT Explorer:"
echo "  http://localhost:4000"
echo ""
echo "Stop everything:"
echo "  docker-compose down"