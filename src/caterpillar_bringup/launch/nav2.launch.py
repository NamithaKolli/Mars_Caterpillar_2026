from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    nav2_params = LaunchConfiguration('nav2_params')
    bt_xml = LaunchConfiguration('bt_xml')
    rviz_config = os.path.join(
    get_package_share_directory('caterpillar_bringup'),
    'config',
    'nav2.rviz'
)

    return LaunchDescription([

        DeclareLaunchArgument(
            'nav2_params',
            default_value=os.path.join(
                get_package_share_directory('caterpillar_bringup'),
                'config',
                'nav2_params.yaml'
            )
        ),

        DeclareLaunchArgument(
            'bt_xml',
            default_value=os.path.join(
                get_package_share_directory('caterpillar_bringup'),
                'bt',
                'bt.xml'
            )
        ),

       

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config]
        ),

        Node(
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[nav2_params]
        ),

        Node(
            package='nav2_planner',
            executable='planner_server',
            output='screen',
            parameters=[nav2_params]
        ),

        Node(
            package='nav2_smoother',
            executable='smoother_server',
            output='screen',
            parameters=[nav2_params]
        ),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            output='screen',
            parameters=[nav2_params]
        ),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            output='screen',
            parameters=[nav2_params, {'default_bt_xml_filename': bt_xml}]
        ),

        # Node(
        #     package='nav2_costmap_2d',
        #     executable='nav2_costmap_2d',
        #     name='local_costmap',
        #     output='screen',
        #     parameters=[nav2_params]
        # ),

        # Node(
        #     package='nav2_costmap_2d',
        #     executable='nav2_costmap_2d',
        #     name='global_costmap',
        #     output='screen',
        #     parameters=[nav2_params]
        # ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            output='screen',
            parameters=[{
                'autostart': True,
                'node_names': [
                    'controller_server',
                    'planner_server',
                    'smoother_server',
                    'behavior_server',
                    'bt_navigator',
                    'local_costmap',
                    'global_costmap'
                ]
            }]
        )
    ])

