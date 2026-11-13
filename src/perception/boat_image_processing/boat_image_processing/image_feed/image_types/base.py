from abc import ABC, abstractmethod

import numpy as np


class ImageFeed(ABC):
    """Common interface for anything that can produce BGR frames."""

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def read(self) -> np.ndarray | None: ...

    @abstractmethod
    def close(self) -> None: ...
