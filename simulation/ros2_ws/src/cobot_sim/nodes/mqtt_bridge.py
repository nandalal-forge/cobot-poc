#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, Image
import paho.mqtt.client as mqtt
import json

class MQTTBridge(Node):
    def __init__(self):
        super().__init__('mqtt_bridge')
        self.mqtt = mqtt.Client()
        self.mqtt.connect('localhost', 1883)

        # Odometry subscriber
        self.create_subscription(
            Odometry, '/odom', self.odom_cb, 10)

        # IMU subscriber
        self.create_subscription(
            Imu, '/imu/data', self.imu_cb, 10)

        self.get_logger().info('MQTT bridge started — odom + IMU')

    def odom_cb(self, msg):
        payload = json.dumps({
            'x': round(msg.pose.pose.position.x, 3),
            'y': round(msg.pose.pose.position.y, 3),
            'heading': round(msg.pose.pose.orientation.z, 3),
        })
        self.mqtt.publish('cobot/position', payload)

    def imu_cb(self, msg):
        payload = json.dumps({
            'ax': round(msg.linear_acceleration.x, 3),
            'ay': round(msg.linear_acceleration.y, 3),
            'az': round(msg.linear_acceleration.z, 3),
            'gx': round(msg.angular_velocity.x, 3),
            'gy': round(msg.angular_velocity.y, 3),
            'gz': round(msg.angular_velocity.z, 3),
        })
        self.mqtt.publish('cobot/imu', payload)

def main():
    rclpy.init()
    rclpy.spin(MQTTBridge())

if __name__ == '__main__':
    main()