"""
Domain Specifications Module
============================

This module contains the higher level building blocks (one higher than the primitives) that compose the primitives into semantic meaning.
They are business rules used to analyze market conditions.

Architectural Role:
-------------------
These classes act as **Stateful Machines**.
They bridge the gap between raw price data and market information (which can be used to make trading decisions).
Unlike primitives (which calculate values), specifications determine business rules (e.g., "Is the market Euphoric?").

Key Characteristics:
1. **Self-Contained:** They ingest raw prices (`update(value)`) and internally own the necessary primitives (`LogReturn`, `ZScore`, etc.) to calculate their metrics.
2. **Autonomous:** Each specification defines its own `window_size`, allowing for independent time horizons (Bounded Contexts) without global dependencies.
3. **Boolean Output:** They answer specific binary questions via `is_satisfied()` based on internal thresholds.
4. **Dependent on Internals:** Since they compose the primitives, they depend on their `readiness` to be callable.

WARNING: They require the client to be aware of their `readiness`, and will throw errors if `is_satisfied()` is called before they're ready.

Exported Specifications:
------------------------
* **DiscountSpecification:** Determines if the asset is in a state of deep discount (oversold).
* **EuphoriaSpecification:** Determines if the asset is in a state of extreme euphoria.
* **HighVolatilitySpecification:** Determines if the market has high activity (volatility) relative to its baseline.
* **PositiveTrendSpecification:** Determines if the asset is in a positive trend state.
"""

from .discount import DiscountSpecification
from .euphoria import EuphoriaSpecification
from .high_volatility import HighVolatilitySpecification
from .positive_trend import PositiveTrendSpecification

__all__ = [
    # Explicitely define module API.
    # Silence linter about unused imports.
    # Limit wildcard imports to the intended components.
    "DiscountSpecification",
    "EuphoriaSpecification",
    "HighVolatilitySpecification",
    "PositiveTrendSpecification",
]
