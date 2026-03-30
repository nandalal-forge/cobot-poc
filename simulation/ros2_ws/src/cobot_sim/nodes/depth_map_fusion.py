#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image
from cv_bridge import CvBridge
import numpy as np
import math

class DepthMapFusion(Node):
    """
    Fuses RealSense D435i depth image with LiDAR scan.
    Detects low obstacles the LiDAR misses and injects them
    into the scan as virtual points.
    """
    def __init__(self):
        super().__init__('depth_map_fusion')
        self.bridge = CvBridge()
        self.latest_depth = None
        self.latest_scan = None

        self.create_subscription(
            Image, '/camera/depth/image_rect_raw', self.depth_cb, 10)
        self.create_subscription(
            LaserScan, '/scan', self.scan_cb, 10)

        self.fused_pub = self.create_publisher(LaserScan, '/scan_fused', 10)
        self.get_logger().info('Depth-LiDAR fusion node started')

    def depth_cb(self, msg):
        self.latest_depth = self.bridge.imgmsg_to_cv2(msg, '32FC1')

    def scan_cb(self, msg):
        self.latest_scan = msg
        if self.latest_depth is not None:
            fused = self.fuse(msg)
            self.fused_pub.publish(fused)

    def fuse(self, scan: LaserScan) -> LaserScan:
        fused = LaserScan()
        fused.header = scan.header
        fused.angle_min = scan.angle_min
        fused.angle_max = scan.angle_max
        fused.angle_increment = scan.angle_increment
        fused.time_increment = scan.time_increment
        fused.scan_time = scan.scan_time
        fused.range_min = scan.range_min
        fused.range_max = scan.range_max
        fused.ranges = list(scan.ranges)

        depth = self.latest_depth
        h, w = depth.shape
        hfov = 1.5184
        mid_row = h // 2

        # Sample depth image centre row — map to scan angles
        for col in range(0, w, 8):
            d = float(depth[mid_row, col])
            if not math.isfinite(d) or d <= 0.1 or d > 5.0:
                continue
            angle = hfov * (col / w - 0.5)
            idx = int((angle - scan.angle_min) / scan.angle_increment)
            if 0 <= idx < len(fused.ranges):
                existing = fused.ranges[idx]
                if not math.isfinite(existing) or d < existing:
                    fused.ranges[idx] = d

        return fused

def main():
    rclpy.init()
    rclpy.spin(DepthMapFusion())

if __name__ == '__main__':
    main()