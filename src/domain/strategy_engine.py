from typing import Optional

from src.domain.state import Action
from src.domain.state import Position
from src.domain.state import Readiness

from src.domain.primitives import LogReturn
from src.domain.primitives import StandardDeviation
from src.domain.primitives import ZScore
from src.domain.primitives import RollingConditionCounter

from src.domain.specifications import DiscountSpecification
from src.domain.specifications import EuphoriaSpecification
from src.domain.specifications import HighVolatilitySpecification
from src.domain.specifications import PositiveTrendSpecification

from src.domain.candle import Candle

from src.domain.config_port import DomainConfigPort

class StrategyEngine:
    """
    Determine the next action to be performed on a given asset.

    This component is stateful, and has a two-point API for feeding internals and querying strategy:
    - It gets fed through the `update()` method everytime a candle (of a fixed timeframe determined by the client) is closed.
    - It owns internal state that keeps track of market and asset conditions, and is mutated ONLY through the `update()` method.
    - It gets queried through the `evaluate()` method, which also receives the current price, so that intra-candle prices might be tested between updates.

    WARNING: Internal state must be adequately accumulated in order for this component to decide on strategy.
    - For this reason the client MUST only call `evaluate()` once the `readiness` property is `Readiness.OPERATIONAL`.
    - It WILL throw an error if `evaluate()` is called before its ready.
    """
    def __init__(self, config: DomainConfigPort):
        if not isinstance(config, DomainConfigPort):
            raise TypeError(f"StrategyEngine expected config to implement DomainConfigPort, got a {type(config).__name__} instance that does not implement it.")
        self._config = config

        # Metrics
        # - These are primitives being used directly by the strategy engine to enforce business logic.
        # - As oposed to primitives used internally in specifications or other dependencies, which are not managed by the strategy engine directly.
        self._log_return: LogReturn = LogReturn()
        self._standard_deviation: StandardDeviation = StandardDeviation(self._config.window_size)
        self._z_score: ZScore = ZScore(self._config.window_size)
        self._low_z_count_in_last_n_candles: RollingConditionCounter = RollingConditionCounter(self._config.stop_low_z_score_n, lambda x: x < self._config.stop_low_z_score_value, float)

        # Specifications
        # - These are business logic containers that output a boolean indicating relevant information (market conditions, asset discount, etc).
        # - They also use primitives internally.
        self._discount_spec: DiscountSpecification = DiscountSpecification(self._config.window_size, self._config.discount_z_score_threshold)
        self._euphoria_spec: EuphoriaSpecification = EuphoriaSpecification(self._config.window_size, self._config.euphoria_z_score_threshold)
        self._high_volatility_spec: HighVolatilitySpecification = HighVolatilitySpecification(self._config.window_size)
        self._positive_trend_spec: PositiveTrendSpecification = PositiveTrendSpecification(self._config.window_size, self._config.positive_trend_ma_threshold)

    def update(self, candle: Candle):
        """
        Update internal metrics with new candle close.

        This method mutates internal state.
        This method MUST be called for every candle close of a fixed timeframe determined by the client.
        """
        if not isinstance(candle, Candle):
            raise TypeError(f"StrategyEngine expected candle to be of type Candle, got {type(candle).__name__}.")
        
        price = candle.close
        self._update_metrics(price)
        self._update_specs(price)

    def _update_metrics(self, price: float):
        self._log_return.update(price)
        if self._log_return.readiness == Readiness.OPERATIONAL:
            self._standard_deviation.update(self._log_return.current)
            self._z_score.update(self._log_return.current)
            if self._z_score.readiness == Readiness.OPERATIONAL:
                self._low_z_count_in_last_n_candles.update(self._z_score.current)

    def _update_specs(self, price: float):
        self._discount_spec.update(price)
        self._euphoria_spec.update(price)
        self._high_volatility_spec.update(price)
        self._positive_trend_spec.update(price)
    
    @property
    def readiness(self):
        """
        Bubble up the readiness of the internal machinery.
        The client should check this before calling 'evaluate()'.
        """
        if (
            # metrics
            self._log_return.readiness == Readiness.OPERATIONAL and
            self._standard_deviation.readiness == Readiness.OPERATIONAL and
            self._z_score.readiness == Readiness.OPERATIONAL and
            self._low_z_count_in_last_n_candles.readiness == Readiness.OPERATIONAL and
            # specifications
            self._discount_spec.readiness == Readiness.OPERATIONAL and
            self._euphoria_spec.readiness == Readiness.OPERATIONAL and
            self._high_volatility_spec.readiness == Readiness.OPERATIONAL and
            self._positive_trend_spec.readiness == Readiness.OPERATIONAL
        ):
            return Readiness.OPERATIONAL
        return Readiness.WARMING_UP

    def evaluate(self, current_price: float, current_position: Position, entry_price: Optional[float] = None) -> Action:
        """
        Calculate the suggested action given the current internal state (as determined by the call to `update()` at the end of each candle).

        This method does not mutate internal state:
        - Client passes current_price (but internal state only gets updated with the price passed in the candle at `update()`).
        - This allows for intra-candle prices to be tested against the current market conditions in the algorithm.
        - This component also does not own the position nor the entry_price (if applicable), they are only used to output the calculation.
        
        This API allows for the domain to only decide the action and not care about order management:
        - Client always passes if the asset being held and at which price, since it is responsible for actually performing the operation.
        - This reduces state desynchronization.
        - If StrategyEngine kept track of position and entry price it would need to leak the abstraction and synchronize state too often.

        WARNING: this method should only be called if this component's `.readiness` property `Readiness.OPERATIONAL`, otherwise it will throw an error.
        """
        if self.readiness != Readiness.OPERATIONAL:
            raise RuntimeError(f"StrategyEngine expected evaluate() to only be called when its readiness is OPERATIONAL, but it is {self.readiness}.")

        if not isinstance(current_price, (int, float)) or isinstance(current_price, bool):
            raise TypeError(f"StrategyEngine expected current_price to be a number, got {type(current_price).__name__}.")
        if current_price <= 0:
            raise ValueError(f"StrategyEngine expected current_price to be positive and non-zero, got {current_price}")
        if not isinstance(current_position, Position):
            raise TypeError(f"StrategyEngine expected current_position to be of type Position, got {type(current_position).__name__}.")

        if current_position == Position.HOLDING:
            # if asset is held, decide if it should be sold
            if entry_price is None:
                # entry price has to exist if the asset is held, otherwise the calculation can't be completed
                raise TypeError(f"StrategyEngine expected evaluate() to only be called with current_position as HOLDING if entry_price exists, but it is None.")
            if not isinstance(entry_price, (int, float)) or isinstance(entry_price, bool):
                raise TypeError(f"StrategyEngine expected entry_price to be a number, got {type(entry_price).__name__}.")

            # check take profit conditions
            take_profit_price = entry_price * (1 + (self._config.take_profit_price_constant_k * self._standard_deviation.current))
            take_profit_price_is_satisfied = current_price >= take_profit_price

            if take_profit_price_is_satisfied:
                # take profit
                # i.e. close the position with profit
                return Action.SELL

            # check stop conditions
            stop_price = entry_price * (1 - (self._config.stop_price_constant_k * self._standard_deviation.current))
            stop_price_is_satisfied = current_price < stop_price
            stop_z_score_is_satisfied = self._z_score.current < self._config.stop_z_score
            stop_low_z_score_count_is_satisfied = self._low_z_count_in_last_n_candles.current >= self._config.stop_low_z_score_count

            if stop_price_is_satisfied and stop_z_score_is_satisfied and stop_low_z_score_count_is_satisfied:
                # stop
                # i.e. close the position at a loss
                return Action.SELL

            # if we should neither take profit, nor stop at a loss, don't close the position (wait)
            return Action.NEUTRAL

        # asset is not held, decide if it should be bought
        if (
            self._positive_trend_spec.is_satisfied() and # if trend is positive
            self._high_volatility_spec.is_satisfied() and # and market is active
            self._discount_spec.is_satisfied() and # and the asset is at a discount
            not self._euphoria_spec.is_satisfied() # and market is NOT euphoric
        ):
            # open position
            # i.e. purchase the asset
            return Action.BUY

        # conditions for purchase are not met, don't open the position (wait)
        return Action.NEUTRAL
