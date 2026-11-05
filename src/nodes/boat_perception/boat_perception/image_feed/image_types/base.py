from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


class ImageFeed(ABC):
    """Common interface for anything that can produce BGR frames."""

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def read(self) -> Optional[np.ndarray]: ...

    @abstractmethod
    def close(self) -> None: ...
