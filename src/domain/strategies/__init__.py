"""
Domain Strategies Module
========================

Stateful components that determine the next trading Action.
They use both specifications and primitives directly and are one abstraction layer above the specifications.

Architectural Role:
-------------------
These classes act as the **Decision Engines** of the domain.

Key Characteristics:
1. **Command-Query Separation (CQS):** They strictly separate state mutation (`update()`) from decision making (`evaluate()`).
2. **Stateful:** They accumulate history through internal primitives and specifications to build context.
3. **Dependent on Internals:** Since they compose the primitives and specifications, they depend on their `readiness` to be callable.

WARNING: They require the client to be aware of their `readiness`, and will throw errors if `evaluate()` is called before they're ready.

Exported Strategies:
--------------------
* **Strategy:** The interface (Protocol) that all strategies must implement.
* **MeanReversionStrategy:** A technical analysis strategy based on Z-Scores, identifying overextended markets and trading the mean reversion.
* **RandomStrategy:** A benchmarking tool that outputs random legal actions to validate system stability or the Efficient Market Hypothesis.
"""

from .interface import Strategy
from .random import RandomStrategy
from .mean_reversion import MeanReversionStrategy

__all__ = [
    # Explicitely define module API.
    # Silence linter about unused imports.
    # Limit wildcard imports to the intended components.
    "Strategy",
    "RandomStrategy",
    "MeanReversionStrategy",
]
