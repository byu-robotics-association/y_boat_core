import time
from typing import Callable, Iterator

from boat_image_processing.object_detector import ObjectDetector
import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray

TIMEOUT_SEC = 5.0

# The executor that's handling both nodes, and the helper node separately.
Harness = tuple[SingleThreadedExecutor, Node]


@pytest.fixture
def harness() -> Iterator[Harness]:
    """
    Run an ObjectDetector alongside a helper node that talks to it.

    The helper node is what the tests will interface with - adding
    subscribers and listeners.
    """
    rclpy.init()
    executor = SingleThreadedExecutor()

    detector = ObjectDetector()
    executor.add_node(detector)

    helper_node = Node('object_detector_test_helper')
    executor.add_node(helper_node)

    try:
        yield executor, helper_node
    finally:
        # Runs after each test finishes
        executor.shutdown()
        detector.destroy_node()
        helper_node.destroy_node()
        rclpy.shutdown()


def spin_until(
    executor: SingleThreadedExecutor,
    condition: Callable[[], bool],
    timeout_sec: float = TIMEOUT_SEC,
) -> bool:
    """Spin the executor until `condition()` is true or the timeout expires."""
    end = time.monotonic() + timeout_sec
    while time.monotonic() < end:
        if condition():
            return True
        executor.spin_once(timeout_sec=0.05)
    return condition()


def test_detector_subscribes_to_images(harness: Harness) -> None:
    executor, helper_node = harness
    image_pub = helper_node.create_publisher(Image, 'camera/image_rect', qos_profile_sensor_data)

    # Run the nodes and make sure there's at least one subscriber
    assert spin_until(executor, lambda: image_pub.get_subscription_count() > 0), \
        'ObjectDetector never subscribed to camera/image_rect'


def test_detector_advertises_detections(harness: Harness) -> None:
    executor, helper_node = harness
    received: list[Detection2DArray] = []
    helper_node.create_subscription(Detection2DArray, 'camera/detections', received.append, 10)

    # Runs the node and makes sure there's at least one publisher
    assert spin_until(executor, lambda: helper_node.count_publishers('camera/detections') > 0), \
        'ObjectDetector never published camera/detections'
