from src.domain.state import Readiness

from src.domain.primitives import LogReturn
from src.domain.primitives import MovingAverage

class PositiveTrendSpecification:
    """
    Determine if the market is in a positive trend state.

    This is a stateful component that owns the 'LogReturn' and 'MovingAverage' primitives.
    It ingests a stream of prices and internally maintains the average Log Return within a given window.
    """
    def __init__(self, window_size: int, ma_positive_trend_threshold: float):
        if not isinstance(window_size, int):
            raise TypeError(f"PositiveTrendSpecification expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"PositiveTrendSpecification expected window_size to be positive and non-zero, got {window_size}.")
        if not isinstance(ma_positive_trend_threshold, (int, float)):
            raise TypeError(f"PositiveTrendSpecification expected ma_positive_trend_threshold to be a number, got {type(ma_positive_trend_threshold).__name__}.")
        if ma_positive_trend_threshold < 0:
            raise ValueError(f"PositiveTrendSpecification expected ma_positive_trend_threshold to be positive, got {ma_positive_trend_threshold}.")

        self._log_return: LogReturn = LogReturn()
        self._ma_positive_trend_threshold: float = ma_positive_trend_threshold # If MA > ma_positive_trend_threshold the positive trend specification is satisfied.
        self._window_size: int = window_size
        self._moving_average: MovingAverage = MovingAverage(window_size=window_size)

    @property
    def readiness(self) -> Readiness:
        """
        Bubble up the readiness of the internal machinery.
        The client should check this before calling 'is_satisfied()'.
        """
        if (
            self._log_return.readiness == Readiness.OPERATIONAL and
            self._moving_average.readiness == Readiness.OPERATIONAL
        ):
            return Readiness.OPERATIONAL
        return Readiness.WARMING_UP

    @property
    def window_size(self) -> int:
        return self._window_size

    @property
    def threshold(self) -> float:
        """
        Limit that determines the highest value that does NOT satisfy the specification.

        i.e. value > threshold satisfies the specification.
        """
        return self._ma_positive_trend_threshold

    def update(self, value: float):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it advances the internal windows/buffers.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"PositiveTrendSpecification expected value to be a number, got {type(value).__name__}.")

        self._log_return.update(value)
        if self._log_return.readiness == Readiness.OPERATIONAL:
            self._moving_average.update(self._log_return.current)

    def is_satisfied(self) -> bool:
        """
        Return True if the specification is met (market has positive trend).

        WARNING: this method should only be called if this component's `.readiness` property `Readiness.OPERATIONAL`, otherwise it will throw an error.
        """
        if self.readiness != Readiness.OPERATIONAL:
            raise RuntimeError(f"PositiveTrendSpecification expected is_satisfied() to only be called when its readiness is OPERATIONAL, but it is {self.readiness}.")

        # NOTE: if readiness is OPERATIONAL, "self._moving_average.current" is guaranteed to be a float (instead of None).

        return self._moving_average.current > self._ma_positive_trend_threshold
