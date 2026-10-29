import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection3DArray, Detection3D, ObjectHypothesisWithPose


class SampleDataPublisher(Node):
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
        msg = Detection3DArray()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"

        buoy_1 = self.create_buoy(msg.header, "buoy_1", "red_buoy", -1.25, 5.0, 0.0)
        buoy_2 = self.create_buoy(msg.header, "buoy_2", "green_buoy", 1.25, 5.0, 0.0)
        buoy_3 = self.create_buoy(msg.header, "buoy_3", "red_buoy", -1.25, 20.0, 0.0)
        buoy_4 = self.create_buoy(msg.header, "buoy_4", "green_buoy", 1.25, 20.0, 0.0)

        msg.detections.append(buoy_1)
        msg.detections.append(buoy_2)
        msg.detections.append(buoy_3)
        msg.detections.append(buoy_4)

        self.publisher.publish(msg)

    def create_buoy(self, header, buoy_id, class_id, x, y, z):
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

        buoy.bbox.size.x = 0.5
        buoy.bbox.size.y = 0.5
        buoy.bbox.size.z = 1.0

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
        rclpy.shutdown()

if __name__ == '__main__':
    main()