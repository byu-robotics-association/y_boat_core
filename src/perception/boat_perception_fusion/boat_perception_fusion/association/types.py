from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

Vector3 = NDArray[np.float64]
Matrix3 = NDArray[np.float64]
FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class Box2D:
    """Bounding box in rectified image pixel coordinates"""
    cx: float
    cy: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width < 0 or self.height < 0:
            raise ValueError(f'Box size must be non-negative, got {self.width}x{self.height}')
    @property
    def left(self) -> float:
        return self.cx - self.width / 2

    @property
    def right(self) -> float:
        return self.cx + self.width / 2

    @property
    def top(self) -> float:
        return self.cy - self.height / 2

    @property
    def bottom(self) -> float:
        return self.cy + self.height / 2


@dataclass(frozen=True, slots=True)
class Detection:
    """A single 2D object detection"""
    box: Box2D
    class_id: str
    confidence: float
    id: str = ''

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f'Detection confidence must be in [0, 1], got {self.confidence}')

@dataclass(frozen=True, slots=True, eq=False)
class ObjectEstimate:
    """A detection with its estimated 3D position"""
    detection: Detection
    position: Vector3
    size: Vector3
    covariance: Matrix3
    # number of lidar points used for estimate
    num_points: int

    def __post_init__(self) -> None:
        # check data shape and create immutable np arrays
        for name, shape in (('position', (3,)), ('size', (3,)), ('covariance', (3, 3))):
            value = np.array(getattr(self, name), dtype=np.float64)
            if value.shape != shape:
                raise ValueError(f'{name} must have shape {shape}, got {value.shape}')
            value.flags.writeable = False
            object.__setattr__(self, name, value)
        # check that at least 1 point was used
        if self.num_points < 1:
            raise ValueError(f'num_points must be at least 1, got {self.num_points}')