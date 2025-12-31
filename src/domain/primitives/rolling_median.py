import statistics
from collections import deque
from typing import Optional

from src.domain.state.readiness import Readiness

class RollingMedian:
    def __init__(self, window_size: int):
        if not isinstance(window_size, int):
            raise TypeError(f"RollingMedian expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"RollingMedian expected window_size to be positive and non-zero, got {window_size}.")

        self._window_size: int = window_size
        self._values: deque = deque(maxlen=window_size)
        self._current: Optional[float] = None  # Latest calculated rolling median (only available if readiness is OPERATIONAL).

    @property
    def readiness(self) -> Readiness:
        """
        Calculate readiness state on the fly.
        If the buffer is full, we are operational. If not, we are warming up.
        Single source of truth, no risk of state duplication or redundancy.
        """
        if len(self._values) == self._window_size:
            return Readiness.OPERATIONAL
        return Readiness.WARMING_UP

    @property
    def current(self) -> Optional[float]:
        if self.readiness != Readiness.OPERATIONAL:
            return None
        return self._current

    @property
    def window_size(self) -> int:
        return self._window_size

    def update(self, value: float):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it:
          - advances the internal window/buffer.
          - calculates and stores the `.current` property (if the `.readiness` property is `Readiness.OPERATIONAL`).
        """
        if not isinstance(value, (int, float)):
             raise TypeError(f"RollingMedian expected value to be a number, got {type(value).__name__}.")

        self._values.append(value) # Add new value. If full, deque automatically pops the oldest value.

        if self.readiness != Readiness.OPERATIONAL:
            return

        # statistics.median handles both odd and even window sizes correctly.
        # If odd: returns the middle element.
        # If even: returns the average of the two middle elements.
        self._current = statistics.median(self._values)
