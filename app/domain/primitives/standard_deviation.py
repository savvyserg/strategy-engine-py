import math
from collections import deque
from typing import Optional

from app.domain.state.readiness import Readiness

from app.domain.primitives.variance import Variance

class StandardDeviation:
    def __init__(self, window_size: int):
        if not isinstance(window_size, int) or isinstance(window_size, bool):
            raise TypeError(f"StandardDeviation expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"StandardDeviation expected window_size to be positive and non-zero, got {window_size}.")    

        self._window_size: int = window_size
        self._variance: Variance = Variance(window_size)
        self._current: Optional[float] = None  # Latest stored calculated deviation (only available if readiness is OPERATIONAL).

    @property
    def readiness(self) -> Readiness:
        """
        Calculate readiness state on the fly.
        If the buffer is full, we are operational. If not, we are warming up.
        Single source of truth, no risk of state duplication or redundancy.
        """
        if (self._variance.readiness == Readiness.OPERATIONAL):
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
        Project the current standard deviation (volatility) forward by N iterations using the 'Square Root of Time Rule' (Square Root Law).

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
        if not isinstance(steps, int) or isinstance(steps, bool):
            raise TypeError(f"StandardDeviation expected steps to be an integer, got {type(steps).__name__}.")
        if steps <= 0:
            raise ValueError(f"StandardDeviation expected steps to be positive and non-zero, got {steps}.")

        if self.readiness != Readiness.OPERATIONAL:
            return None
        return self.current * math.sqrt(steps)

    def update(self, value: float):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it:
          - Advances the internal window/buffer.
          - Calculates and stores the `.current` property (if the `.readiness` property is `Readiness.OPERATIONAL`).
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"StandardDeviation expected value to be a number, got {type(value).__name__}.")

        self._variance.update(value)

        if self.readiness != Readiness.OPERATIONAL:
            return

        # NOTE: if readiness is OPERATIONAL, "mean" is guaranteed to be a float (instead of None).

        # Standard Deviation: sqrt(Variance)
        self._current = math.sqrt(self._variance.current)
