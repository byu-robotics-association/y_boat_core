import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

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
    
    # TR is a 4x4 homogeneous with R and t together
    # [R11 R12 R13 | T1]
    # [R21 R22 R23 | T2]
    # [R31 R32 R33 | T3]
    # [0   0   0   | 1 ]

    R = T[:3, :3] # rotation matrix
    t = T[:3, 3] # translation vector
    rotated_points = points @ R.T # points are rows (N, 3); p @ R.T == (R @ p) for row vectors
    translated_points = rotated_points + t
    return translated_points