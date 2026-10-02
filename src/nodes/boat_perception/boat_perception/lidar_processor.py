import rclpy
from rclpy.node import Node


class LidarProcessor(Node):
    def __init__(self) -> None:
        super().__init__('lidar_processor')
        self.get_logger().info('Lidar processor started')


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = LidarProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
