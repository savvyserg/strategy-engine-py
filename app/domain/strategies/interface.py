from typing import Protocol, Optional, runtime_checkable
from app.domain.candle import Candle
from app.domain.state import Position, Action, Readiness

@runtime_checkable
class StrategyInterface(Protocol):
    """
    Interface for any trading strategy (e.g. MeanReversion, Random, ML).

    Mutation & Evaluation
    ---------------------
    This interface enforces a strict Command-Query Separation (CQS) to prevent side effects during evaluation:

    1. **Mutation (`update`)**:
      - Accepts a `Candle`.
      - Updates internal state (metrics, indicators, specifications).
      - MUST be called exactly once per time interval.
      - Returns `None`.

    2. **Query (`evaluate`)**:
      - Accepts current market price and position data.
      - Uses the *already accumulated* state to decide the next action.
      - Is idempotent (does not change state).
      - Returns `Action`.

    Readiness
    ---------
    Strategies often rely on rolling windows (e.g., Moving Averages, Z-Scores).
    Therefore, a strategy is not immediately usable upon instantiation.
    Clients MUST check the `.readiness` property:
    - `Readiness.WARMING_UP`: The strategy is accumulating data. `evaluate()` will raise an error.
    - `Readiness.OPERATIONAL`: The strategy has sufficient data to make decisions.
    """
    def update(self, candle: Candle) -> None: ...
    def evaluate(self, current_price: float, current_position: Position, entry_price: Optional[float] = None) -> Action: ...
    @property
    def readiness(self) -> Readiness: ...
