from typing import Optional, Union

import cv2
import numpy as np

from .base import ImageFeed


class WebcamFeed(ImageFeed):
    """Reads frames from a USB camera (incl. wide-angle) via OpenCV + V4L2."""

    def __init__(
        self,
        device: Union[int, str] = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
        fourcc: str = "MJPG",
    ):
        self._device = device
        self._width = width
        self._height = height
        self._fps = fps
        self._fourcc = fourcc
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        # CAP_V4L2 skips OpenCV's backend guessing, which is flaky in containers.
        cap = cv2.VideoCapture(self._device, cv2.CAP_V4L2)

        # Check BEFORE .set(): setting properties on a dead capture silently does nothing.
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(
                f"Could not open camera {self._device}. Check `ls /dev/video*`, that it is "
                "passed into the container, and that nothing else is using it. Docker "
                "Desktop on macOS/Windows can't pass cameras through; use feed_type:="
                "static_image there."
            )

        # FOURCC first: wide cams usually only give high res/fps in MJPG.
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*self._fourcc))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        cap.set(cv2.CAP_PROP_FPS, self._fps)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # always give YOLO the newest frame
        self._cap = cap

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def read(self) -> Optional[np.ndarray]:
        if self._cap is None:
            return None
        ok, frame = self._cap.read()
        return frame if ok else None