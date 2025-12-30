#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import cv2
import numpy as np

from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32, Int16

from visualization_msgs.msg import Marker, MarkerArray
from aruco_msgs.msg import MarkerArray as ArucoMarkerArray
from aruco_msgs.msg import Marker as ArucoMarker


class ArucoAlignedDepthNode(Node):
    def __init__(self):
        super().__init__('aruco_aligned_depth_node')

        self.bridge = CvBridge()

        # ---------------- Camera intrinsics ----------------
        self.fx = self.fy = self.cx = self.cy = None
        self.depth_img = None

        # ---------------- Thresholds ----------------
        self.switch_dist = 1.0
        self.thresh_dist = 0.15

        # ---------------- ArUco IDs ----------------
        self.PRIORITY_ID = 1
        self.EXCAVATION_ID = 2
        self.HELPER_ID = 3

        # FSM state
        self.active_goal = self.PRIORITY_ID

        # ---------------- Publishers ----------------
        self.goal_pub = self.create_publisher(
            MarkerArray, "/goal_pose", 10
        )
        self.aruco_pub = self.create_publisher(
            ArucoMarkerArray, "/aruco/detections", 10
        )
        self.excavation_pub = self.create_publisher(
            Float32, "/excavation_pose", 10
        )
        self.helper_pose_pub = self.create_publisher(
            PoseStamped, "/helper_pose", 10
        )
        self.helper_id_pub = self.create_publisher(
            Int16, "/helper_id", 10
        )
        self.thresh_pub = self.create_publisher(
            Float32, "/thresh", 10
        )

        # ---------------- Subscribers ----------------
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

        # ---------------- ArUco detector ----------------
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_6X6_250
        )
        self.detector = cv2.aruco.ArucoDetector(
            self.aruco_dict,
            cv2.aruco.DetectorParameters()
        )

        self.get_logger().info("✅ ArUco detector with aruco_msgs + goal logic started")

    # ---------------------------------------------------
    # CALLBACKS
    # ---------------------------------------------------

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

    def publish_goal_marker(self, marker_id, pose_msg):
        marker = Marker()
        marker.header = pose_msg.header
        marker.id = marker_id
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose = pose_msg.pose
        marker.scale.x = 0.15
        marker.scale.y = 0.15
        marker.scale.z = 0.15
        marker.color.g = 1.0
        marker.color.a = 1.0

        ma = MarkerArray()
        ma.markers.append(marker)
        self.goal_pub.publish(ma)

    def color_cb(self, msg):
        if self.depth_img is None or self.fx is None:
            return

        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = self.detector.detectMarkers(gray)

        aruco_array = ArucoMarkerArray()
        aruco_array.header = msg.header

        if ids is None:
            self.aruco_pub.publish(aruco_array)
            cv2.imshow("Aruco", frame)
            cv2.waitKey(1)
            return

        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        for i, marker_id in enumerate(ids.flatten()):
            c = corners[i][0]
            u = int(np.mean(c[:, 0]))
            v = int(np.mean(c[:, 1]))

            depth_mm = self.depth_img[v, u]
            if depth_mm == 0:
                continue

            Z = depth_mm / 1000.0
            X = (u - self.cx) * Z / self.fx
            Y = (v - self.cy) * Z / self.fy

            pose = PoseStamped()
            pose.header.stamp = msg.header.stamp
            pose.header.frame_id = "camera_link"
            pose.pose.position.x = float(X)
            pose.pose.position.y = float(Y)
            pose.pose.position.z = float(Z)

            # ---------- aruco_msgs detection ----------
            aruco_marker = ArucoMarker()
            aruco_marker.id = int(marker_id)
            aruco_marker.pose.pose = pose.pose
            aruco_marker.pose.header = pose.header
            aruco_array.markers.append(aruco_marker)

            # ---------- safety ----------
            if Z < self.thresh_dist:
                self.thresh_pub.publish(Float32(data=Z))

            # ---------- helper ----------
            if marker_id == self.HELPER_ID:
                self.helper_pose_pub.publish(pose)
                self.helper_id_pub.publish(Int16(data=self.HELPER_ID))

            # ---------- priority ----------
            if self.active_goal == self.PRIORITY_ID and marker_id == self.PRIORITY_ID:
                self.publish_goal_marker(marker_id, pose)
                if Z <= self.switch_dist:
                    self.active_goal = self.EXCAVATION_ID
                    self.get_logger().info("Priority reached → Excavation active")

            # ---------- excavation ----------
            if self.active_goal == self.EXCAVATION_ID and marker_id == self.EXCAVATION_ID:
                self.publish_goal_marker(marker_id, pose)
                self.excavation_pub.publish(Float32(data=Z))

            cv2.putText(
                frame,
                f"ID:{marker_id} Z:{Z:.2f}m",
                (u + 10, v - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        self.aruco_pub.publish(aruco_array)

        cv2.imshow("Aruco", frame)
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
