"""
Domain Primitives Module
========================

This module contains the fundamental building blocks (computational primitives) used to analyze time-series data.

Architectural Role:
-------------------
These classes act as **Stateful Machines**.
They ingest data one point at a time, maintain internal state (history), and output calculated metrics.
They are the "Machinery" of the domain.

Key Characteristics:
1. **Stateful:** They maintain their own sliding window buffers.
2. **Reactive:** They expose a `readiness` state (WARMING_UP vs OPERATIONAL).
3. **Encapsulated:** They contain all logic required to compute their specific metric.

Exported Primitives:
--------------------
* **LogReturn:** Calculates the logarithmic growth rate between sequential values.
* **RollingMax:** Tracks statistical extremes.
* **RollingMedian:** Tracks statistical centers.
* **MovingAverage:** Tracks the underlying trend of a value.
* **StandardDeviation:** Tracks the volatility (dispersion) of a value.
* **ZScore:** Normalizes a value against its historical mean and volatility.
* **RollingConditionCounter:** Counts frequency of boolean events (logic filters).

"""
