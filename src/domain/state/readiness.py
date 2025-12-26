from enum import Enum, auto

class Readiness(Enum):
    """
    Indicate if the trading bot has accumulated enough candles to make decisions.
    """
    WARMING_UP = auto()   # Collecting the required 'x' candles.
    OPERATIONAL = auto()  # Data structures full; indicators calculated; ready to trade.

    def __str__(self):
        """
        Return the enum variant name formatted as title-cased words.
        """
        return self.name.replace('_', ' ').title()
