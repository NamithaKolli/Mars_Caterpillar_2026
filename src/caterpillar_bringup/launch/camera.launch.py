from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    return LaunchDescription([

        # -------------------------------
        # RealSense Camera
        # -------------------------------
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='realsense2_camera',
            # output='screen',
            parameters=[{
                'enable_color': True,
                'enable_depth': True,
                'enable_gyro': True,
                'enable_accel': True,
                'align_depth.enable': True,
                'unite_imu_method': 1,
                # 'color_width': 848,    # match depth width #Didnt work
                # 'color_height': 480,   # match depth height #--
                # 'color_fps': 30,
                'enable_depth': True,
                # 'depth_width': 848,    # match color width #--
                # 'depth_height': 480,   # match color height #--
                # 'depth_fps': 30,
                'pointcloud.enable': True,

            }]    
        ),


        # -------------------------------
        # RGBD Sync
        # -------------------------------
        Node(
            package='rtabmap_sync',
            executable='rgbd_sync',
            name='rgbd_sync',
            # output='screen',
            parameters=[{
                'approx_sync': True,              # Enable approximate sync for timestamp jitter
                'approx_sync_max_interval': 0.05, # 50 ms tolerance
                'topic_queue_size': 30,
                'sync_queue_size': 30
            }],
            remappings=[
                ('rgb/image', '/camera/realsense2_camera/color/image_raw'),
                ('depth/image', '/camera/realsense2_camera/aligned_depth_to_color/image_raw'),
                ('rgb/camera_info', '/camera/realsense2_camera/color/camera_info'),
                ('rgbd_image', '/rgbd_sync/rgbd_image')  # Output topic
            ]
        ),



        # -------------------------------
        # IMU Transformation
        # -------------------------------
        Node(
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='imu_filter',
            # output='screen',
            parameters=[{
                'use_mag': False,
                'publish_tf': False,
                'world_frame': 'enu'
            }],
            remappings=[
                # Input: The topic created by unite_imu_method above
                ('/imu/data_raw', '/camera/realsense2_camera/imu'), 
                # Output: The corrected topic RTAB-Map will listen to
                ('/imu/data', '/rtabmap/imu')
            ]
        ),

        #Node(
         #       package='caterpillar_bringup',  
           #     executable='odom_to_base_link',   # dynamic transform node
            #    name='odom_to_base_link',
             #   #output='screen'
            #),

        # Static transform from base_link -> camera_link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_camera',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'camera_link'],
            #output='screen'
        )
])