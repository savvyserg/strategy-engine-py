import math
from collections import deque
from typing import Optional

from src.domain.primitives.moving_average import MovingAverage

from src.domain.state.readiness import Readiness

class StandardDeviation:
    def __init__(self, window_size: int):
        if not isinstance(window_size, int):
            raise TypeError(f"StandardDeviation expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"StandardDeviation expected window_size to be positive and non-zero, got {window_size}.")    
        if window_size < 2:
            # this is the sample standard deviation, not the population standard deviation, which means it has Bessel's Correction.
            # Bessel's Correction is 1/(n-1), so we need at least 2 data points to divide by (n-1).
            raise ValueError(f"StandardDeviation expected window_size >= 2, got {window_size}.")

        self._window_size: int = window_size
        self._values: deque = deque(maxlen=window_size)
        self._moving_average = MovingAverage(window_size)
        self._current: Optional[float] = None  # Latest stored calculated deviation (only available if readiness is OPERATIONAL).

    @property
    def readiness(self) -> Readiness:
        """
        Calculates readiness state on the fly.
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
        Projects the current standard deviation (volatility) forward by N iterations using 
        the 'Square Root of Time Rule' (Square Root Law).

        THEORETICAL BASIS:
        This projection assumes the data follows a Random Walk (Wiener Process/Brownian Motion)
        where returns are Independent and Identically Distributed (I.I.D.).
        
        WHY MULTIPLY BY SQRT(STEPS)?
        1. "Identically Distributed" means we assume the Variance of every future step is 
           identical to the current Variance.
        2. In a Random Walk, Variance is additive. The total Variance for N steps is the sum 
           of N identical current variances:
           Total_Variance = N * Current_Variance
        3. Standard Deviation is the square root of Variance. To get the Total Standard Deviation,
           we take the square root of the Total Variance:
           Total_Sigma = sqrt(N * Current_Variance)
        4. Reducing the equation:
           Total_Sigma = sqrt(N) * Current_Sigma

        ARGUMENT ABSTRACTION:
        :param steps: The number of discrete iterations to project forward. 
                      In finance, this is often abstracted as "Time" (e.g., converting 15-min 
                      volatility to Daily volatility means projecting 26 steps forward).
        
        COMMON USE CASES:
        - Intraday to Daily (e.g., steps=26 for 15m bars)
        - Daily to Annual (e.g., steps=252 for daily bars)
        """
        if not isinstance(steps, int):
            raise TypeError(f"StandardDeviation expected steps to be an integer, got {type(steps).__name__}.")
        if steps <= 0:
            raise ValueError(f"StandardDeviation expected steps to be positive and non-zero, got {steps}.")

        if self.readiness != Readiness.OPERATIONAL:
            return None
        return self.current * math.sqrt(steps)

    def update(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f"StandardDeviation expected value to be a number, got {type(value).__name__}.")

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
        variance = sum_of_squared_diffs / (self._window_size - 1)

        # Standard Deviation: sqrt(Variance)
        self._current = math.sqrt(variance)
