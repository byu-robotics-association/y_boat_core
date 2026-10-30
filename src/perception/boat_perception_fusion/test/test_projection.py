from boat_perception_fusion.association.projection import (
    project_points,
    transform_points,
)
import numpy as np
from numpy.typing import NDArray
import pytest

FloatArray = NDArray[np.float64]


def make_transform(R: FloatArray, t: FloatArray) -> FloatArray:
    """Build a 4x4 homogeneous transform from a rotation and translation."""
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


# 90° rotation about z: x axis -> y axis
ROT_Z_90 = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])

# Camera optical frame in base_link (z forward, x right, y down), mounted at (0.2, 0, 0.5)
R_BASE_FROM_CAM = np.array([[0.0, 0.0, 1.0], [-1.0, 0.0, 0.0], [0.0, -1.0, 0.0]])
T_BASE_FROM_CAM = make_transform(R_BASE_FROM_CAM, np.array([0.2, 0.0, 0.5]))
T_CAM_FROM_BASE = np.linalg.inv(T_BASE_FROM_CAM)

# Ideal rectified camera: fx = fy = 700, principal point (640, 360)
FX = FY = 700.0
CX, CY = 640.0, 360.0
P: FloatArray = np.array([[FX, 0.0, CX, 0.0], [0.0, FY, CY, 0.0], [0.0, 0.0, 1.0, 0.0]])


def test_identity_leaves_points_unchanged():
    points = np.array([[1.0, 2.0, 3.0], [-4.0, 5.0, -6.0]])
    np.testing.assert_allclose(transform_points(points, np.eye(4)), points)


def test_pure_translation_shifts_every_point():
    points = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    T = make_transform(np.eye(3), np.array([1.0, 2.0, 3.0]))
    np.testing.assert_allclose(
        transform_points(points, T), [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]]
    )


def test_rotation_direction_is_correct():
    # Catches a missing transpose, which would rotate the opposite way (-> (0, -1, 0))
    points = np.array([[1.0, 0.0, 0.0]])
    T = make_transform(ROT_Z_90, np.zeros(3))
    np.testing.assert_allclose(
        transform_points(points, T), [[0.0, 1.0, 0.0]], atol=1e-12
    )


def test_rotation_is_applied_before_translation():
    # Rotate (1, 0, 0) to (0, 1, 0), then shift by (10, 0, 0)
    T = make_transform(ROT_Z_90, np.array([10.0, 0.0, 0.0]))
    np.testing.assert_allclose(
        transform_points(np.array([[1.0, 0.0, 0.0]]), T), [[10.0, 1.0, 0.0]], atol=1e-12
    )


def test_base_link_to_camera_optical_frame():
    # The buoy from the synthetic bag: 9.8 m ahead, 2 m left, 0.2 m below the lens
    buoy = np.array([[10.0, 2.0, 0.3]])
    np.testing.assert_allclose(
        transform_points(buoy, T_CAM_FROM_BASE), [[-2.0, 0.2, 9.8]], atol=1e-12
    )


