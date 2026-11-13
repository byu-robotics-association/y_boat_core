import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


class ImageRectifierNode(Node):
    def __init__(self):
        super().__init__("image_rectifier_node")
        
        
        self.declare_parameter("alpha", 0.0) # 0 cuts and zooms in so all pixels are valid, 1 leaves as is
        self._alpha = self.get_parameter("alpha").value
        
        self._bridge = CvBridge()
        self._info = None
        self._map_key = None
        self._map1 = None
        self._map2 = None
        self._rect_info = None
        
        self.create_subscription(CameraInfo, "camera/camera_info", self._on_info, 10)
        self.create_subscription( # subscribes to image output node
            Image, "camera/image_raw", self._on_image, 10
        )
        self._pub = self.create_publisher(Image, "camera/image_rect", 10) # will publish good quality :)
        self._info_pub = self.create_publisher(CameraInfo, "camera/camera_info_rect", 10)

    def _on_info(self, msg: CameraInfo) -> None:
        self._info = msg        
        
    def _build_maps(self, info, width, height) -> None:
        K = np.array(info.k, dtype = np.float64).reshape(3,3)
        D = np.array(info.d, dtype = np.float64)
        
        if info.width > 0 and info.height > 0:
            sx = width / info.width # if the new camera is a different size, then well fix that (just trust the math)
            sy = height / info.height
            K[0,0] *= sx # scale fx by width
            K[0,2] *= sx # scale cx by width
            K[1,1] *= sy # scale fy by height
            K[1,2] *= sy # scale cy by height
        
        new_K, _roi = cv2.getOptimalNewCameraMatrix(
            K, D, (width, height), self._alpha
        )
        # corners get pushed in or out
        # alpha 0 zooms in so all pixels are valid but cut some pixels
        # alpha 1, leaves it as is
        
        self._map1, self._map2 = cv2.initUndistortRectifyMap(
            K, D, None, new_K, (width, height), cv2.CV_16SC2
        )
        
        # this is the lookup table from K to new_K stored in the cv2.CV_16SC format (AI approves) 👍
        
        rect = CameraInfo()
        rect.width = width
        rect.height = height
        rect.distortion_model = "plumb_bob"
        rect.d = [0.0] * 5
        rect.k = new_K.flatten().tolist()
        rect.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        rect.p = [
            new_K[0,0], 0.0, new_K[0,2], 0.0,
            0.0, new_K[1,1], new_K[1,2], 0.0,
            0.0,0.0,1.0,0.0
        ]
        self._rect_info = rect
        self.get_logger().info(f"Rectification maps built for {width}x{height}")
        
    def _on_image(self, msg: Image) -> None:
        info = self._info
        if info is None or info.k[0] <= 0:
            self.get_logger().warn(
                "No valid camera_info yet. Frame dropped.",
                throttle_duration_sec = 5.0
            )
            return
        
        frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        h, w = frame.shape[:2]
        
        key = (w, h, tuple(info.k), tuple(info.d), info.width, info.height)
        if key != self._map_key:
            self._build_maps(info, w, h)
            self._map_key = key
            
        rectified = cv2.remap(frame, self._map1, self._map2, cv2.INTER_LINEAR)
        
        out = self._bridge.cv2_to_imgmsg(rectified, encoding="bgr8")
        out.header = msg.header
        self._pub.publish(out)
        
        self._rect_info.header = msg.header
        self._info_pub.publish(self._rect_info)
        
def main():
    rclpy.init()
    node = ImageRectifierNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
                
if __name__ == "__main__":
    main()