from message_filters import ApproximateTimeSynchronizer, Subscriber
from rcl_interfaces.msg import FloatingPointRange, IntegerRange, ParameterDescriptor
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.utilities import try_shutdown
from sensor_msgs.msg import CameraInfo, PointCloud2
from std_msgs.msg import Header
from vision_msgs.msg import Detection2DArray, Detection3DArray
from visualization_msgs.msg import MarkerArray, Marker
from tf2_ros import Buffer, TransformListener
from geometry_msgs.msg import TransformStamped
from rclpy.time import Time
from .association.conversions import Obj_Estimate_to_Detection3D, TF_to_transform_matrix, det_msg_to_Detection_list, camera_info_to_P, pointcloud_to_Float_Array
from .association.projection import transform_points, project_points, points_in_box
from .association.types import ObjectEstimate
import numpy as np

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
        self.declare_parameter(
            'box_precision',
            .1,
            ParameterDescriptor(
                description='Percent of box detection box gets trimmed off for comparison to cloud',
                floating_point_range=[FloatingPointRange(from_value=0.0, to_value=.49)],
            )
        )

        sync_slop_value = self.get_parameter('sync_slop').value
        if not isinstance(sync_slop_value, (int, float)):
            raise TypeError('sync_slop must be a number')
        sync_slop = float(sync_slop_value)

        queue_size_value = self.get_parameter('queue_size').value
        if not isinstance(queue_size_value, int):
            raise TypeError('queue_size must be an integer')
        queue_size = int(queue_size_value)

        box_precision_value = self.get_parameter('box_precision').value
        if not isinstance(box_precision_value, (float)):
            raise TypeError('box_precision must be a float')
        self.box_precision = float(box_precision_value)

        self.camera_info = None

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self, spin_thread=True)

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

        self.debug_publisher = self.create_publisher(
            MarkerArray, 'objects/debug/selected_points', 10
        )
        return

    def on_synced(self, det_msg: Detection2DArray, cloud_msg: PointCloud2) -> None:
        """Handle a synced set of detection and point cloud messages."""
        # wait for camera info
        if self.camera_info is None:
            self.get_logger().warn('Waiting for camera_info', throttle_duration_sec=0.5)
            return

        # make sure we're getting detections from the correct camera
        if det_msg.header.frame_id != self.camera_info.header.frame_id:
            self.get_logger().warn(
                f'Detection frame "{det_msg.header.frame_id}" does not match camera frame '
                f'"{self.camera_info.header.frame_id}"; check the detector copies the image header',
                throttle_duration_sec=10.0)
            return

        # get latest transform from cloud to cam
        tf: TransformStamped = self.tf_buffer.lookup_transform(self.camera_info.header.frame_id, cloud_msg.header.frame_id, Time.from_msg(cloud_msg.header.stamp))

        # FRAMEWORK FOR BUILDING UP THE MARKER ARRAY
        # step 1 - convert all the ROS2 data into our python data types
        detection_list = det_msg_to_Detection_list(det_msg)
        pointcloud_data = pointcloud_to_Float_Array(cloud_msg)
        camera_pmatrix = camera_info_to_P(self.camera_info)
        tf_transform = TF_to_transform_matrix(tf)

        # step 2 - apply our numpy python helper functions to process the data

        # Transforms point cloud into camera coordinate frame
        transformed_pointcloud_data = transform_points(pointcloud_data, tf_transform)
        # Projects transformed points into 2D
        projected_pointcloud = project_points(transformed_pointcloud_data ,camera_pmatrix)
        # Create list of ObjectEstimates, iterate thru the detections, and turn them into ObjEstimates
        detection_3d_array = Detection3DArray()
        marker_array = MarkerArray()
        detection_3d_array.header = cloud_msg.header
        for detection_index, detection in enumerate(detection_list):
            trimmed_box = detection.box.shrunk(self.box_precision)
            cloud_mask = points_in_box(projected_pointcloud, trimmed_box)
            associated_points = pointcloud_data[cloud_mask]
            if associated_points.shape[0] == 0:
                # TO-DO, what will we do with a case of 0 points?
                pass
            elif associated_points.shape[0] == 1:
                # TO-DO, what will we do with a case of 1 point?
                pass
            else:
                num_points = associated_points.shape[0]       
                point_spread = np.cov(associated_points, rowvar=False)
                box_size = np.ptp(associated_points, axis=0)
                x_center = ((associated_points[:, 0].max() - associated_points[:,0].min()) / 2) + associated_points[:,0].min()
                y_center = ((associated_points[:, 1].max() - associated_points[:,1].min()) / 2) + associated_points[:,1].min()
                z_center = ((associated_points[:, 2].max() - associated_points[:,2].min()) / 2) + associated_points[:,2].min()
                box_position = [x_center, y_center, z_center]
                object_estimate = ObjectEstimate(detection, box_position, box_size, point_spread, num_points)
                detection_3d_array.detections.append(Obj_Estimate_to_Detection3D(object_estimate))
                marker = Marker()
                marker.header = cloud_msg.header
                marker.ns = 'object_boxes'
                marker.id = detection_index
                marker.type = Marker.CUBE
                marker.action = Marker.ADD

                marker.pose.position.x = object_estimate.position[0]
                marker.pose.position.y = object_estimate.position[1]
                marker.pose.position.z = object_estimate.position[2]
                marker.pose.orientation.w = 1.0  # identity rotation

                marker.scale.x = object_estimate.size[0]
                marker.scale.y = object_estimate.size[1]
                marker.scale.z = object_estimate.size[2]

                marker.color.r = 0.0
                marker.color.g = 1.0
                marker.color.b = 0.0
                marker.color.a = 0.5

                marker_array.markers.append(marker)


        # we can publish our selected points for each bounding box to this debug topic so we can see it in foxglove
        # TO-DO - implement debug switch that turns on/off the MarkerArray
        msg = marker_array

        self.debug_publisher.publish(msg)
        
        # right now, this is just going to publish an empty detection array
        msg = detection_3d_array
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
