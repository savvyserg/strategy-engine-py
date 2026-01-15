from datetime import datetime

class Candle:
    """
    Represent a candle containing price data for a specific time interval.
    """
    __slots__ = (
        "_open", # The price at the start of the interval.
        "_high", # The highest price reached during the interval.
        "_low", # The lowest price reached during the interval.
        "_close", # The price at the end of the interval.
        "_timestamp", # The date and time of the candle.
    )

    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise AttributeError("Candle is immutable.")
        object.__setattr__(self, name, value)

    def __init__(self, open: float, high: float, low: float, close: float, timestamp: datetime):
        # type check
        if not isinstance(timestamp, datetime):
            raise TypeError(f"Candle expected timestamp to be datetime, got {type(timestamp).__name__}.")
        if not isinstance(open, (int, float)) or isinstance(open, bool):
            raise TypeError(f"Candle expected open to be a number, got {type(open).__name__}.")
        if not isinstance(high, (int, float)) or isinstance(high, bool):
            raise TypeError(f"Candle expected high to be a number, got {type(high).__name__}.")
        if not isinstance(low, (int, float)) or isinstance(low, bool):
            raise TypeError(f"Candle expected low to be a number, got {type(low).__name__}.")
        if not isinstance(close, (int, float)) or isinstance(close, bool):
            raise TypeError(f"Candle expected close to be a number, got {type(close).__name__}.")

        # sanity check
        if open <= 0 or high <= 0 or low <= 0 or close <= 0:
            raise ValueError(f"Candle expected prices to be positive, got Candle(O:{open}, H:{high}, L:{low}, C:{close}).")
        if not (high >= open and high >= close and high >= low):
            raise ValueError(f"Candle expected high to be the maximum value, got Candle(O:{open}, H:{high}, L:{low}, C:{close}).")
        if not (low <= open and low <= close and low <= high):
            raise ValueError(f"Candle expected low to be the minimum value, got Candle(O:{open}, H:{high}, L:{low}, C:{close}).")

        self._open = open
        self._high = high
        self._low = low
        self._close = close
        self._timestamp = timestamp

    def __str__(self):
        """
        Return a string representation for debugging.
        """
        return f"Candle(O:{self._open}, H:{self._high}, L:{self._low}, C:{self._close}, T:{self._timestamp})"

    def __repr__(self):
        return self.__str__()

    @property
    def open(self) -> float:
        return self._open

    @property
    def high(self) -> float:
        return self._high

    @property
    def low(self) -> float:
        return self._low

    @property
    def close(self) -> float:
        return self._close

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def range(self) -> float:
        """
        Return the total price spread (High - Low).
        """
        return self._high - self._low

    @property
    def body(self) -> float:
        """
        Return the absolute distance between the Open and Close.
        """
        return abs(self._close - self._open)
