import os
import datetime
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():

    # Generate a unique folder BEFORE starting any node
    base_dir = os.path.expanduser("~/manip_logs")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = os.path.join(base_dir, f"logs_{timestamp}")
    os.makedirs(folder, exist_ok=True)

    # Path for rosbag inside same folder
    bag_path = os.path.join(folder, "rosbag")

    return LaunchDescription([

        # Logging node gets folder_path parameter
        Node(
            package="logger_pkg",
            executable="logging_node",
            name="logging_node",
            parameters=[{"folder_path": folder}],
        ),

        # rosbag stores directly inside our timestamped folder
        ExecuteProcess(
            cmd=[
                "ros2", "bag", "record",
                "/manipulator_cmd",
                "/bevel_cmd","--storage",
                "mcap",
                #"/manipulator_target",
                #"/bevel_target",
                "-o", bag_path
            ],
            shell=False
        )
    ])
