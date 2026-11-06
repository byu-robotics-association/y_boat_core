# Our utility functions for converting from ROS2 types to numpy/our internal types goes here
import numpy as np
from sensor_msgs.msg import PointCloud2, CameraInfo
from sensor_msgs_py import point_cloud2
from vision_msgs.msg import Detection2DArray, Detection3DArray
from .types import Detection, Box2D, FloatArray, ObjectEstimate
from tf2_ros import TransformStamped

# CONVERSION #1 - Convert det_msg into a list of detection objects

def det_msg_to_Detection_list(det_msg: Detection2DArray) -> list[Detection]:
    """
    DESCRIPTION
    Creates a list of Detection (numpy) objects by converting the ROS2 array of detections

    PARAMETERS
    det_msg: The ROS2 data type. It stores a header including the array of detections,
    a class_id, a confidence score that tells us how confident the YOLO algortihm is, and a detection_id
    """
    detection_list: list[Detection] = []

    for detection in det_msg.detections:

        newBox2D: Box2D = Box2D(
            cx=detection.bbox.center.x,
            cy=detection.bbox.center.y, 
            width=detection.bbox.size_x, 
            height=detection.bbox.size_y
        )      
        
        #parse thru the results and id data - choose the highest confidence score and associated ID
        if detection.results:
            best_result = max(detection.results, key = lambda result: result.hypothesis.score,)
            newDetection: Detection = Detection(
                box=newBox2D, 
                class_id=best_result.hypothesis.class_id, 
                confidence=best_result.hypothesis.score, 
                detection_id=detection.id,
            )
            detection_list.append(newDetection)

    return detection_list

# CONVERSION #2 - Convert PointCloud2 to XYZ Float Array
def pointcloud_to_Float_Array(pointcloud_msg: PointCloud2) -> FloatArray:
    """
    DESCRIPTION
    Creates an (N, 3) matrix of all the coordinates of the point cloud

    PARAMETERS
    pointcloud_msg: Contains metadata about timestamp, frame_id, and all the point cloud points
    """
    pointcloud_data: FloatArray = point_cloud2.read_points_numpy(
        pointcloud_msg,
        field_names=['x','y','z'],
        skip_nans=False,
    )

    pointcloud_data = pointcloud_data.astype(np.float64)
    return pointcloud_data

# CONVERSION #3 - Convert Camera Info into P transformation matrix
def camera_info_to_P(camera_info: CameraInfo) -> FloatArray:
    """
    DESCRIPTION
    Creates a (3, 4) P transform matrix to rectify the camera image

    PARAMETERS
    camera_info: Contains information about the camera used to build the rectifying P transform matrix
    """
    p:FloatArray = np.asarray(camera_info.p, dtype=np.float64).reshape(3, 4)
    return p

# CONVERSION #4 - Convert TF Transform into 4x4 transform matrix
def TF_to_transform_matrix(tf: TransformStamped) -> FloatArray:
    """
    DESCRIPTION
    Creates a (4, 4) transform matrix for converting point cloud coordinate space to the camera's

    PARAMETERS
    tf: The transform data created by the tf2 package
    """
    transform_matrix:FloatArray[0, 0] = tf.transform.translation.x
    transform_matrix[1, 1] = tf.transform.translation.y
    transform_matrix[2, 2] = tf.transform.translation.z
    transform_matrix[:, 0] = tf.transform.rotation.x
    transform_matrix[:, 1] = tf.transform.rotation.y
    transform_matrix[:, 2] = tf.transform.rotation.z
    transform_matrix[:, 3] = tf.transform.rotation.w

    return transform_matrix

# CONVERSION #5 - Convert ObjectEstimate into Detection3D, and collect it into a Detection3DArray
def Obj_Estimate_to_Detection3D(estimate: ObjectEstimate) -> Detection3DArray:
    pass
    # This only does one Detection3D object - but we need the whole array?


