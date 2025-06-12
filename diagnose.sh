#!/bin/bash

echo "Diagnosing RTLS Container Issues"
echo "================================"

# Check publisher logs
echo -e "\n1. Publisher Logs:"
echo "-------------------"
docker-compose logs --tail=20 rtls-publisher

# Check subscriber logs
echo -e "\n2. Subscriber Logs:"
echo "-------------------"
docker-compose logs --tail=20 rtls-subscriber

# Check if files exist in container
echo -e "\n3. Checking files in publisher container:"
echo "------------------------------------------"
docker-compose run --rm rtls-publisher ls -la
docker-compose run --rm rtls-publisher ls -la src/
docker-compose run --rm rtls-publisher ls -la examples/

# Test Python imports
echo -e "\n4. Testing Python imports:"
echo "---------------------------"
docker-compose run --rm rtls-publisher python -c "import src; print('src module OK')"
docker-compose run --rm rtls-publisher python -c "import yaml; print('yaml module OK')"
docker-compose run --rm rtls-publisher python -c "import paho.mqtt.client; print('paho-mqtt OK')"

# Check if main.py is executable
echo -e "\n5. Testing main module:"
echo "------------------------"
docker-compose run --rm rtls-publisher python -c "from src import main; print('main module OK')"

# Rebuild without cache
echo -e "\n6. Rebuilding images without cache..."
echo "--------------------------------------"
docker-compose build --no-cache