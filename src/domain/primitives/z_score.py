from typing import Optional

from src.domain.state.readiness import Readiness

from src.domain.primitives.moving_average import MovingAverage
from src.domain.primitives.standard_deviation import StandardDeviation

class ZScore:
    def __init__(self, window_size: int):
        if not isinstance(window_size, int) or isinstance(window_size, bool):
            raise TypeError(f"ZScore expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"ZScore expected window_size to be positive and non-zero, got {window_size}.")

        self._window_size: int = window_size
        self._moving_average = MovingAverage(window_size)
        self._standard_deviation = StandardDeviation(window_size)
        self._current: Optional[float] = None # Latest calculated standard deviation (only available if readiness is OPERATIONAL).

    @property
    def readiness(self) -> Readiness:
        """
        Calculate readiness state on the fly.
        If the buffer is full, we are operational. If not, we are warming up.
        Single source of truth, no risk of state duplication or redundancy.
        """
        if (self._moving_average.readiness == Readiness.OPERATIONAL) and (self._standard_deviation.readiness == Readiness.OPERATIONAL):
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
          - Advances the internal window/buffer.
          - Calculates and stores the `.current` property (if the `.readiness` property is `Readiness.OPERATIONAL`).
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
             raise TypeError(f"ZScore expected value to be a number, got {type(value).__name__}.")

        self._moving_average.update(value)
        mean = self._moving_average.current
        self._standard_deviation.update(value)
        sigma = self._standard_deviation.current

        if self.readiness != Readiness.OPERATIONAL:
            return None

        # NOTE: if readiness is OPERATIONAL, "mean" and "sigma" are guaranteed to be floats (instead of None).

        if sigma == 0:
            # Avoid division by zero.
            # Theoretically, if all values in the window are identical, sigma is 0.
            # Also, if all values are identical, "value - mean" would be "x - x"  which is also 0, so ZScore formula would be "0 / 0".
            # In this case, since the value and the mean are identical, and ZScore calculates the distance of the value from the mean in measures, the ZScore is 0.
            # i.e.: ZScore asks "how many standard deviations is this value away from the average", but the average is identical to the value, so 0.
            # So we return 0, even though "0 / 0" is mathematically indeterminate.
            # TODO: figure out if zero is indeed the correct return here.
            self._current = 0.0
            return

        # Z-Score: (Value - Mean) / Standard Deviation
        self._current = (value - mean) / sigma
