#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import cv2
import numpy as np

from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32, Int16


class ArucoAlignedDepthNode(Node):
    def __init__(self):
        super().__init__('aruco_aligned_depth_node')

        self.bridge = CvBridge()

        # Camera intrinsics (COLOR camera)
        self.fx = self.fy = self.cx = self.cy = None

        self.depth_img = None

        # Thresholds
        self.thresh_dist = 0.15   # 15 cm → /thresh
        self.rohan_dist = 1.0     # 1 m   → /rohan

        # Marker IDs
        self.marker_ids = {
            1: "excavation",
            2: "construction",
            42: "priority"
        }

        # ---------------- PUBLISHERS ----------------
        self.pose_pubs = {
            name: self.create_publisher(
                PoseStamped, f"/{name}_pose", 10
            )
            for name in self.marker_ids.values()
        }

        self.goal_pub = self.create_publisher(PoseStamped, "/goal_pose", 10)
        self.thresh_pub = self.create_publisher(Float32, "/thresh", 10)
        self.rohan_pub = self.create_publisher(Int16, "/rohan", 10)

        # ---------------- SUBSCRIBERS ----------------
        self.create_subscription(
            Image,
            "/camera/realsense2_camera/color/image_raw",
            self.color_cb,
            10
        )

        self.create_subscription(
            Image,
            "/camera/realsense2_camera/aligned_depth_to_color/image_raw",
            self.depth_cb,
            10
        )

        self.create_subscription(
            CameraInfo,
            "/camera/realsense2_camera/color/camera_info",
            self.camera_info_cb,
            10
        )

        # ArUco
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_6X6_250
        )
        self.detector = cv2.aruco.ArucoDetector(
            self.aruco_dict, cv2.aruco.DetectorParameters()
        )

        self.get_logger().info("✅ ArUco with ALIGNED DEPTH node started")

    # ---------------- CALLBACKS ----------------

    def camera_info_cb(self, msg):
        if self.fx is None:
            self.fx = msg.k[0]
            self.fy = msg.k[4]
            self.cx = msg.k[2]
            self.cy = msg.k[5]

    def depth_cb(self, msg):
        self.depth_img = self.bridge.imgmsg_to_cv2(
            msg, desired_encoding="passthrough"
        )

    def color_cb(self, msg):
        if self.depth_img is None or self.fx is None:
            return

        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = self.detector.detectMarkers(gray)

        if ids is None:
            cv2.imshow("Aruco seen", frame)
            cv2.waitKey(1)
            return

        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        for i, marker_id in enumerate(ids.flatten()):
            if marker_id not in self.marker_ids:
                continue

            label = self.marker_ids[marker_id]
            c = corners[i][0]

            # ---------- CENTER PIXEL ----------
            u = int(np.mean(c[:, 0]))
            v = int(np.mean(c[:, 1]))

            depth_mm = self.depth_img[v, u]
            if depth_mm == 0:
                continue

            # ---------- TRUE METRIC DEPTH ----------
            Z = depth_mm / 1000.0
            X = (u - self.cx) * Z / self.fx
            Y = (v - self.cy) * Z / self.fy

            # ---------- POSE ----------
            pose = PoseStamped()
            pose.header.stamp = msg.header.stamp
            pose.header.frame_id = "camera_link"
            pose.pose.position.x = float(X)
            pose.pose.position.y = float(Y)
            pose.pose.position.z = float(Z)

            # Publish all original pose topics
            self.pose_pubs[label].publish(pose)
            self.goal_pub.publish(pose)

            # ---------- /thresh ----------
            if Z < self.thresh_dist:
                self.thresh_pub.publish(Float32(data=Z))

            # ---------- /rohan ----------
            if Z <= self.rohan_dist:
                if marker_id == 1:
                    self.rohan_pub.publish(Int16(data=1))
                elif marker_id == 2:
                    self.rohan_pub.publish(Int16(data=2))

            # ---------- VISUALIZATION ----------
            cv2.circle(frame, (u, v), 5, (0, 0, 255), -1)
            cv2.putText(
                frame,
                f"X:{X:.2f} Y:{Y:.2f} Z:{Z:.2f}",
                (u + 10, v - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        cv2.imshow("Aruco seen", frame)
        cv2.waitKey(1)


def main():
    rclpy.init()
    node = ArucoAlignedDepthNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