def test_three_points_are_transformed_independently():
    # N == 3 makes the array square, where row/column mix-ups run without error
    points = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    T = make_transform(ROT_Z_90, np.zeros(3))
    np.testing.assert_allclose(
        transform_points(points, T),
        [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
        atol=1e-12,
    )


def test_round_trip_through_inverse_returns_original():
    rng = np.random.default_rng(0)
    points = rng.uniform(-50, 50, size=(100, 3))
    restored = transform_points(
        transform_points(points, T_CAM_FROM_BASE), T_BASE_FROM_CAM
    )
    np.testing.assert_allclose(restored, points, atol=1e-9)


def test_empty_input_returns_empty_array_transform():
    result = transform_points(np.zeros((0, 3)), T_CAM_FROM_BASE)
    assert result.shape == (0, 3)


@pytest.mark.parametrize(
    'points, T',
    [
        (np.zeros((5, 2)), np.eye(4)),  # points with the wrong number of columns
        (np.zeros((5, 3)), np.eye(3)),  # 3x3 rotation instead of a 4x4 transform
        (np.zeros(3), np.eye(4)),  # a single point as a 1-D array
    ],
)
def test_wrong_shapes_raise_transform(points: FloatArray, T: FloatArray):
    with pytest.raises(ValueError):
        transform_points(points, T)


def test_point_on_optical_axis_projects_to_principal_point():
    pixels = project_points(np.array([[0.0, 0.0, 20.0]]), P)
    np.testing.assert_allclose(pixels, [[CX, CY]])


def test_worked_example():
    # Buoy 9.8 m ahead, 2 m left, 0.2 m below the lens (see the math reference doc)
    pixels = project_points(np.array([[-2.0, 0.2, 9.8]]), P)
    np.testing.assert_allclose(pixels, [[497.142857, 374.285714]], rtol=1e-6)


def test_image_directions_follow_optical_frame():
    # +x is right (larger u), +y is down (larger v)
    pixels = project_points(np.array([[1.0, 0.0, 10.0], [0.0, 1.0, 10.0]]), P)
    assert pixels[0, 0] > CX and pixels[0, 1] == pytest.approx(CY)
    assert pixels[1, 1] > CY and pixels[1, 0] == pytest.approx(CX)


def test_doubling_distance_halves_offset_from_center():
    pixels = project_points(np.array([[1.0, 0.5, 10.0], [1.0, 0.5, 20.0]]), P)
    near_offset = pixels[0] - [CX, CY]
    far_offset = pixels[1] - [CX, CY]
    np.testing.assert_allclose(far_offset, near_offset / 2)


def test_points_behind_camera_are_nan_and_others_unaffected():
    points = np.array(
        [
            [-2.0, 0.2, 9.8],  # in front
            [1.0, -0.5, -3.0],  # behind
            [0.0, 0.0, 20.0],  # in front
        ]
    )
    pixels = project_points(points, P)

    assert np.isnan(pixels[1]).all()
    np.testing.assert_allclose(pixels[0], [497.142857, 374.285714], rtol=1e-6)
    np.testing.assert_allclose(pixels[2], [CX, CY])


@pytest.mark.parametrize(
    'z',
    [
        pytest.param(0.0, id='exactly-zero'),
        pytest.param(1e-3, id='equal-to-min-depth'),
        pytest.param(1e-6, id='below-min-depth'),
    ],
)
def test_points_at_or_too_close_to_camera_are_nan(z: float):
    pixels = project_points(np.array([[0.5, 0.5, z]]), P)
    assert np.isnan(pixels).all()


def test_custom_min_depth_is_respected():
    points = np.array([[0.0, 0.0, 0.5], [0.0, 0.0, 2.0]])
    pixels = project_points(points, P, min_depth=1.0)
    assert np.isnan(pixels[0]).all()
    np.testing.assert_allclose(pixels[1], [CX, CY])


def test_output_rows_line_up_with_input_rows():
    points = np.array(
        [[0.0, 0.0, -1.0], [1.0, 0.0, 10.0], [0.0, 0.0, -2.0], [0.0, 1.0, 10.0]]
    )
    pixels = project_points(points, P)

    assert pixels.shape == (4, 2)
    assert np.isnan(pixels[[0, 2]]).all()
    np.testing.assert_allclose(pixels[1], [CX + FX * 0.1, CY])
    np.testing.assert_allclose(pixels[3], [CX, CY + FY * 0.1])


def test_stereo_offset_column_is_applied():
    # Right camera of a stereo pair: Tx = -fx * baseline shifts u by -fx * B / Z
    baseline = 0.12
    P_right = P.copy()
    P_right[0, 3] = -FX * baseline

    pixels = project_points(np.array([[0.0, 0.0, 10.0]]), P_right)
    np.testing.assert_allclose(pixels, [[CX - FX * baseline / 10.0, CY]])


def test_all_points_behind_camera_returns_all_nan():
    pixels = project_points(np.array([[0.0, 0.0, -1.0], [1.0, 1.0, -5.0]]), P)
    assert pixels.shape == (2, 2)
    assert np.isnan(pixels).all()


def test_empty_input_returns_empty_array_project():
    pixels = project_points(np.zeros((0, 3)), P)
    assert pixels.shape == (0, 2)


@pytest.mark.parametrize(
    'points, projection',
    [
        pytest.param(np.zeros((5, 2)), P, id='points-wrong-columns'),
        pytest.param(np.zeros(3), P, id='single-point-1d'),
        pytest.param(np.zeros((5, 3)), P[:, :3], id='projection-3x3'),
        pytest.param(np.zeros((5, 3)), np.eye(4), id='projection-4x4'),
    ],
)
def test_wrong_shapes_raise_project(points: FloatArray, projection: FloatArray):
    with pytest.raises(ValueError):
        project_points(points, projection)


@pytest.mark.parametrize(
    'min_depth',
    [
        pytest.param(0.0, id='zero'),
        pytest.param(-1.0, id='negative'),
    ],
)
def test_non_positive_min_depth_raises(min_depth: float):
    with pytest.raises(ValueError):
        project_points(np.array([[0.0, 0.0, 10.0]]), P, min_depth=min_depth)
