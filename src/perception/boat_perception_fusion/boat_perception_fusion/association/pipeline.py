from .types import ObjectEstimate, FloatArray, Detection
from .projection import transform_points, project_points, points_in_box
import numpy as np

def fuse_lidar_camera_data(
    pointcloud_data: FloatArray, 
    tf_transform: FloatArray, 
    camera_pmatrix: FloatArray, 
    detection_list: list[Detection],
    box_precision: float,
) -> list[ObjectEstimate]:
    """
    DESCRIPTION
        Takes in our custom Python objects converted from a ROS2 image and pointcloud, applies various transforms defined
        in the conversions.py and projections.py files, and returns a list of ObjectEstimate objects ready to be converted into
        a Detection3DArray, or MarkerArray in debugging mode
    PARAMETERS
        pointcloud_data: An (N,3) matrix with N LiDAR position data points
        tf_transform: A (4,4) transform matrix for LiDAR frame to the camera frame
        camera_pmatrix: A (3, 4) projection matrix for the rectified camera image
        detection_list: list of Detection objects for each object identified in camera image
        box_precision: A parameter we choose for how much bounding boxes are trimmed before mapping LiDAR points onto it
    """
    object_estimate_list = []

     # Transforms point cloud into camera coordinate frame
    transformed_pointcloud_data = transform_points(pointcloud_data, tf_transform)

    # Projects transformed points into 2D
    projected_pointcloud = project_points(transformed_pointcloud_data ,camera_pmatrix)

    # Processing each Detection from detection_list
    for detection in detection_list:

        # Trim each Detection bounding box by <box_precision> percent on each side
        if not 0.0 <= box_precision < 0.5:
            raise ValueError('box_precision must be in [0.0, 0.5)')
        trimmed_box = detection.box.shrunk(box_precision)

        # Determines which converted LiDAR data points are inside a Detection bounding box
        cloud_mask = points_in_box(projected_pointcloud, trimmed_box)
        associated_points = pointcloud_data[cloud_mask]

        # Handles different cases where 0, 1, or multiple LiDAR points are found inside a Detection bounding box
        if associated_points.shape[0] == 0:
            # TO-DO, what will we do with a case of 0 points?
            continue
        elif associated_points.shape[0] == 1:
            # TO-DO, what will we do with a case of 1 point?
            continue
        else:
            num_points = associated_points.shape[0]     

            # DESIGN DECISION: Build the covariance matrix with numpy cov. Currently our code does not implement this in a meaningful way  
            point_spread = np.cov(associated_points, rowvar=False)

            # DESIGN DECISION: Using the outer most points inside the box to determine size, does not account for outliers
            box_size = np.ptp(associated_points, axis=0)

            # DESIGN DECISION: Find the halfway point between furthest points
            x_center = ((associated_points[:, 0].max() - associated_points[:,0].min()) / 2) + associated_points[:,0].min()
            y_center = ((associated_points[:, 1].max() - associated_points[:,1].min()) / 2) + associated_points[:,1].min()
            z_center = ((associated_points[:, 2].max() - associated_points[:,2].min()) / 2) + associated_points[:,2].min()
            box_position = [x_center, y_center, z_center]

            object_estimate = ObjectEstimate(detection, box_position, box_size, point_spread, num_points)
            object_estimate_list.append(object_estimate)
    
    return object_estimate_list

