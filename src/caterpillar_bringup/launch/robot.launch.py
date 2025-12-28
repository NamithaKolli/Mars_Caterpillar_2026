import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
# from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 1. Get Paths
    pkg_caterpillar = get_package_share_directory('caterpillar_bringup')
    pkg_nav2 = get_package_share_directory('nav2_bringup')
    rviz_config_file = os.path.join(pkg_caterpillar, 'rviz', 'nav2.rviz')


    # 1. Launch Camera
    cam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_caterpillar, 'launch', 'camera.launch.py')
        )
    )

    # 2. Define SLAM Launch (Your existing file)
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_caterpillar, 'launch', 'vslam.launch.py')
        )
    )

    # 3. Define Nav2 Launch
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_caterpillar, 'launch', 'navigation.launch.py')
        ),
    )

    # 3. Define Nav2 Launch
    rviz2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_caterpillar, 'launch', 'rviz.launch.py')
        ),
    )

    # 4. Create the "Delayed" Nav2 Action
    # This waits 10 seconds after the launch file starts before triggering Nav2
    delayed_slam = TimerAction(
        period=5.0,
        actions=[slam_launch]
    )
    
    delayed_nav2 = TimerAction(
        period=10.0,
        actions=[nav2_launch]
    )

    delayed_RVIZ = TimerAction(
        period=12.0,
        actions=[rviz2_launch]
    )

    # 5. Return the list: Start SLAM immediately, start Nav2 after 10s
    return LaunchDescription([
        cam_launch,
        delayed_slam,
        delayed_nav2,
        delayed_RVIZ,
        # odom_base,
        # base_camera

    ])