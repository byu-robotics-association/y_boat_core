import math
from typing import Optional

import cv2
import numpy as np

from .base import ImageFeed


class SyntheticFeed(ImageFeed):
    """Generates a fake frame with a moving orange 'buoy' for testing."""

    def __init__(self, width: int = 640, height: int = 480):
        self._w = width
        self._h = height
        self._t = 0
        self._is_open = False

    def open(self) -> None:
        self._t = 0
        self._is_open = True

    def close(self) -> None:
        self._is_open = False

    def read(self) -> Optional[np.ndarray]:
        if not self._is_open:
            return None
        frame = np.full((self._h, self._w, 3), (120, 70, 20), np.uint8)  # BGR: blue-ish water
        cv2.rectangle(frame, (0, 0), (self._w, self._h // 3), (200, 170, 120), -1)  # "sky"
        x = int(self._w / 2 + (self._w / 3) * math.sin(self._t / 30))
        y = int(self._h * 0.6 + 30 * math.sin(self._t / 10))
        cv2.circle(frame, (x, y), 25, (0, 140, 255), -1)  # orange buoy
        cv2.putText(frame, f"frame {self._t}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        self._t += 1
        return frame