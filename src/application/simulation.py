from typing import Optional

from src.domain.state import Readiness
from src.domain.state import Position
from src.domain.state import Action

from src.application.ports.driven.candle_source import CandleSourcePort
from src.application.ports.driven.journal import JournalPort

from src.domain import StrategyInterface

class SimulatedTradingEngine:
    """
    Simulate trading using a given strategy.

    It binds the 'Outside World' (Candle Sources) to the 'Brain' (Strategy), simulates trades internally, and records the 'Outcome' (Journal).

    - This is an Application Service, any service that occupies this position acts as an orchestrator between the Infrastructure and Domain layers.
    - It is 'Simulated' because no trading takes place:
      - Other implementations might connect to a brokerage account and handle order management.
      - This one simulates trades with zero fees and no slippage using a hardcoded cash-only start of $100k.
    - The strategy can be any strategy as long as it satisfies the interface.
    - The Candle Source can be anything from a live feed from a broker to a csv file, as long as it satisfies the interface.
    - The Journal can ouput to any medium as long as it satisfies the interface.
    """
    def __init__(
        self,
        strategy: StrategyInterface,
        source: CandleSourcePort,
        journal: JournalPort
    ):
        self._strategy = strategy
        self._source = source
        self._journal = journal
        
        # Internal Simulation State.
        self._cash: float = 100000.0  # Hardcoded start at $100k.
        self._held_quantity: int = 0
        self._position: Position = Position.ZEROED
        self._entry_price: Optional[float] = None
        self._last_timestamp: Optional[int] = None

    def run(self) -> None:
        """
        Execute the main event loop.
        Consumes the stream, ticks the strategy, simulates execution, and journals.
        """
        for candle in self._source:
            # Validate time is not moving backwards.
            if self._last_timestamp is not None:
                if candle.timestamp <= self._last_timestamp:
                    raise ValueError(f"{type(self).__name__} Error: new Candle timestamp '{candle.timestamp}' is not strictly after previous Candle timestamp '{self._last_timestamp}'.")

            self._last_timestamp = candle.timestamp
            self._strategy.update(candle)

            current_action_if_ready: Optional[Action] = None
            if self._strategy.readiness == Readiness.OPERATIONAL:
                current_action_if_ready = self._strategy.evaluate(
                    candle.close,
                    self._position,
                    entry_price=self._entry_price,
                )

                # Simulate trading.
                close_price = candle.close
                if current_action_if_ready == Action.BUY:
                    self._handle_buy(close_price)
                elif current_action_if_ready == Action.SELL:
                    self._handle_sell(close_price)

            # Simulate equity state.
            # Equity = Cash + (Held Units * Current Price).
            current_equity = self._cash + (self._held_quantity * candle.close)

            # Journal.
            self._journal.write(
                candle=candle,
                action=current_action_if_ready,
                equity=current_equity
            )

    def _handle_buy(self, price: float) -> None:
        """
        Execute a simulated BUY (All-in).
        """
        if self._position != Position.ZEROED:
             raise RuntimeError(f"{type(self).__name__} Error: Attempted to BUY while position is {self._position.name}.")

        # Integer Math: Calculate max whole units we can afford.
        quantity_to_buy = int(self._cash // price)

        if quantity_to_buy > 0:
            cost = quantity_to_buy * price
            self._cash -= cost
            self._held_quantity = quantity_to_buy
            self._position = Position.HOLDING
            self._entry_price = price
        else:
            # Corner case: Not enough cash to buy even 1 unit.
            # We treat this as a "failed fill" effectively doing nothing but staying Neutral.
            pass

    def _handle_sell(self, price: float) -> None:
        """
        Execute a simulated SELL (Liquidate all).
        """
        if self._position != Position.HOLDING:
             raise RuntimeError(f"{type(self).__name__} Error: Attempted to SELL while position is {self._position.name}.")

        revenue = self._held_quantity * price
        self._cash += revenue
        self._held_quantity = 0
        self._position = Position.ZEROED
        self._entry_price = None
