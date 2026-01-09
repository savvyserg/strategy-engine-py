from app.domain.state import Readiness

from app.domain.primitives import LogReturn
from app.domain.primitives import ZScore

class DiscountSpecification:
    """
    Determine if the market is in a state of deep discount (oversold).

    This is a stateful component that owns the 'LogReturn' and 'ZScore' primitives.
    It ingests a stream of prices and and internally maintains the Z-Score (calculated from LogReturns) within a given window.
    """
    def __init__(self, window_size: int, z_score_discount_threshold: float):
        if not isinstance(window_size, int) or isinstance(window_size, bool):
            raise TypeError(f"DiscountSpecification expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"DiscountSpecification expected window_size to be positive and non-zero, got {window_size}.")
        if not isinstance(z_score_discount_threshold, (int, float)) or isinstance(z_score_discount_threshold, bool):
            raise TypeError(f"DiscountSpecification expected z_score_discount_threshold to be a number, got {type(z_score_discount_threshold).__name__}.")
        
        if z_score_discount_threshold >= 0:
            # A discount by definition implies trading below the mean (0), therefore the threshold must be negative.
            raise ValueError(f"DiscountSpecification expected z_score_discount_threshold to be negative (e.g., -1.0), got {z_score_discount_threshold}.")

        self._log_return: LogReturn = LogReturn()
        self._z_score_discount_threshold: float = z_score_discount_threshold
        self._window_size: int = window_size
        self._z_score: ZScore = ZScore(window_size=window_size)

    @property
    def readiness(self) -> Readiness:
        """
        Bubble up the readiness of the internal machinery.
        The client should check this before calling 'is_satisfied()'.
        """
        if (
            self._log_return.readiness == Readiness.OPERATIONAL and
            self._z_score.readiness == Readiness.OPERATIONAL
        ):
            return Readiness.OPERATIONAL
        return Readiness.WARMING_UP

    @property
    def window_size(self) -> int:
        return self._window_size

    @property
    def threshold(self) -> float:
        """
        Limit that determines the lowest value that does NOT satisfy the specification.

        i.e. value < threshold satisfies the specification.
        """
        return self._z_score_discount_threshold

    def update(self, value: float):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it advances the internal windows/buffers.
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"DiscountSpecification expected value to be a number, got {type(value).__name__}.")

        self._log_return.update(value)
        if self._log_return.readiness == Readiness.OPERATIONAL:
            self._z_score.update(self._log_return.current)

    def is_satisfied(self) -> bool:
        """
        Return True if the specification is met (market is discounted).

        WARNING: this method should only be called if this component's `.readiness` property `Readiness.OPERATIONAL`, otherwise it will throw an error.
        """
        if self.readiness != Readiness.OPERATIONAL:
            raise RuntimeError(f"DiscountSpecification expected is_satisfied() to only be called when its readiness is OPERATIONAL, but it is {self.readiness}.")

        # NOTE: if readiness is OPERATIONAL, "self._z_score.current" is guaranteed to be a float (instead of None).

        return self._z_score.current < self._z_score_discount_threshold
