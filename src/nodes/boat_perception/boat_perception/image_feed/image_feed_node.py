import rclpy # Ros library
from cv_bridge import CvBridge # converts image to Ros typle image
from rclpy.node import Node # node base class
from sensor_msgs.msg import Image # image data type
from boat_perception.image_feed import FEED_FACTORIES, ImageFeed # feed types

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

        msg = self._bridge.cv2_to_imgmsg(frame, encoding="bgr8") #converts frame in cv to Image
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self._frame_id
        self._publisher.publish(msg)
        
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
        