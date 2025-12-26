from enum import Enum, auto

class Position(Enum):
    """
    Indicate the current custody state of the target asset for the trading bot.
    """
    ZEROED = auto()   # No allocation.
    HOLDING = auto()  # Some allocation.

    def __str__(self):
        """
        Return the enum variant name formatted as title-cased words.
        """
        return self.name.replace('_', ' ').title()
