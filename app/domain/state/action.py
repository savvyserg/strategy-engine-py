from enum import Enum, auto

class Action(Enum):
    """
    Indicate the current suggested action of the trading bot for target asset.
    """
    BUY = auto()   # Should send a purchase order.
    # TODO: consider replacing the "NEUTRAL" variant with a nullable object wrapper for the entire enum.
    # TODO: maybe not, classically "not doing something" is an action in trading bot systems.
    NEUTRAL = auto()  # Should do nothing.
    SELL = auto()  # Should send a sell order.

    def __str__(self):
        """
        Return the enum variant name formatted as title-cased words.
        """
        return self.name.replace('_', ' ').title()
