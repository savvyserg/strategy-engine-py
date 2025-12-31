from src.domain.state import Readiness

from src.domain.primitives import LogReturn
from src.domain.primitives import RollingMax
from src.domain.primitives import ZScore

class EuphoriaSpecification:
    """
    Determine if the market is in a state of extreme euphoria.
    
    This is a stateful component that owns the 'LogReturn', 'ZScore', and 'RollingMax' primitives.
    It ingests a stream of prices and internally maintains the historical Z-Score maximum (calculated from LogReturns) within a given window.
    """
    def __init__(self, window_size: int, z_score_euphoria_threshold: float):
        if not isinstance(window_size, int):
            raise TypeError(f"EuphoriaSpecification expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"EuphoriaSpecification expected window_size to be positive and non-zero, got {window_size}.")
        if not isinstance(z_score_euphoria_threshold, (int, float)):
            raise TypeError(f"EuphoriaSpecification expected z_score_euphoria_threshold to be a number, got {type(z_score_euphoria_threshold).__name__}.")
        if z_score_euphoria_threshold <= 0:
            raise ValueError(f"EuphoriaSpecification expected z_score_euphoria_threshold to be positive and non-zero, got {z_score_euphoria_threshold}.")

        self._log_return: LogReturn = LogReturn()
        self._z_score_euphoria_threshold: float = z_score_euphoria_threshold # If max > z_score_euphoria_threshold the euphoria specification is satisfied.
        self._window_size: int = window_size
        self._z_score: ZScore = ZScore(window_size=window_size)
        self._rolling_max: RollingMax = RollingMax(window_size=window_size)

    @property
    def readiness(self) -> Readiness:
        """
        Bubble up the readiness of the internal machinery.
        The client should check this before calling 'is_satisfied()'.
        """
        if (
            self._log_return.readiness == Readiness.OPERATIONAL and
            self._z_score.readiness == Readiness.OPERATIONAL and
            self._rolling_max.readiness == Readiness.OPERATIONAL
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
        return self._z_score_euphoria_threshold

    def update(self, value: float):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it advances the internal windows/buffers.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"EuphoriaSpecification expected value to be a number, got {type(value).__name__}.")

        self._log_return.update(value)
        if self._log_return.readiness == Readiness.OPERATIONAL:
            self._z_score.update(self._log_return.current)
            if self._z_score.readiness == Readiness.OPERATIONAL:
                self._rolling_max.update(self._z_score.current)

    def is_satisfied(self) -> bool:
        """
        Return True if the specification is met (market is euphoric).

        WARNING: this method should only be called if this component's `.readiness` property `Readiness.OPERATIONAL`, otherwise it will throw an error.
        """
        if self.readiness != Readiness.OPERATIONAL:
            raise RuntimeError(f"EuphoriaSpecification expected is_satisfied() to only be called when its readiness is OPERATIONAL, but it is {self.readiness}")

        # NOTE: if readiness is OPERATIONAL, "self._rolling_max.current" is guaranteed to be a float (instead of None).

        return self._rolling_max.current > self._z_score_euphoria_threshold
