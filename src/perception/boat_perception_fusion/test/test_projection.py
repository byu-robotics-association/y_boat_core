import numpy as np
import pytest
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

from boat_perception_fusion.association.projection import transform_points

def make_transform(R: FloatArray, t: FloatArray) -> FloatArray:
    """Build a 4x4 homogeneous transform from a rotation and translation."""
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


# 90° rotation about z: x axis -> y axis
ROT_Z_90 = np.array([[0.0, -1.0, 0.0],
                     [1.0,  0.0, 0.0],
                     [0.0,  0.0, 1.0]])

# Camera optical frame in base_link (z forward, x right, y down), mounted at (0.2, 0, 0.5)
R_BASE_FROM_CAM = np.array([[0.0, 0.0, 1.0],
                            [-1.0, 0.0, 0.0],
                            [0.0, -1.0, 0.0]])
T_BASE_FROM_CAM = make_transform(R_BASE_FROM_CAM, np.array([0.2, 0.0, 0.5]))
T_CAM_FROM_BASE = np.linalg.inv(T_BASE_FROM_CAM)


def test_identity_leaves_points_unchanged():
    points = np.array([[1.0, 2.0, 3.0], [-4.0, 5.0, -6.0]])
    np.testing.assert_allclose(transform_points(points, np.eye(4)), points)


def test_pure_translation_shifts_every_point():
    points = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    T = make_transform(np.eye(3), np.array([1.0, 2.0, 3.0]))
    np.testing.assert_allclose(transform_points(points, T),
                               [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]])


def test_rotation_direction_is_correct():
    # Catches a missing transpose, which would rotate the opposite way (-> (0, -1, 0))
    points = np.array([[1.0, 0.0, 0.0]])
    T = make_transform(ROT_Z_90, np.zeros(3))
    np.testing.assert_allclose(transform_points(points, T), [[0.0, 1.0, 0.0]], atol=1e-12)


def test_rotation_is_applied_before_translation():
    # Rotate (1, 0, 0) to (0, 1, 0), then shift by (10, 0, 0)
    T = make_transform(ROT_Z_90, np.array([10.0, 0.0, 0.0]))
    np.testing.assert_allclose(transform_points(np.array([[1.0, 0.0, 0.0]]), T),
                               [[10.0, 1.0, 0.0]], atol=1e-12)


def test_base_link_to_camera_optical_frame():
    # The buoy from the synthetic bag: 9.8 m ahead, 2 m left, 0.2 m below the lens
    buoy = np.array([[10.0, 2.0, 0.3]])
    np.testing.assert_allclose(transform_points(buoy, T_CAM_FROM_BASE),
                               [[-2.0, 0.2, 9.8]], atol=1e-12)


def test_three_points_are_transformed_independently():
    # N == 3 makes the array square, where row/column mix-ups run without error
    points = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    T = make_transform(ROT_Z_90, np.zeros(3))
    np.testing.assert_allclose(transform_points(points, T),
                               [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]], atol=1e-12)


def test_round_trip_through_inverse_returns_original():
    rng = np.random.default_rng(0)
    points = rng.uniform(-50, 50, size=(100, 3))
    restored = transform_points(transform_points(points, T_CAM_FROM_BASE), T_BASE_FROM_CAM)
    np.testing.assert_allclose(restored, points, atol=1e-9)


def test_empty_input_returns_empty_array():
    result = transform_points(np.zeros((0, 3)), T_CAM_FROM_BASE)
    assert result.shape == (0, 3)


@pytest.mark.parametrize('points, T', [
    (np.zeros((5, 2)), np.eye(4)),   # points with the wrong number of columns
    (np.zeros((5, 3)), np.eye(3)),   # 3x3 rotation instead of a 4x4 transform
    (np.zeros(3), np.eye(4)),        # a single point as a 1-D array
])
def test_wrong_shapes_raise(points: FloatArray, T: FloatArray):
    with pytest.raises(ValueError):
        transform_points(points, T)