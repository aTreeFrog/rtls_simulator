FROM ros:noetic-ros-core

WORKDIR /app

# Install pip and Python dependencies
RUN apt-get update && apt-get install -y python3-pip python3-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install ROS Python libraries
RUN apt-get update && apt-get install -y \
      ros-noetic-rospy \
      ros-noetic-geometry-msgs \
    && rm -rf /var/lib/apt/lists/*

# Copy your code
COPY config/ ./config/
COPY src/ ./src/
COPY examples/ ./examples/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Source ROS before running Python
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["python3", "examples/subscriber_example.py", "-b", "mosquitto"]
