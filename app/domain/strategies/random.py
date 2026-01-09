from typing import Optional
import random

from app.domain.candle import Candle
from app.domain.state import Position, Action, Readiness

from app.domain.strategies.interface import StrategyInterface

class RandomStrategy(StrategyInterface):
    """
    A strategy implementation that outputs random legal actions.
    Used for benchmarking (Efficient Market Hypothesis) or system testing.
    """
    __slots__ = ()

    def __init__(self):
        # No state needed for random selection.
        pass

    def update(self, candle: Candle) -> None:
        # This class has no state, so no update is needed.
        pass

    def evaluate(self, current_price: float, current_position: Position, entry_price: Optional[float] = None) -> Action:
        if not isinstance(current_position, Position):
            raise TypeError(f"{type(self).__name__} expected current_position to be of type Position, got {type(current_position).__name__}.")

        if current_position == Position.HOLDING:
            # if Holding -> 50% Sell / 50% Neutral
            return random.choice((Action.SELL, Action.NEUTRAL))
        if current_position == Position.ZEROED:
            # if Neutral -> 50% Buy / 50% Neutral
            return random.choice((Action.BUY, Action.NEUTRAL))
    
    @property
    def readiness(self) -> Readiness:
        # Stateless random strategy is always ready.
        return Readiness.OPERATIONAL
