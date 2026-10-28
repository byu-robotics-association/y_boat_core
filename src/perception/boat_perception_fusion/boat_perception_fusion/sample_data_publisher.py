import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection3DArray


class SampleDataPublisher(Node):
    def __init__(self):
        super().__init__('sample_data_publisher')

        self.publisher = self.create_publisher(
            Detection3DArray,
            'objects/detections',
            10,
        )

        self.get_logger().info('Sample data publisher started')


def main(args=None):
    rclpy.init(args=args)

    node = SampleDataPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()