#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from nav2_msgs.action import NavigateToPose
import json
import paho.mqtt.client as mqtt
import threading

class WaypointExecutor(Node):
    def __init__(self):
        super().__init__('waypoint_executor')
        self.cb_group = ReentrantCallbackGroup()
        self._nav_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose',
            callback_group=self.cb_group)
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.connect('localhost', 1883)
        self.mqtt_client.subscribe('cobot/waypoints')
        self.mqtt_client.subscribe('cobot/command')
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.loop_start()
        self.running = False
        self.get_logger().info('Waypoint executor ready — waiting for waypoints')

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        if topic == 'cobot/waypoints':
            waypoints = json.loads(msg.payload.decode())
            self.get_logger().info(f'Received {len(waypoints)} waypoints')
            thread = threading.Thread(
                target=self.execute_waypoints,
                args=(waypoints,),
                daemon=True)
            thread.start()
        elif topic == 'cobot/command':
            cmd = json.loads(msg.payload.decode())
            if cmd.get('cmd') == 'stop':
                self.running = False
                self.get_logger().info('Stop command received')

    def execute_waypoints(self, waypoints):
        self.running = True
        total = len(waypoints)
        for i, (x, y) in enumerate(waypoints):
            if not self.running:
                self.get_logger().info('Execution stopped by command')
                break
            success = self.send_goal(float(x), float(y))
            progress = {
                'waypoint': i + 1,
                'total': total,
                'percent': round((i + 1) / total * 100, 1),
                'x': x, 'y': y,
                'success': success
            }
            self.mqtt_client.publish('cobot/progress', json.dumps(progress))
            self.get_logger().info(
                f'Waypoint {i+1}/{total} ({"OK" if success else "FAILED"})')
        self.running = False
        self.mqtt_client.publish('cobot/session_complete',
            json.dumps({'status': 'complete', 'total': total}))
        self.get_logger().info('All waypoints complete!')

    def send_goal(self, x: float, y: float) -> bool:
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.w = 1.0
        self._nav_client.wait_for_server()
        self.get_logger().info(f'Navigating to ({x}, {y})')
        event = threading.Event()
        result_container = {}

        def on_goal_response(future):
            handle = future.result()
            if not handle.accepted:
                self.get_logger().warn(f'Goal ({x},{y}) rejected')
                event.set()
                return
            result_future = handle.get_result_async()
            result_future.add_done_callback(
                lambda f: (result_container.update({'done': True}), event.set()))

        future = self._nav_client.send_goal_async(goal)
        future.add_done_callback(on_goal_response)
        event.wait(timeout=120.0)
        return result_container.get('done', False)

def main():
    rclpy.init()
    executor = MultiThreadedExecutor()
    node = WaypointExecutor()
    executor.add_node(node)
    executor.spin()

if __name__ == '__main__':
    main()