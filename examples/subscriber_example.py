#!/usr/bin/env python3

import json
import signal
import sys
import paho.mqtt.client as mqtt
import rospy
from geometry_msgs.msg import Pose, Point, Quaternion

class RTLS2ROSPoseNode:
    def __init__(self, broker='localhost', port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id='rtls_ros_pose')
        self.pose_pub = None

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\nShutting down...")
        self.client.disconnect()
        rospy.signal_shutdown('SIGINT received')
        sys.exit(0)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker at {self.broker}:{self.port}")
            # Subscribe to location messages for all tags
            client.subscribe("rtls/location/+", qos=1)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split('/')
            payload = json.loads(msg.payload.decode('utf-8'))
            if topic_parts[1] == 'location':
                tag_id = topic_parts[2]
                loc = payload["location"]
                pose = Pose()
                pose.position = Point(x=loc["x"], y=loc["y"], z=loc["z"])
                pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
                self.pose_pub.publish(pose)
                # Full logging
                print(f"[{rospy.get_time():.2f}] Location Update - Tag: {tag_id}")
                print(f"  Position: ({loc['x']:.2f}, {loc['y']:.2f}, {loc['z']:.2f})")
                print(f"  Zone: {payload.get('zone_id', 'None')}, "
                    f"Speed: {payload.get('speed', 0.0):.2f} m/s, "
                    f"Battery: {payload.get('battery', 'N/A')}%")
                print(f"Published Pose for {tag_id}: ({loc['x']:.2f}, {loc['y']:.2f}, {loc['z']:.2f})")
                print('-' * 60)
        except Exception as e:
            print(f"Error processing MQTT message: {e}")

    def run(self):
        rospy.init_node('rtls_pose_node', anonymous=True)
        self.pose_pub = rospy.Publisher('/rtls_pose', Pose, queue_size=10)
        print("ROS node started. Publishing Pose messages to /rtls_pose.")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
        # Keep ROS node alive
        rospy.spin()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--broker', default='localhost')
    parser.add_argument('--port', type=int, default=1883)
    args = parser.parse_args()
    node = RTLS2ROSPoseNode(broker=args.broker, port=args.port)
    node.run()
