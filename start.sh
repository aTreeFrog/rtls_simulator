#!/bin/bash

# Start script for MQTT RTLS API with Docker

set -e

echo "MQTT RTLS API - Docker Startup"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p mosquitto/config mosquitto/data mosquitto/log
mkdir -p mqtt-explorer-config

# Check if mosquitto.conf exists
if [ ! -f mosquitto/config/mosquitto.conf ]; then
    echo "Error: mosquitto/config/mosquitto.conf not found"
    echo "Please ensure all files are properly set up"
    exit 1
fi

# Set permissions
echo "Setting permissions..."
chmod -R 755 mosquitto/

# Copy .env file if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
    fi
fi

# Build images
echo "Building Docker images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Check service status
echo ""
echo "Service Status:"
echo "==============="
docker-compose ps

echo ""
echo "Services are running!"
echo ""
echo "Access points:"
echo "- MQTT Broker: localhost:1883"
echo "- MQTT WebSocket: ws://localhost:9001"
echo "- MQTT Explorer: http://localhost:4000"
echo ""
echo "View logs with: docker-compose logs -f"
echo "Stop services with: docker-compose down"
echo ""
echo "To see RTLS data, run: docker-compose logs -f rtls-subscriber"