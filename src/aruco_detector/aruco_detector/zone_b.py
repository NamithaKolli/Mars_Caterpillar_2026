#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Int16


class SingleArucoInfiniteMission(Node):

    def __init__(self):
        super().__init__('single_aruco_encoder_mission')

        # ---------------- Publishers ----------------
        self.cmd_pub = self.create_publisher(Int16, '/steer_cmd', 10)
        self.rohan_pub = self.create_publisher(Int16, '/rohan', 10)
        self.encoder_reset_pub = self.create_publisher(Int16, '/encoder_reset', 10)

        # ---------------- Subscribers ----------------
        self.create_subscription(
            PoseStamped,
            '/excavation_pose',   # ArUco ID = 1 pose
            self.aruco_cb,
            10
        )

        self.create_subscription(
            Int16,
            '/vihaan',
            self.vihaan_cb,
            10
        )

        self.create_subscription(
            Int16,
            '/encoder_data',
            self.encoder_cb,
            10
        )

        # ---------------- Internal State ----------------
        self.marker_pose = None
        self.vihaan_state = 0
        self.encoder_data = 0

        self.state = 'WAIT_FOR_ARUCO'
        self.aruco_used = False   # ArUco triggers only once

        # Distance targets (×10 scale → Int16 safe)
        self.forward_target = 24   # 2.4 m
        self.backward_target = 27  # 2.7 m

        self.timer = self.create_timer(0.1, self.loop)

        self.get_logger().info("✅ Single ArUco Encoder-Based Infinite Mission Started")

    # ---------------- Callbacks ----------------

    def aruco_cb(self, msg):
        if not self.aruco_used:
            self.marker_pose = msg

    def vihaan_cb(self, msg):
        self.vihaan_state = msg.data

    def encoder_cb(self, msg):
        self.encoder_data = msg.data

    def send_cmd(self, value):
        self.cmd_pub.publish(Int16(data=value))

    def publish_rohan(self, value):
        self.rohan_pub.publish(Int16(data=value))
        # 🔁 ALSO RESET ENCODERS
        self.encoder_reset_pub.publish(Int16(data=1))

    # ---------------- Main FSM ----------------

    def loop(self):

        # ---------------- WAIT FOR ARUCO ----------------
        if self.state == 'WAIT_FOR_ARUCO':

            if self.marker_pose is None:
                return

            Z = self.marker_pose.pose.position.z

            if Z > 1.0:
                self.send_cmd(50)   # forward
            else:
                self.send_cmd(0)
                self.publish_rohan(1)

                self.get_logger().info("Reached 1m → rohan=1")
                self.aruco_used = True
                self.state = 'WAIT_VIHAAN_1'

        # ---------------- WAIT FOR VIHAAN = 1 ----------------
        elif self.state == 'WAIT_VIHAAN_1':

            if self.vihaan_state == 1:
                self.vihaan_state = 0
                self.encoder_data = 0
                self.state = 'FORWARD_2_4M'

        # ---------------- MOVE FORWARD 2.4m ----------------
        elif self.state == 'FORWARD_2_4M':

            self.send_cmd(50)

            if self.encoder_data >= self.forward_target:
                self.send_cmd(0)
                self.publish_rohan(2)

                self.get_logger().info("Forward 2.4m reached → rohan=2")
                self.state = 'WAIT_VIHAAN_2'

        # ---------------- WAIT FOR VIHAAN = 2 ----------------
        elif self.state == 'WAIT_VIHAAN_2':

            if self.vihaan_state == 2:
                self.vihaan_state = 0
                self.encoder_data = 0
                self.state = 'BACKWARD_2_7M'

        # ---------------- MOVE BACKWARD 2.7m ----------------
        elif self.state == 'BACKWARD_2_7M':

            self.send_cmd(25)   # reverse

            if self.encoder_data >= self.backward_target:
                self.send_cmd(0)
                self.publish_rohan(1)

                self.get_logger().info("Backward 2.7m reached → rohan=1")
                # 🔁 INFINITE LOOP
                self.state = 'WAIT_VIHAAN_1'


def main():
    rclpy.init()
    node = SingleArucoInfiniteMission()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
