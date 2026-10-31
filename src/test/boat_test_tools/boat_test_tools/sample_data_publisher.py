import rclpy
from rclpy.node import Node
from rclpy.utilities import try_shutdown
from vision_msgs.msg import Detection3D, Detection3DArray, ObjectHypothesisWithPose

FRAME_ID = 'map'

BUOY_WIDTH = 0.5
BUOY_DEPTH = 0.5
BUOY_HEIGHT = 1.0

SAMPLE_BUOYS = [
    ('buoy_1', 'red_buoy', -1.25, 5.0),
    ('buoy_2', 'green_buoy', 1.25, 5.0),
    ('buoy_3', 'red_buoy', -1.25, 20.0),
    ('buoy_4', 'green_buoy', 1.25, 20.0)
]


class SampleDataPublisher(Node):
    """Publish fake buoy detections for navigation testing."""

    def __init__(self):
        super().__init__('sample_data_publisher')

        self.publisher = self.create_publisher(
            Detection3DArray,
            'objects/detections',
            10,
        )

        self.timer = self.create_timer(1.0, self.publish_sample_data)

        self.get_logger().info('Sample data publisher started')

    def publish_sample_data(self):
        """Publish sample buoy positions to the 'objects/detections' topic."""
        msg = Detection3DArray()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = FRAME_ID

        for buoy_id, class_id, x, y in SAMPLE_BUOYS:
            buoy = self.create_buoy(msg.header, buoy_id, class_id, x, y)
            msg.detections.append(buoy)

        self.publisher.publish(msg)

    def create_buoy(self, header, buoy_id, class_id, x, y, z=0.0):
        """Create and return a buoy of type Detection3D."""
        buoy = Detection3D()
        buoy.header = header
        buoy.id = buoy_id

        hypothesis = ObjectHypothesisWithPose()
        hypothesis.hypothesis.class_id = class_id
        hypothesis.hypothesis.score = 1.0

        hypothesis.pose.pose.position.x = x
        hypothesis.pose.pose.position.y = y
        hypothesis.pose.pose.position.z = z

        buoy.results.append(hypothesis)

        buoy.bbox.center.position.x = x
        buoy.bbox.center.position.y = y
        buoy.bbox.center.position.z = z

        buoy.bbox.size.x = BUOY_WIDTH
        buoy.bbox.size.y = BUOY_DEPTH
        buoy.bbox.size.z = BUOY_HEIGHT

        return buoy


def main(args=None):
    rclpy.init(args=args)

    node = SampleDataPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try_shutdown()


if __name__ == '__main__':
    main()
