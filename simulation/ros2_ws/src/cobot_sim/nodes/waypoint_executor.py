#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import json
import paho.mqtt.client as mqtt

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
        for i, (x, y) in enumerate(waypoints):
            self.send_goal(x, y)
            self.mqtt.publish('cobot/progress',
                json.dumps({
                    'waypoint': i + 1,
                    'total': len(waypoints),
                    'percent': round((i + 1) / len(waypoints) * 100, 1)
                }))

    def send_goal(self, x, y):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.w = 1.0
        self._client.wait_for_server()
        future = self._client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f'Reached waypoint ({x}, {y})')

def main():
    rclpy.init()
    rclpy.spin(WaypointExecutor())

if __name__ == '__main__':
    main()