#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraViewer(Node):
    def __init__(self):
        super().__init__('camera_viewer')
        self.bridge = CvBridge()
        self.create_subscription(
            Image, '/camera/color/image_raw', self.rgb_cb, 10)
        self.create_subscription(
            Image, '/camera/depth/image_rect_raw', self.depth_cb, 10)
        self.get_logger().info('Camera viewer started')
        self.get_logger().info('Press Q in the window to quit')

    def rgb_cb(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        cv2.imshow('RealSense D435i — RGB', frame)
        cv2.waitKey(1)

    def depth_cb(self, msg):
        depth = self.bridge.imgmsg_to_cv2(msg, '32FC1')
        import numpy as np
        depth_display = cv2.normalize(
            depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        depth_colormap = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)
        cv2.imshow('RealSense D435i — Depth', depth_colormap)
        cv2.waitKey(1)

def main():
    rclpy.init()
    node = CameraViewer()
    try:
        rclpy.spin(node)
    finally:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()