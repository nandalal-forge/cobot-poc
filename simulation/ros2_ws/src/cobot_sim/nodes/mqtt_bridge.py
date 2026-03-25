#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import paho.mqtt.client as mqtt
import json

class MQTTBridge(Node):
    def __init__(self):
        super().__init__('mqtt_bridge')
        self.mqtt = mqtt.Client()
        self.mqtt.connect('localhost', 1883)
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.get_logger().info('MQTT bridge started')

    def odom_cb(self, msg):
        payload = json.dumps({
            'x': round(msg.pose.pose.position.x, 3),
            'y': round(msg.pose.pose.position.y, 3),
        })
        self.mqtt.publish('cobot/position', payload)

def main():
    rclpy.init()
    rclpy.spin(MQTTBridge())

if __name__ == '__main__':
    main()