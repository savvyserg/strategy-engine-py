"""
Domain State Taxonomy
=====================

This module defines the **Vocabulary** used throughout the trading bot's domain.

Architectural Role:
-------------------
These definitions act as the "Nouns" of the system.
They represent the rigid classification systems (Enums) that the logic layers use to communicate status and intent.
They are the leaf nodes of the dependency graph (zero dependencies).

Components:
-----------
* **Readiness:**
   Defines the lifecycle state of a timeseries component that is bufferized one point at a time (e.g., is the buffer full?).
   - WARMING_UP: Accumulating data.
   - OPERATIONAL: Ready for inference.

* **Position:**
   Defines the bot's current exposure to a given asset.
   - ZEROED: No active position.
   - HOLDING: Currently owning the asset.

* **Action:**
   Defines the output intent of the strategy layer.
   - NEUTRAL: Do nothing / Wait.
   - BUY: Enter a position.
   - SELL: Exit a position.
"""

from .action import Action
from .position import Position
from .readiness import Readiness

__all__ = [
    # Explicitely define module API.
    # Silence linter about unused imports.
    # Limit wildcard imports to the intended components.
    "Readiness",
    "Position",
    "Action",
]
