"""Entry point for the boat LiDAR processor ROS 2 node."""

import rclpy
from rclpy.node import Node


class LidarProcessor(Node):
    """Represent the boat LiDAR processor node."""

    def __init__(self):
        """Initialize the ROS node and log that it has started."""
        super().__init__("lidar_processor")
        self.get_logger().info("Lidar processor started")


def main(args=None):
    """Start the node and release ROS resources when it stops."""
    rclpy.init(args=args)
    node = LidarProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
