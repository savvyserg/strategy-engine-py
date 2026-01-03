# Simulated Trading Engine

A Python-based trading simulation engine that tests strategies against historical candle data.

**Note on Architecture:** This project is built using **Hexagonal Architecture (Ports & Adapters)**. While currently configured for backtesting using CSV files, the domain logic is completely decoupled from infrastructure. This means it can be readily extended for **live brokerage operations** by simply swapping the current CSV adapters for API-based implementations (e.g., interactive brokers, crypto exchanges) without modifying the core strategy logic.

## How to Run

Execute the script from the **root directory** of the project:

```bash
python -m src.main
```

## Backtesting

### Configuration

The application requires a **`config.toml`** file in the root directory.
* This file defines strategy parameters (e.g., window sizes, thresholds).
* **Reference:** Please check **`config.example.toml`** for all available variables, descriptions, and value examples.
* **Requirement:** The application will fail to start if this file is missing or invalid.

### Input File Specification (`input.csv`)

To perform a backtest, a file named **`input.csv`** must exist in the root directory.

#### File Requirements
* **Format:** CSV (Comma-Separated Values)
* **Encoding:** UTF-8
* **Headers:** Mandatory (Row 1 must contain the exact column names listed below).

#### Column Definitions

| Column Name | Data Type | Constraints & Format |
| :--- | :--- | :--- |
| **`timestamp`** | `String` | **ISO 8601 Format.**<br>Must include date and time.<br>Example: `2023-10-27T14:30:00-04:00` |
| **`open`** | `Number` | Float or Integer. Must be positive (`> 0`). |
| **`high`** | `Number` | Float or Integer. Must be positive (`> 0`). |
| **`low`** | `Number` | Float or Integer. Must be positive (`> 0`). |
| **`close`** | `Number` | Float or Integer. Must be positive (`> 0`). |

