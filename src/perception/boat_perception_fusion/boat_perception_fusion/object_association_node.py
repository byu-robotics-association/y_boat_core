from message_filters import ApproximateTimeSynchronizer, Subscriber
from rcl_interfaces.msg import FloatingPointRange, IntegerRange, ParameterDescriptor
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.utilities import try_shutdown
from sensor_msgs.msg import CameraInfo, PointCloud2
from std_msgs.msg import Header
from vision_msgs.msg import Detection2DArray, Detection3DArray


class ObjectAssociation(Node):
    """Read 2D detections and a lidar stream and turn them into 3D detections."""

    def __init__(self) -> None:
        super().__init__('object_association')

        self.declare_parameter(
            'sync_slop',
            0.05,
            ParameterDescriptor(
                description='Max timestamp difference (s) between paired detections and clouds',
                floating_point_range=[FloatingPointRange(from_value=0.0, to_value=1.0)],
            ),
        )
        self.declare_parameter(
            'queue_size',
            10,
            ParameterDescriptor(
                description='Number of buffered point cloud and detection messages',
                integer_range=[IntegerRange(from_value=1, to_value=20)],
            ),
        )

        sync_slop_value = self.get_parameter('sync_slop').value
        if not isinstance(sync_slop_value, (int, float)):
            raise TypeError('sync_slop must be a number')
        sync_slop = float(sync_slop_value)

        queue_size_value = self.get_parameter('queue_size').value
        if not isinstance(queue_size_value, int):
            raise TypeError('queue_size must be an integer')
        queue_size = int(queue_size_value)

        self.camera_info = None

        detection_subscription = Subscriber(self, Detection2DArray, 'camera/detections')
        lidar_subscription = Subscriber(
            self,
            PointCloud2,
            'lidar/point_cloud_rect',
            qos_profile=qos_profile_sensor_data,
        )
        self.create_subscription(
            CameraInfo,
            'camera/camera_info',
            self.on_camera_info,
            qos_profile=qos_profile_sensor_data,
        )

        self.syncronizer = ApproximateTimeSynchronizer(
            [detection_subscription, lidar_subscription],
            queue_size=queue_size,
            slop=sync_slop,
        )
        self.syncronizer.registerCallback(self.on_synced)

        self.publisher = self.create_publisher(
            Detection3DArray, 'objects/detections', 10
        )
        return

    def on_synced(self, det_msg: Detection2DArray, cloud_msg: PointCloud2) -> None:
        """Handle a synced set of detection and point cloud messages."""
        # wait for camera info
        if self.camera_info is None:
            self.get_logger().warn('Waiting for camera_info', throttle_duration_sec=0.5)
            return
        # right now, this is just going to publish an empty detection array
        msg = Detection3DArray()
        msg.header = Header(
            stamp=det_msg.header.stamp, frame_id=cloud_msg.header.frame_id
        )
        self.publisher.publish(msg)
        return

    def on_camera_info(self, camera_info: CameraInfo) -> None:
        """Handle updated camera_info."""
        self.camera_info = camera_info
        return


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ObjectAssociation()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try_shutdown()
