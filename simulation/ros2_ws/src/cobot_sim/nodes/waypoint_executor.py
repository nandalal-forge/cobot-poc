#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
import json
import paho.mqtt.client as mqtt
import threading

class WaypointExecutor(Node):
    def __init__(self):
        super().__init__('waypoint_executor')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.mqtt = mqtt.Client()
        self.mqtt.connect('localhost', 1883)
        self.mqtt.subscribe('cobot/waypoints')
        self.mqtt.on_message = self.on_waypoints
        self.mqtt.loop_start()
        self.get_logger().info('Waypoint executor ready')

    def on_waypoints(self, client, userdata, msg):
        waypoints = json.loads(msg.payload.decode())
        self.get_logger().info(f'Received {len(waypoints)} waypoints')
        thread = threading.Thread(target=self.execute_waypoints, args=(waypoints,))
        thread.start()

    def execute_waypoints(self, waypoints):
        for i, (x, y) in enumerate(waypoints):
            self.send_goal(x, y)
            self.mqtt.publish('cobot/progress',
                json.dumps({
                    'waypoint': i + 1,
                    'total': len(waypoints),
                    'percent': round((i + 1) / len(waypoints) * 100, 1)
                }))
            self.get_logger().info(f'Waypoint {i+1}/{len(waypoints)} done')

    def send_goal(self, x, y):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.pose.position.x = float(x)
        goal.pose.pose.position.y = float(y)
        goal.pose.pose.orientation.w = 1.0
        self._client.wait_for_server()
        self.get_logger().info(f'Navigating to ({x}, {y})')
        future = self._client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

def main():
    rclpy.init()
    rclpy.spin(WaypointExecutor())

if __name__ == '__main__':
    main()