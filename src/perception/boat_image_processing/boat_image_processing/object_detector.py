import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray


class ObjectDetector(Node):
    def __init__(self) -> None:
        super().__init__('object_detector')
        self.get_logger().info('Object Detector started')

        self.image_subscription = self.create_subscription(
            Image,
            'camera/image_rect',
            self.on_image,
            # Standard default for image frames.
            qos_profile_sensor_data  # `BEST_EFFORT`, `KEEP_LAST`, `depth=5`
        )

        self.detection_publisher = self.create_publisher(
            Detection2DArray,
            'camera/detections',
            # Default is `RELIABLE`, which is probably what object_association will want.
            10  # `RELIABLE`, `KEEP_LAST`, `depth=10`
        )

    def on_image(self, image: Image) -> None:
        # Send an empty message with the same header received.
        self.detection_publisher.publish(Detection2DArray(header=image.header))


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ObjectDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
