import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # 1. Get Directory Paths
    my_pkg_dir = get_package_share_directory('caterpillar_bringup')
    nav2_dir = get_package_share_directory('nav2_bringup')

    # 2. Define Configuration Variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    
    # Point to your custom params file (The one with the Voxel Layer config)
    params_file = os.path.join(my_pkg_dir, 'config', 'nav2_params.yaml')

    return LaunchDescription([
        
        # 3. Launch Nav2 "Navigation Component" ONLY
        # We use 'navigation_launch.py' instead of 'bringup_launch.py'
        # because RTAB-Map is already handling Localization (AMCL) and Mapping.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2_dir, 'launch', 'navigation.launch.py')),
            launch_arguments={
                'params_file': params_file,
                'use_sim_time': use_sim_time,
                'autostart': 'true',  # Automatically transition nodes to Active
                'use_composition': 'True' # Optimizes CPU usage
            }.items()
        ),
    ])