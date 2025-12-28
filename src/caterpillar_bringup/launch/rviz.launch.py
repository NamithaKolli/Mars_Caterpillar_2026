import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_name = 'caterpillar_bringup'   
    pkg_share = get_package_share_directory(pkg_name)

    rviz_config = os.path.join(pkg_share, 'rviz', 'nav2.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config]
    )

    return LaunchDescription([
        rviz_node
    ])
