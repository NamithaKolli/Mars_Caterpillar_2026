# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String
# from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy
# import os

# class DataLogger(Node):
#     def __init__(self):
#         super().__init__("logging_node")

#         # Read folder path from launch parameter
#         self.folder = self.declare_parameter("folder_path", "").value

#         if not self.folder:
#             raise RuntimeError("folder_path parameter not provided!")

#         os.makedirs(self.folder, exist_ok=True)

#         self.get_logger().info(f"Logging to folder: {self.folder}")

#         # Create text files
#         self.files = {
#             "/manipulator_cmd": open(os.path.join(self.folder, "manipulator_cmd.txt"), "w"),
#             "/bevel_cmd": open(os.path.join(self.folder, "bevel_cmd.txt"), "w"),
#             "/manipulator_target": open(os.path.join(self.folder, "manipulator_target_encoder.txt"), "w"),
#             "/bevel_target": open(os.path.join(self.folder, "bevel_target_encoder.txt"), "w"),
#         }

#         qos = QoSProfile(
#             depth=50,
#             history=HistoryPolicy.KEEP_LAST,
#             reliability=ReliabilityPolicy.RELIABLE
#         )

#         # Subscribers
#         self.create_subscription(String, "/manipulator_cmd", self.cb("/manipulator_cmd"), qos)
#         self.create_subscription(String, "/bevel_cmd", self.cb("/bevel_cmd"), qos)
#         self.create_subscription(String, "/manipulator_target", self.cb("/manipulator_target"), qos)
#         self.create_subscription(String, "/bevel_target", self.cb("/bevel_target"), qos)

#     def cb(self, topic_name):
#         def callback(msg):
#             now = self.get_clock().now().nanoseconds / 1e9
#             self.files[topic_name].write(f"{now}: {msg}\n")
#             self.files[topic_name].flush()
#         return callback


# def main(args=None):
#     rclpy.init(args=args)
#     node = DataLogger()
#     rclpy.spin(node)
#     for f in node.files.values():
#         f.close()
#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == "__main__":
#     main()


























import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy
import os

class DataLogger(Node):
    def __init__(self):
        super().__init__("logging_node")

        # Parameter: folder path where logs will be saved
        self.folder = self.declare_parameter("folder_path", "").value

        if not self.folder:
            raise RuntimeError("folder_path parameter not provided!")

        os.makedirs(self.folder, exist_ok=True)

        self.get_logger().info(f"Logging to folder: {self.folder}")

        # Create text files for each topic
        self.files = {
            "/manipulator_cmd": open(os.path.join(self.folder, "manipulator_cmd.txt"), "w"),
            "/bevel_cmd": open(os.path.join(self.folder, "bevel_cmd.txt"), "w"),
            "/manipulator_target": open(os.path.join(self.folder, "manipulator_target_encoder.txt"), "w"),
            "/bevel_target": open(os.path.join(self.folder, "bevel_target_encoder.txt"), "w"),
        }

        # Reliable QoS for data logging
        qos = QoSProfile(
            depth=50,
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.RELIABLE
        )

        # Subscribers with correct message type Int16
        self.create_subscription(Int16, "/manipulator_cmd",
                                 self.cb("/manipulator_cmd"), qos)

        self.create_subscription(Int16, "/bevel_cmd",
                                 self.cb("/bevel_cmd"), qos)

        self.create_subscription(Int16, "/manipulator_target",
                                 self.cb("/manipulator_target"), qos)

        self.create_subscription(Int16, "/bevel_target",
                                 self.cb("/bevel_target"), qos)

    def cb(self, topic_name):
        def callback(msg):
            # high-precision timestamp
            timestamp = self.get_clock().now().nanoseconds / 1e9
            # log only the integer value
            self.files[topic_name].write(f"{timestamp}: {msg.data}\n")
            self.files[topic_name].flush()
        return callback


def main(args=None):
    rclpy.init(args=args)
    node = DataLogger()
    rclpy.spin(node)

    # Close all files on shutdown
    for f in node.files.values():
        f.close()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
