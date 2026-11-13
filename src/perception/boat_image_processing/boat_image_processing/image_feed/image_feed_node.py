import yaml
from pathlib import Path
import rclpy # Ros library
from cv_bridge import CvBridge # converts image to Ros typle image
from rclpy.node import Node # node base class
from sensor_msgs.msg import CameraInfo, Image # image data type
from boat_image_processing.image_feed import FEED_FACTORIES, ImageFeed # feed types

REOPEN_AFTER_FAILURES = 30 # how many times reading can fail before restarting

class ImageFeedNode(Node):
    def __init__(self):
        super().__init__("image_feed_node")
        
        self.declare_parameter("feed_type", "synthetic") # type of data being read
        self.declare_parameter("publish_rate_hz", 10.0) # how fast we read and publish
        self.declare_parameter("frame_id", "camera") # what coordinate frame       
        
        rate_hz = self.get_parameter("publish_rate_hz").value
        if rate_hz <= 0: # hz must be a legal value
            raise ValueError(
                f"Publish_rate_hz '{rate_hz}' cannot be less than or equal to 0."
            )
        period = 1.0 / rate_hz  # seconds between timer callbacks
            
        
        # Camera Stuff
        self.declare_parameter("webcam_device", 0)
        self.declare_parameter("image_width", 640) # in pixels
        self.declare_parameter("image_height", 480)
        self.declare_parameter("image_fps", 30)
        self.declare_parameter("image_fourcc", "MJPG")
        
        self.declare_parameter("camera_info_file", "")
        self._info_publisher = self.create_publisher(CameraInfo, "camera/camera_info", 10)
        self._camera_info = self._load_camera_info()
        
        feed_type = self.get_parameter("feed_type").value
        if feed_type not in FEED_FACTORIES:
            raise ValueError(
                f"Unknown feed_type '{feed_type}'. Supported: {sorted(FEED_FACTORIES)}"
            )
        
        self._feed: ImageFeed = FEED_FACTORIES[feed_type](self)
        self._feed.open()
        
        self._bridge = CvBridge() # convert CV array to Image
        self._frame_id = self.get_parameter("frame_id").value
        self._publisher = self.create_publisher(Image, "camera/image_raw", 10)
        
        
        self._frames_published = 0
        self._failures = 0
        
        self._timer = self.create_timer(period, self._on_timer)
        self.get_logger().info(f"Publishing from '{feed_type}' feed at {rate_hz} Hz. Ctrl + C to stop.")
        
    def _on_timer(self) -> None:
        frame = self._feed.read()
        if frame is None: # Handle if no frame is found :/
            self._failures += 1
            self.get_logger().warn("Feed returned no frame", throttle_duration_sec=5.0)
            if self._failures >= REOPEN_AFTER_FAILURES:
                self._reopen_feed()
            return
        self._failures = 0
        
        h, w = frame.shape[:2]
        if (w, h) != (self._camera_info.width, self._camera_info.height):
            self.get_logger().warn(
                f"Mismatch between frame shape {w}x{h} and "
                f"calibration which is {self._camera_info.width}x{self._camera_info.height}",
                throttle_duration_sec = 5.0
            )

        msg = self._bridge.cv2_to_imgmsg(frame, encoding="bgr8") #converts frame in cv to Image
        stamp = self.get_clock().now().to_msg()
        msg.header.stamp = stamp
        msg.header.frame_id = self._frame_id
        
        self._camera_info.header.stamp = stamp
        self._camera_info.header.frame_id = self._frame_id
        
        self._publisher.publish(msg)
        self._info_publisher.publish(self._camera_info)
        
        self._frames_published += 1
        self.get_logger().info(
            f"Published {self._frames_published} frames so far", throttle_duration_sec=5.0 
        )
        
        
    def _reopen_feed(self) -> None:
        self.get_logger().warn(f"Reached {self._failures}/{REOPEN_AFTER_FAILURES} empty reads; reopening feed.")
        self._failures = 0
        self._feed.close()
        try:
            self._feed.open()
        except RuntimeError as exc:
            # after another set of empty reads, it will try again
            self.get_logger().error(str(exc), throttle_duration_sec=5.0)
            
    def _load_camera_info(self) -> CameraInfo:
        path = self.get_parameter("camera_info_file").value
        info = CameraInfo()
        
        if path:
            file = Path(path).expanduser()
            if not file.is_file():
                raise FileNotFoundError(f"camera_info_file '{path}' does not exist")
            # camera calibration stuff i dont understand, but uses YAML format
            data = yaml.safe_load(file.read_text())
            info.width = data["image_width"]
            info.height = data["image_height"]
            info.distortion_model = data["distortion_model"]
            info.d = [float(x) for x in data["distortion_coefficients"]["data"]]
            info.k = [float(x) for x in data["camera_matrix"]["data"]]
            info.r = [float(x) for x in data["rectification_matrix"]["data"]]
            info.p = [float(x) for x in data["projection_matrix"]["data"]]
            self.get_logger().info(f"Loaded camera calibration from {path}")
            return info
        
        width = self.get_parameter("image_width").value
        height = self.get_parameter("image_height").value
        fx = fy = float(width)
        cx, cy = width / 2.0, height / 2.0

        info.width = width
        info.height = height
        info.distortion_model = "plumb_bob"
        info.d = [0.0] * 5
        info.k = [fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0]
        info.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        info.p = [fx, 0.0, cx, 0.0, 0.0, fy, cy, 0.0, 0.0, 0.0, 1.0, 0.0]
        self.get_logger().warn(
            "No camera_info_file set: publishing PLACEHOLDER intrinsics. "
            "Do not trust 3D/pose results until you calibrate."
        )
        return info
            
    def destroy_node(self) -> bool:
        self._feed.close() # kill the camera feed
        return super().destroy_node() # node will do its stuff
    
def main():
    rclpy.init()
    node = ImageFeedNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass # terminate with ctrl + C
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
            
if __name__ == "__main__":
    main()
        