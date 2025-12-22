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
            output='screen',
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
            }]    
        ),


        # -------------------------------
        # RGBD Sync
        # -------------------------------
        Node(
            package='rtabmap_sync',
            executable='rgbd_sync',
            name='rgbd_sync',
            output='screen',
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
            output='screen',
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
        
        # -------------------------------
        # RGBD Odometry
        # -------------------------------
        Node(
            package='rtabmap_odom',
            executable='rgbd_odometry',
            name='rgbd_odometry',
            output='screen',
            parameters=[{
                'frame_id': 'camera_link',
                'odom_frame_id': 'odom',
                'publish_tf': True,
                'approx_sync': True,
                
            }],
            remappings=[
                ('/rgb/image', '/camera/realsense2_camera/color/image_raw'),
                ('/depth/image', '/camera/realsense2_camera/aligned_depth_to_color/image_raw'),
                ('/rgb/camera_info', '/camera/realsense2_camera/color/camera_info')
            ],
            arguments=['--verbose']
        ),

        # -------------------------------
        # RTAB-Map SLAM
        # -------------------------------
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=[{
                'frame_id': 'camera_link',
                'map_frame_id': 'map',
                'odom_frame_id': 'odom',
                'publish_tf': True,
                'subscribe_rgbd': True,
                'approx_sync': True,
                'approx_sync_max_interval': 0.02,
                'topic_queue_size': 30,   # default 10, increase if needed
                'sync_queue_size': 30,
                'database_path': os.path.join(
                    get_package_share_directory('realsense_vslam'),
                    'map',
                    'cat_map.db'
                    ),
                # 'Mem/IncrementalMemory': True, #Didnt work
                # 'rtabmap_args': '--delete_db_on_start',    # wrong
                # 'Rtabmap/PublishScene': 'true',    # REQUIRED: Publishes /rtabmap/cloud_map for OctoMap
                # 'Grid/FromDepth': 'true',          # OPTIONAL: Generates a 2D height map internally (saves you work!)
                # 'Mem/IncrementalMemory': 'true',   # 'true' = SLAM (Map building), 'false' = Localization only
                # 'Rtabmap/DetectionRate': '1',

                # # ---------- MAP FOR NAV2 ----------
                'Grid/FromDepth': 'true',     # <-- create 2D grid from depth
                'Grid/3D': 'false',           # <-- disable 3D occupancy grid
        	    'Grid/RangeMax': '5.0',       # optional
        	    'Grid/CellSize': '0.05',      # 5cm resolution (Nav2 friendly)
        	    'Grid/GroundIsObstacle': 'false',
            }],
            remappings=[
            ('/rgb/image', '/camera/realsense2_camera/color/image_raw'),
            ('/depth/image', '/camera/realsense2_camera/aligned_depth_to_color/image_raw'),
            ('/rgb/camera_info', '/camera/realsense2_camera/color/camera_info'),
            ('rgbd_image', '/rgbd_sync/rgbd_image'),
            ('odom', '/rgbd_odometry/odom'),
            ("/imu", "/rtabmap/imu")
            ],
            arguments=['--delete_db_on_start']
        ),

        # -------------------------------
        # Visualization
        # -------------------------------
        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            name='rtabmap_viz',
            output='screen',
            parameters=[{
                'frame_id': 'camera_link',
                'odom_frame_id': 'odom',
                'subscribe_odom_info' : True,
                'subscribe_rgbd': True,
                'subscribe_odom': True,
            }],
            remappings=[
                # Subscribe to the synced RGBD image and odometry topics
                ('rgbd_image', '/rgbd_sync/rgbd_image'),
                ('odom', '/rgbd_odometry/odom'),
                ('odom_info', '/odom_info')
            ]
        ),
    ])
