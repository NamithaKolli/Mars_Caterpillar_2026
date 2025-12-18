import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid

import numpy as np
import math
from collections import defaultdict

from sensor_msgs_py import point_cloud2


class VoxelCostmapNode(Node):

    def __init__(self):
        super().__init__('voxel_costmap_node')

        # ---- Parameters ----
        self.voxel_size = 0.05        # meters
        self.hat_radius = 2           # voxels
        self.map_size = 10.0          # meters
        self.resolution = self.voxel_size

        self.ground_thresh = 0.05     # meters
        self.obstacle_thresh = 0.15   # meters

        # ---- ROS interfaces ----
        self.sub = self.create_subscription(
            PointCloud2,
            '/rtabmap/cloud_map',
            self.cloud_callback,
            10
        )

        self.pub = self.create_publisher(
            OccupancyGrid,
            '/voxel_costmap',
            10
        )

        self.get_logger().info("Voxel costmap Python node started")

    # -----------------------------------------------------

    def cloud_callback(self, msg: PointCloud2):

        # Map: (x, y) voxel → list of z values
        height_map = defaultdict(list)

        # Convert PointCloud2 → iterable xyz
        for p in point_cloud2.read_points(
                msg, field_names=('x', 'y', 'z'), skip_nans=True):

            x, y, z = p

            vx = int(math.floor(x / self.voxel_size))
            vy = int(math.floor(y / self.voxel_size))

            height_map[(vx, vy)].append(z)

        self.publish_costmap(height_map)

    # -----------------------------------------------------

    def publish_costmap(self, height_map):

        grid = OccupancyGrid()
        grid.header.stamp = self.get_clock().now().to_msg()
        grid.header.frame_id = 'map'

        width = int(self.map_size / self.resolution)
        height = int(self.map_size / self.resolution)

        grid.info.resolution = self.resolution
        grid.info.width = width
        grid.info.height = height

        grid.info.origin.position.x = -self.map_size / 2.0
        grid.info.origin.position.y = -self.map_size / 2.0
        grid.info.origin.orientation.w = 1.0

        grid.data = [-1] * (width * height)

        # ---- Iterate over 2D costmap cells ----
        for i in range(width):
            for j in range(height):

                mx = i - width // 2
                my = j - height // 2

                min_z = float('inf')
                found = False

                # -------- HAT AREA --------
                for dx in range(-self.hat_radius, self.hat_radius + 1):
                    for dy in range(-self.hat_radius, self.hat_radius + 1):

                        key = (mx + dx, my + dy)
                        if key not in height_map:
                            continue

                        for z in height_map[key]:
                            min_z = min(min_z, z)
                            found = True

                idx = j * width + i

                if not found:
                    grid.data[idx] = -1
                    continue

                # -------- HEIGHT → COST --------
                if min_z < self.ground_thresh:
                    grid.data[idx] = 0
                elif min_z < self.obstacle_thresh:
                    grid.data[idx] = 50
                else:
                    grid.data[idx] = 100

        self.pub.publish(grid)


# ---------------------------------------------------------

def main(args=None):
    rclpy.init(args=args)
    node = VoxelCostmapNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

