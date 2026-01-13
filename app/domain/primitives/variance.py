import math
from collections import deque
from typing import Optional

from app.domain.state.readiness import Readiness
from app.domain.primitives.moving_average import MovingAverage

class Variance:
    def __init__(self, window_size: int):
        if not isinstance(window_size, int) or isinstance(window_size, bool):
            raise TypeError(f"Variance expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"Variance expected window_size to be positive and non-zero, got {window_size}.")    
        if window_size < 2:
            # This is the sample Variance, not the population Variance, which means it has Bessel's Correction.
            # Bessel's Correction is 1/(n-1), so we need at least 2 data points to divide by (n-1).
            raise ValueError(f"Variance expected window_size >= 2, got {window_size}.")

        self._window_size: int = window_size
        self._values: deque = deque(maxlen=window_size)
        self._moving_average = MovingAverage(window_size)
        self._current: Optional[float] = None  # Latest stored calculated variance (only available if readiness is OPERATIONAL).

    @property
    def readiness(self) -> Readiness:
        """
        Calculate readiness state on the fly.
        If the buffer is full, we are operational. If not, we are warming up.
        Single source of truth, no risk of state duplication or redundancy.
        """
        if (len(self._values) == self._window_size) and (self._moving_average.readiness == Readiness.OPERATIONAL):
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

    def project_random_walk(self, steps: int) -> Optional[float]:
        """
        Project the current Variance forward by N iterations using the linear scaling rule of Random Walks.

        THEORETICAL BASIS:
        This projection assumes the data follows a Random Walk (Wiener Process/Brownian Motion)
        where returns are Independent and Identically Distributed (I.I.D.).
        
        WHY MULTIPLY BY STEPS?
        1. In a Random Walk, Variance is additive.
        2. "Identically Distributed" means we assume the Variance of every future step is 
           identical to the current Variance.
        3. Therefore, the total Variance for N steps is the sum of N identical current variances:
           Total_Variance = N * Current_Variance

        :param steps: The number of discrete iterations to project forward. 
        """
        if not isinstance(steps, int) or isinstance(steps, bool):
            raise TypeError(f"Variance expected steps to be an integer, got {type(steps).__name__}.")
        if steps <= 0:
            raise ValueError(f"Variance expected steps to be positive and non-zero, got {steps}.")

        if self.readiness != Readiness.OPERATIONAL:
            return None
        return self.current * steps

    def update(self, value: float):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it:
          - Advances the internal window/buffer.
          - Calculates and stores the `.current` property (if the `.readiness` property is `Readiness.OPERATIONAL`).
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"Variance expected value to be a number, got {type(value).__name__}.")

        self._values.append(value) # Add new value. If full, deque automatically pops the oldest value.

        # MA
        self._moving_average.update(value)
        mean = self._moving_average.current

        if self.readiness != Readiness.OPERATIONAL:
            return

        # NOTE: if readiness is OPERATIONAL, "mean" is guaranteed to be a float (instead of None).

        # Sum of Squared Differences: sum((r - MA)^2)
        sum_of_squared_diffs = sum((x - mean) ** 2 for x in self._values)

        # Variance: (1 / (n - 1)) * sum_of_squared_diffs
        # Bessel's Correction applied here.
        self._current = sum_of_squared_diffs / (self._window_size - 1)
