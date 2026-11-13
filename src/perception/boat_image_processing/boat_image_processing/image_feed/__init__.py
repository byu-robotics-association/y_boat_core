from collections.abc import Callable
from typing import TYPE_CHECKING, Dict

from .image_types.base import ImageFeed
from .image_types.synthetic_feed import SyntheticFeed
from .image_types.webcam_feed import WebcamFeed

if TYPE_CHECKING:
    from rclpy.node import Node

FEED_FACTORIES: dict[str, Callable[["Node"], ImageFeed]] = {
    "webcam": lambda node: WebcamFeed(
        device=node.get_parameter("webcam_device").value,
        width=node.get_parameter("image_width").value,
        height=node.get_parameter("image_height").value,
        fps=node.get_parameter("image_fps").value,
        fourcc=node.get_parameter("image_fourcc").value,
    ),
     "synthetic": lambda node: SyntheticFeed(
        width=node.get_parameter("image_width").value,
        height=node.get_parameter("image_height").value,
    ),
}

__all__ = ["FEED_FACTORIES", "ImageFeed", "SyntheticFeed", "WebcamFeed"]