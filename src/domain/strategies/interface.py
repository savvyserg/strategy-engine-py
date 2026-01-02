from typing import Protocol, Optional, runtime_checkable
from src.domain.candle import Candle
from src.domain.state import Position, Action, Readiness

@runtime_checkable
class Strategy(Protocol):
    """
    Interface for any trading strategy (e.g. MeanReversion, Random, ML).
    """
    def update(self, candle: Candle) -> None: ...
    def evaluate(self, current_price: float, current_position: Position, entry_price: Optional[float] = None) -> Action: ...
    @property
    def readiness(self) -> Readiness: ...
