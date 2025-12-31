import math
from typing import Optional

from src.domain.state.readiness import Readiness

class LogReturn:
    def __init__(self):
        # We only need to remember the last value seen.
        # Initialized to None to represent the "warming up" state.
        self._last_value: Optional[float] = None # Last value seen.
        self._current: Optional[float] = None # Latest calculated log return (only available if readiness is OPERATIONAL).

    @property
    def readiness(self) -> Readiness:
        """
        Calculate readiness state on the fly.
        If we have a last seen value and a current value, we are operational. If not, we are warming up.
        """
        if self._last_value is not None and self._current is not None:
            return Readiness.OPERATIONAL
        return Readiness.WARMING_UP

    @property
    def current(self) -> Optional[float]:
        if self.readiness != Readiness.OPERATIONAL:
            return None
        return self._current

    def update(self, value: float):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it:
          - Calculates and stores the `.current` property (only after the first last seen value, i.e. when the `._last_value` property is NOT `None`).
          - Updates the internal last seen value.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"LogReturn expected value to be a number, got {type(value).__name__}.")

        if value <= 0:
            raise ValueError(f"LogReturn expected value > 0 to calculate log return, got {value}.")

        if self._last_value is None:
            # BOOTSTRAPPING:
            # If this is the first value, we store it but cannot calculate a return yet.
            self._last_value = value
            return

        # CALCULATION:
        # We use log(A/B) instead of log(A) - log(B) because it is numerically
        # more stable (avoids catastrophic cancellation when A ~= B) and faster.
        self._current = math.log(value / self._last_value)

        # Update buffer for the next step
        self._last_value = value
