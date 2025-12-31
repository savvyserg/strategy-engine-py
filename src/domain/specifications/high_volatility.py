from src.domain.state import Readiness

from src.domain.primitives import LogReturn
from src.domain.primitives import RollingMedian
from src.domain.primitives import StandardDeviation

class HighVolatilitySpecification:
    """
    Determine if the market has high activity (volatility).

    This is a stateful component that owns the 'LogReturn', 'StandardDeviation' (volatility) and 'RollingMedian' primitives, it:
    - Ingests a stream of prices and turns them into Log Returns to calculate volatility.
    - Internally maintains the volatility within a given window.
    - Internally maintains a median of that volatility within the same window.
    - Compares the volatility with the median of the volatility within the window.
    """
    def __init__(self, window_size: int):
        if not isinstance(window_size, int):
            raise TypeError(f"HighVolatilitySpecification expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"HighVolatilitySpecification expected window_size to be positive and non-zero, got {window_size}.")

        self._log_return:LogReturn = LogReturn()
        self._window_size: int = window_size
        self._standard_deviation: StandardDeviation = StandardDeviation(window_size=window_size)
        self._rolling_median: RollingMedian = RollingMedian(window_size=window_size)

    @property
    def readiness(self) -> Readiness:
        """
        Bubble up the readiness of the internal machinery.
        The client should check this before calling 'is_satisfied()'.
        """
        if (
            self._log_return.readiness == Readiness.OPERATIONAL and
            self._standard_deviation.readiness == Readiness.OPERATIONAL and
            self._rolling_median.readiness == Readiness.OPERATIONAL
        ):
            return Readiness.OPERATIONAL
        return Readiness.WARMING_UP

    @property
    def window_size(self) -> int:
        return self._window_size

    def update(self, value: float):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it advances the internal windows/buffers.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"HighVolatilitySpecification expected value to be a number, got {type(value).__name__}.")

        self._log_return.update(value)
        if self._log_return.readiness == Readiness.OPERATIONAL:            
          self._standard_deviation.update(self._log_return.current)
          if self._standard_deviation.readiness == Readiness.OPERATIONAL:
              self._rolling_median.update(self._standard_deviation.current)

    def is_satisfied(self) -> bool:
        """
        Return True if the specification is met (market activity > baseline).

        WARNING: this method should only be called if this component's `.readiness` property `Readiness.OPERATIONAL`, otherwise it will throw an error.
        """
        if self.readiness != Readiness.OPERATIONAL:
            raise RuntimeError(f"HighVolatilitySpecification expected is_satisfied() to only be called when its readiness is OPERATIONAL, but it is {self.readiness}")

        # NOTE: if readiness is OPERATIONAL, "self._standard_deviation.current" and "self._rolling_median.current" are guaranteed to be floats (instead of None).
        
        return self._standard_deviation.current > self._rolling_median.current
