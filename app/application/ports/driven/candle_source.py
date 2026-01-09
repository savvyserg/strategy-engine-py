from typing import Protocol, Iterator, runtime_checkable
from app.domain.candle import Candle

@runtime_checkable
class CandleSourcePort(Protocol):
    """
    Driven Port: Provides a stream of candles.

    The application uses this port to pull market data regardless of the source (e.g., a live WebSocket stream, http queries, a CSV file, etc).
    - Live Market Data: Iterates over a WebSocket queue or polls a REST API (blocking), ideally never raises `StopIteration`.
    - In Backtest: Iterates over a CSV file, raises `StopIteration` when the file is exhausted.

    Iterator Pattern
    ----------------
    It implements the standard Python Iterator protocol:
    - `__iter__`: Returns self.
    - `__next__`: Returns the next `Candle` or raises `StopIteration`.
    """
    def __iter__(self) -> Iterator[Candle]:
        """
        Return the iterator object (usually self).
        """
        ...

    def __next__(self) -> Candle:
        """
        Return the next available candle or raise StopIteration.
        """
        ...
