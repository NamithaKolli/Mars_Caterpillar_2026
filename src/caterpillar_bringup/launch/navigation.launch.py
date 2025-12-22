import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    pkg_nav2 = get_package_share_directory('nav2_bringup')
    pkg_caterpillar = get_package_share_directory('caterpillar_bringup')

    params_file = os.path.join(
        pkg_caterpillar,
        'config',
        'nav2_params.yaml'
    )

    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav2, 'launch', 'navigation_launch.py')
            ),
            launch_arguments={
                'params_file': params_file,
                'use_sim_time': use_sim_time,
                'autostart': 'true'
            }.items()
        ),
    ])
