from typing import Protocol, runtime_checkable
from typing import Optional
from src.domain.candle import Candle
from src.domain.state import Action

@runtime_checkable
class JournalPort(Protocol):
    """
    Driven Port: Records the trading session history.

    This port allows the application to persist its activity without knowing
    the storage medium (CSV, Database, Terminal, etc.).
    """
    def write(
        self,
        candle: Candle,
        action: Optional[Action],
        equity: float,
    ) -> None:
        """
        Write a single row summarizing the complete state of a trading step.

        This method is called at the end of every processing loop to create a comprehensive audit trail (ledger).

        Args:
            candle: The market data for this step.
            action: The decision made by the strategy.
            equity: The total portfolio value (Cash + Holdings * Price) *after* trades.
        """
        ...
