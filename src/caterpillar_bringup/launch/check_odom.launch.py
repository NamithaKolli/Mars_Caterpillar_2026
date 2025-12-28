from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    return LaunchDescription([

        # -------------------------------
        # RGBD Odometry
        # -------------------------------
        Node(
            package='rtabmap_odom',
            executable='rgbd_odometry',
            name='rgbd_odometry',
            output='screen',
            parameters=[{
                'frame_id': 'base_link',
                'odom_frame_id': 'odom',
                'publish_tf': False,
                'approx_sync': True,
                
            }],
            remappings=[
                ('/rgb/image', '/camera/realsense2_camera/color/image_raw'),
                ('/depth/image', '/camera/realsense2_camera/aligned_depth_to_color/image_raw'),
                ('/rgb/camera_info', '/camera/realsense2_camera/color/camera_info')
                # Remapping odom data to odom_camera topic
                ('/odom', '/odom_camera')
            ],
            arguments=['--verbose']
        ),

    #     # -------------------------------
    #     # RTAB-Map SLAM
    #     # -------------------------------
    #     Node(
    #         package='rtabmap_slam',
    #         executable='rtabmap',
    #         name='rtabmap',
    #         # output='screen',
    #         parameters=[{
    #             'frame_id': 'base_link', #initially this was camera_link changed because loop closure was not happening
    #             'map_frame_id': 'map',
    #             'odom_frame_id': 'odom',
                
    #             'publish_tf': True,
    #             'subscribe_rgbd': True,
    #             'approx_sync': True,
    #             'approx_sync_max_interval': 0.02,
    #             'topic_queue_size': 30,   # default 10, increase if needed
    #             'sync_queue_size': 30,
                
    #             # # ---------- MAP FOR NAV2 ----------
    #             'Grid/FromDepth': 'true',     # <-- create 2D grid from depth
    #             'Grid/3D': 'false',           # <-- disable 3D occupancy grid
    #     	    'Grid/RangeMax': '5.0',       # optional
    #     	    'Grid/CellSize': '0.05',      # 5cm resolution (Nav2 friendly)
    #     	    'Grid/GroundIsObstacle': 'false',
                
    #             # # ----------- TEMPORARILY TURNING OFF IMU ----------
    #             # 'RGBD/UseIMU': False,
                
    #             # #------------ EXPLICITLY ENABLING LOOP CLOSURE -------
    #             # 'RGBD/OptimizeFromGraphEnd': False,
    #             # 'RGBD/LoopClosureReextractFeatures': True,

    #             # 'Mem/IncrementalMemory': True,
    #             # 'Mem/InitWMWithAllNodes': False,

    #             # 'Kp/MaxDepth': 5.0,
    #             # 'Kp/DetectorStrategy': 6,   # ORB (most stable)
                
    #             # #------------ DATABASE ------------
    #             # 'database_path': os.path.join(
    #             #     get_package_share_directory('realsense_vslam'),
    #             #     'map',
    #             #     'cat_map.db'
    #             #     ),
    #             # 'Mem/IncrementalMemory': True, #Didnt work
    #             # 'rtabmap_args': '--delete_db_on_start',    # wrong
    #         }],
    #         remappings=[
    #         ('/rgb/image', '/camera/realsense2_camera/color/image_raw'),
    #         ('/depth/image', '/camera/realsense2_camera/aligned_depth_to_color/image_raw'),
    #         ('/rgb/camera_info', '/camera/realsense2_camera/color/camera_info'),
    #         ('rgbd_image', '/rgbd_sync/rgbd_image'),
    #         ('odom', '/rgbd_odometry/odom'),
    #         ("/imu", "/rtabmap/imu")
    #         ],
    #         arguments=['--delete_db_on_start']
    #     ),

    #     # -------------------------------
    #     # Visualization
    #     # -------------------------------
    #     Node(
    #         package='rtabmap_viz',
    #         executable='rtabmap_viz',
    #         name='rtabmap_viz',
    #         # output='screen',
    #         parameters=[{
    #             'frame_id': 'base_link',
    #             'odom_frame_id': 'odom',
    #             'subscribe_odom_info' : True,
    #             'subscribe_rgbd': True,
    #             'subscribe_odom': True,
    #         }],
    #         remappings=[
    #             # Subscribe to the synced RGBD image and odometry topics
    #             ('rgbd_image', '/rgbd_sync/rgbd_image'),
    #             ('odom', '/rgbd_odometry/odom'),
    #             ('odom_info', '/odom_info')
    #         ]
    #     ),
    ])
