import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image

class ImageRectifierNode(Node):
    def __init__(self):
        super().__init__("image_rectifier_node")
        
        self.declare_parameter("camera_matrix", [0.0] * 9) # map 3d point to 2d pixel
        self.declare_parameter("distortion_coeffs", [0.0] * 5) # radial distortion of cam
        self.declare_parameter("calib_width", 640)
        self.declare_parameter("calib_height", 480)
        self.declare_parameter("alpha", 0.0) # 0 cuts and zooms in so all pixels are valid, 1 leaves as is
        
        k = np.array(self.get_parameter("camera_matrix").value, dtype=np.float64)
        self._K = k.reshape(3,3) # make the cam_mat an actual matrix
        self._D = np.array(self.get_parameter("distortion_coeffs").value, dtype=np.float64)
        
        self._calib_size = (
            self.get_parameter("calib_width").value,
            self.get_parameter("calib_height").value,
        )
        self._alpha = self.get_parameter("alpha").value
        
        self._calibrated = self._K[0,0] > 0
        if not self._calibrated:
            self.get_logger().error(
                "Warning: the camera matrix is empty. Images passed through will remail unchanged."
            )
        
        self._bridge = CvBridge()
        self._map1 = None
        self._map2 = None
        self._map_size = None
        
        self._sub = self.create_subscription( # subscribes to image output node
            Image, "camera/image_raw", self._on_image, 10
        )
        self._pub = self.create_publisher(Image, "camera/image_rect", 10) # will publish good quality :)
        
    def _build_maps(self, width: int, height: int) -> None:
        sx = width / self._calib_size[0] # if the new camera is a different size, then well fix that (just trust the math)
        sy = height / self._calib_size[1]
        K = self._K.copy() # lets not mess up the original
        K[0,0] *= sx # scale fx by width
        K[0,2] *= sx # scale cx by width
        K[1,1] *= sy # scale fy by height
        K[1,2] *= sy # scale cy by height
        
        new_K, _roi = cv2.getOptimalNewCameraMatrix(
            K, self._D, (width, height), self._alpha
        )
        # corners get pushed in or out
        # alpha 0 zooms in so all pixels are valid but cut some pixels
        # alpha 1, leaves it as is
        
        self._map1, self._map2 = cv2.initUndistortRectifyMap(
            K, self._D, None, new_K, (width, height), cv2.CV_16SC2
        )
        
        # this is the lookup table from K to new_K stored in the cv2.CV_16SC format (AI approves) 👍
        
        self._map_size = (width, height)
        self.get_logger().info(f"Built rectification map for size {width}, {height}.")
        
    def _on_image(self, msg: Image) -> None:
        if not self._calibrated: # if it's not calibrated, no processing is necessary (because it'll do squat)
            self._pub.publish(msg)
            return
        
        frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        
        h, w = frame.shape[:2]
        
        if self._map_size != (w, h): # wrong sizing, we need to rebuild the map
            self._build_maps(w, h)
            
        rectified = cv2.remap(frame, self._map1, self._map2, cv2.INTER_LINEAR)
        # remaped frame acording to the settings specified
        
        out =  self._bridge.cv2_to_imgmsg(rectified, encoding="bgr8")
        out.header = msg.header # keep old header
        self._pub.publish(out)
        
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