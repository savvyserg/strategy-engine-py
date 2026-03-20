# Simulated Trading Engine

A Python-based trading simulation engine that tests strategies against historical candle data.

**Note on Architecture:** This project is built using **Hexagonal Architecture (Ports & Adapters)**. While currently configured for backtesting using CSV files, the domain logic is completely decoupled from infrastructure. This means it can be readily extended for **live brokerage operations** by simply swapping the current CSV adapters for API-based implementations (e.g., interactive brokers, crypto exchanges) without modifying the core strategy logic.

## How to Run

Execute the script from the **root directory** of the project:

```bash
python -m app.main
```

## Building for Production (Single-File Binary)

This project can be compiled into a standalone binary using **PyApp**.

### Prerequisites

1. **Rust & Cargo:** [Install Rust](https://www.rust-lang.org/tools/install)
2. **PyApp Source:** Must exist in a sibling directory.
   *We pin version `v0.29.0` to ensure build stability.*
  ```bash
  git clone --branch v0.29.0 https://github.com/ofek/pyapp ../pyapp
  ```
3. **Python Build Dependencies** Install the project and build tools (required for `build-binary.sh`):
  ```bash
  pip install -e ".[dev]"
  ```

### Cross-Compilation Tools (Optional)

To perform **cross-compilation** (targeting different Operating Systems or CPU architectures), you need **Zig** and **Cargo Zigbuild**.
Without these, the build script will fail on non-native targets due to missing system linkers.

1.  **Install Zig Compiler:**
    * **Ubuntu/Debian (Snap):**
        ```bash
        sudo snap install zig --classic --beta
        ```
    * **Manual Download:** Get the release from [ziglang.org/download](https://ziglang.org/download/) and add it to your `PATH`.

2.  **Install Cargo Extension:**
    ```bash
    cargo install cargo-zigbuild
    ```

*If you do not wish to install these tools, please open `build-binary.sh` and comment out the targets you do not need (e.g., Mac/Windows).*

### Build Instructions

Run the automated build script from the project root:

```bash
./build-binary.sh
```

* **Artifacts:** Binaries are placed in the project root (e.g., `quant-trader_linux_x86-64`).
* **Cross-Compilation:** Building for Windows/Mac from Linux requires specific linkers (see `build-binary.sh` notes).

## Backtesting

### Configuration

The application requires a **`config.toml`** file.

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

## User-Provided File Location:
The application detects required files (e.g., `config.toml`, `input.csv`) based on your execution mode.

1. **Running Packaged Executable:**
   The application looks in the **Current Working Directory**.
   * **GUI (Double-Click):** Works automatically (files must be next to the binary).
   * **Terminal:** You must run the command *from the directory containing the files*.

2. **Running Script Directly:**
   The application looks in the **Project Root** (main source folder).
