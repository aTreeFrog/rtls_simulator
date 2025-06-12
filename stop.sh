#!/bin/bash

# Stop script for MQTT RTLS API with Docker

echo "Stopping MQTT RTLS API services..."

# Stop services
docker-compose down

echo "All services stopped."

# Ask if user wants to clean up data
read -p "Do you want to remove all data and volumes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing volumes and data..."
    docker-compose down -v
    rm -rf mosquitto/data/*
    rm -rf mosquitto/log/*
    echo "All data removed."
fi

echo "Shutdown complete."