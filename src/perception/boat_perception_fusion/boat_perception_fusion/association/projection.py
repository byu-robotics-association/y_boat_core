import numpy as np
from .types import FloatArray

def require_shape(name: str, array: FloatArray, shape: tuple[int | None, ...]) -> None:
    """Raise if `array` doesn't match `shape`; None matches any size in that dimension."""
    if array.ndim != len(shape) or any(
            expected is not None and actual != expected
            for actual, expected in zip(array.shape, shape)):
        pretty = tuple('N' if s is None else s for s in shape)
        raise ValueError(f'{name} must have shape {pretty}, got {array.shape}')

def transform_points(points: FloatArray, T: FloatArray) -> FloatArray:
    """Apply a transform to a set of points.
    
    points: (N, 3) points in the source frame, meters
    T:      (4, 4) homogeneous transform from the source frame to the target frame
    returns (N, 3) points in the target frame, meters
    """
    require_shape('points', points, (None, 3))
    require_shape('T', T, (4, 4))
    
    # T is a 4x4 homogeneous with R and t together
    # [R11 R12 R13 | T1]
    # [R21 R22 R23 | T2]
    # [R31 R32 R33 | T3]
    # [0   0   0   | 1 ]

    R = T[:3, :3] # rotation matrix
    t = T[:3, 3] # translation vector
    rotated_points = points @ R.T # points are rows (N, 3); p @ R.T == (R @ p) for row vectors
    translated_points = rotated_points + t
    return translated_points

def project_points(points_cam: FloatArray, P: FloatArray, min_depth: float = 1e-3) -> FloatArray:
    """Project points in the camera optical frame onto the rectified image.
    
    points_cam: (N, 3) points in the camera optical frame, meters
                (z forward out of the lens, x right, y down)
    P:          (3, 4) rectified projection matrix from CameraInfo
    min_depth:  points with z <= min_depth are treated as at or behind the camera, meters
    returns     (N, 2) pixel coordinates (u, v) (pixels to the right, pixels down) in the rectified image;
                rows for points at or behind the camera are NaN
    """
    require_shape('points_cam', points_cam, (None, 3))
    require_shape('P', P, (3, 4))
    if min_depth <= 0:
        raise ValueError(f'min_depth must be positive, got {min_depth}')

    # every row starts as NaN ("not visible"); only visible points get filled in below.
    pixels = np.full((len(points_cam), 2), np.nan) 

    # Keep only points far enough in front of the camera to project safely.
    in_front = points_cam[:, 2] > min_depth # Create a mask
    visible = points_cam[in_front] # Apply mask to points

    # append a 1 to each point, (M, 3) -> (M, 4), so P's fourth column (stereo offset) applies.
    ones = np.ones((len(visible), 1))
    homogeneous = np.hstack([visible, ones]) 

    projected = homogeneous @ P.T # (M, 4) @ (4, 3) -> (M, 3): (u', v', w')
    pixels[in_front] = projected[:, :2] / projected[:, 2:3]  # divide (u', v') by w'

    return pixels
