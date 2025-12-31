from collections import deque
from typing import Callable, Generic, TypeVar, Optional, Deque, NamedTuple, Type

from src.domain.state.readiness import Readiness

# T represents the type of data we are analyzing (e.g. float, int)
T = TypeVar("T")

class ConditionEvaluation(NamedTuple, Generic[T]):
    """
    Immutable snapshot of a single data point and its evaluation result.
    This provides the audit trail/traceability.
    """
    value: T
    is_satisfied: bool

class RollingConditionCounter(Generic[T]):
    def __init__(self, window_size: int, condition: Callable[[T], bool], data_type: Type[T]):
        """
        :param window_size: The number of steps to look back.
        :param condition: A function that defines the rule. 
                          It receives a value of type T and returns True if it counts towards the metric.
                          Example: lambda z: z < -2
        :param data_type: The expected type of the input values (e.g., float, int).
                          Required for runtime safety checks.
        """
        if not isinstance(window_size, int):
            raise TypeError(f"RollingConditionCounter expected window_size to be an integer, got {type(window_size).__name__}.")
        if window_size <= 0:
            raise ValueError(f"RollingConditionCounter expected window_size to be positive and non-zero, got {window_size}.")
        if not callable(condition):
             raise TypeError(f"RollingConditionCounter expected 'condition' to be a callable function (lambda).")
        if not isinstance(data_type, (type, tuple)): # Allow tuples for multiple types.
             raise TypeError(f"RollingConditionCounter expected 'data_type' to be a class type, got {type(data_type).__name__}.")

        self._window_size = window_size
        self._condition = condition # The condition is baked into the instance (Immutable Logic).
        self._data_type = data_type # Stored to allow runtime isinstance() checks on dynamic types.

        self._values: Deque[ConditionEvaluation[T]] = deque(maxlen=window_size) # Store values and evaluations for auditability.
        self._current: Optional[int] = None # Latest calculated rolling condition count (only available if readiness is OPERATIONAL).

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
    def current(self) -> Optional[int]:
        if self.readiness != Readiness.OPERATIONAL:
            return None
        return self._current

    @property
    def window_size(self) -> int:
        return self._window_size

    def get_history(self) -> list[ConditionEvaluation[T]]:
        """
        Return a copy of the current window buffer.
        Useful for debugging: "Which specific values triggered this count?"
        """
        return list(self._values)

    def update(self, value: T):
        """
        Ingest a new value from the data stream to update internal state and metrics.

        This operation is stateful, it:
          - Advances the internal window/buffer.
          - Calculates and stores the `.current` property (if the `.readiness` property is `Readiness.OPERATIONAL`).
        """
        if not isinstance(value, self._data_type):
            expected = self._data_type.__name__ if isinstance(self._data_type, type) else str(self._data_type)
            raise TypeError(f"RollingConditionCounter expected value of type {expected}, got {type(value).__name__}.")

        try:
            is_satisfied = self._condition(value)
        except Exception as e:
            raise RuntimeError(f"RollingConditionCounter failed to execute condition lambda on value {value}: {e}") from e

        if not isinstance(is_satisfied, bool):
             raise TypeError(f"RollingConditionCounter expected condition lambda to return a boolean, got {type(is_satisfied).__name__}.")
        
        self._values.append(ConditionEvaluation(value=value, is_satisfied=is_satisfied))

        if self.readiness != Readiness.OPERATIONAL:
            return

        # We sum the 'is_satisfied' booleans (True=1, False=0).
        # This is O(N), which is efficient for typical window sizes (e.g. N=5 or N=20).
        self._current = sum(1 for item in self._values if item.is_satisfied)
