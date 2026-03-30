#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
import paho.mqtt.client as mqtt
import json
import sys
sys.path.insert(0, '/home/forge/cobot-poc')

class MQTTBridge(Node):
    def __init__(self):
        super().__init__('mqtt_bridge')
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.connect('localhost', 1883)
        self.mqtt_client.loop_start()

        try:
            from backend.app.services.influx_writer import write_position, write_imu
            self.write_position = write_position
            self.write_imu = write_imu
            self.influx_ok = True
            self.get_logger().info('InfluxDB connected')
        except Exception as e:
            self.influx_ok = False
            self.get_logger().warn(f'InfluxDB not available: {e}')

        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.get_logger().info('MQTT bridge started — odom + IMU + InfluxDB')

    def odom_cb(self, msg):
        x = round(msg.pose.pose.position.x, 3)
        y = round(msg.pose.pose.position.y, 3)
        heading = round(msg.pose.pose.orientation.z, 3)
        payload = json.dumps({'x': x, 'y': y, 'heading': heading})
        self.mqtt_client.publish('cobot/position', payload)
        if self.influx_ok:
            try:
                self.write_position('cobot_01', x, y)
            except Exception as e:
                self.get_logger().warn(f'InfluxDB position write failed: {e}')

    def imu_cb(self, msg):
        data = {
            'ax': round(msg.linear_acceleration.x, 3),
            'ay': round(msg.linear_acceleration.y, 3),
            'az': round(msg.linear_acceleration.z, 3),
            'gx': round(msg.angular_velocity.x, 3),
            'gy': round(msg.angular_velocity.y, 3),
            'gz': round(msg.angular_velocity.z, 3),
        }
        self.mqtt_client.publish('cobot/imu', json.dumps(data))
        if self.influx_ok:
            try:
                self.write_imu('cobot_01', **data)
            except Exception as e:
                self.get_logger().warn(f'InfluxDB IMU write failed: {e}')

def main():
    rclpy.init()
    rclpy.spin(MQTTBridge())

if __name__ == '__main__':
    main()