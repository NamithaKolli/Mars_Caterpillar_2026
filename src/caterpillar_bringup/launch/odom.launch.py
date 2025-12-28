import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Get Paths
    pkg_caterpillar = get_package_share_directory('caterpillar_bringup')
    ekf_yaml = os.path.join(pkg_caterpillar, 'config', 'ekf.yaml')

    # 1. Launch Camera
    cam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_caterpillar, 'launch', 'camera.launch.py')
        )
    )

    # 2. SLAM Launch (start after laun)
    camera_odom_slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_caterpillar, 'launch', 'check_odom.launch.py')
        )
    )

    # 3. EKF node (start AFTER SLAM)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[ekf_yaml],
    )

    delayed_ekf = TimerAction(
        period=8.0,   # must be > slam delay
        actions=[ekf_node]
    )
    
    delayed_slam = TimerAction(
        period=5.0,
        actions=[camera_odom_slam]
    )

    # 5. Return the list: Start SLAM immediately
    return LaunchDescription([
        cam_launch,
        delayed_slam,
        delayed_ekf,
    ])