import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
import numpy as np
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import PointCloud2, Image
from sensor_msgs_py import point_cloud2 as pc2

class OpenCVHeatmap(Node):
    def __init__(self):
        super().__init__('opencv_heatmap')
        
        # --- Config ---
        self.map_size_meters = 20.0
        self.resolution = 0.05
        self.img_size = int(self.map_size_meters / self.resolution) 
        self.min_height = -1.0 
        self.max_height = 2.0  
        
        self.bridge = CvBridge()

        # --- KEY FIX: QoS Profile ---
        # We set "Transient Local" to ensure we receive the map 
        # even if it was published before we started the node.
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.sub = self.create_subscription(
            PointCloud2,
            '/cloud_map',  
            self.listener_callback,
            qos_profile) # <--- Using the custom QoS here
            
        self.pub = self.create_publisher(Image, '/heatmap_image', 1)
        self.get_logger().info("VISUALIZER STARTED (QoS: Transient Local). Waiting for data...")

    def listener_callback(self, msg):
        self.get_logger().info(f"Received Cloud with {msg.width * msg.height} points.") # Debug Print

        gen = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
        points_list = list(gen)
        
        if not points_list:
            return

        points_struct = np.array(points_list)
        x = points_struct['x']
        y = points_struct['y']
        z = points_struct['z']

        heatmap_grid = np.zeros((self.img_size, self.img_size), dtype=np.float32)

        center_offset = self.img_size // 2
        u = (x / self.resolution).astype(int) + center_offset
        v = (y / self.resolution).astype(int) + center_offset

        mask = (u >= 0) & (u < self.img_size) & (v >= 0) & (v < self.img_size)
        valid_u = u[mask]
        valid_v = v[mask]
        valid_z = z[mask]

        if valid_z.size == 0:
            return

        valid_z = np.clip(valid_z, self.min_height, self.max_height)
        norm_z = (valid_z - self.min_height) / (self.max_height - self.min_height)
        pixel_values = (norm_z * 255).astype(np.float32)

        flat_idx = valid_v * self.img_size + valid_u
        flat_grid = heatmap_grid.flatten()
        np.maximum.at(flat_grid, flat_idx, pixel_values)
        heatmap_grid = flat_grid.reshape(self.img_size, self.img_size)

        heatmap_uint8 = heatmap_grid.astype(np.uint8)
        kernel = np.ones((2,2), np.uint8)
        heatmap_uint8 = cv2.dilate(heatmap_uint8, kernel, iterations=1)
        color_image = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

        mask_empty = heatmap_uint8 == 0
        color_image[mask_empty] = [0, 0, 0] 

        # Display
        display_img = cv2.flip(color_image, 0) 
        cv2.imshow("Live Height Heatmap", display_img)
        cv2.waitKey(1)

        img_msg = self.bridge.cv2_to_imgmsg(color_image, encoding="bgr8")
        img_msg.header = msg.header 
        self.pub.publish(img_msg)

def main(args=None):
    rclpy.init(args=args)
    node = OpenCVHeatmap()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()