#!/usr/bin/env bash
set -e

# --- CONFIGURATION ---
# 1. Project Definitions
PROJECT_NAME="quant-trader"
PROJECT_VERSION="0.1.0"
PYTHON_PKG_NAME="app"

# 2. Path to the PyApp Source Code (Rust Builder)
PYAPP_SOURCE_DIR="../pyapp-latest"

# 3. Detect Current Directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "   BUILDING: $PROJECT_NAME"
echo "   HOST PLATFORM: $(uname -s)"
echo "=========================================="

# --- STEP 1: CACHE DESTRUCTION ---
echo "[1/4] Cleaning Caches..."

# A. Clean Python Build Artifacts
for p in dist build *.egg-info; do
    if [ -e "$p" ]; then
        rm -rf "$p"
        echo "  -> Build artifact nuked: $p"
    else
        echo "  -> Build artifact not found (clean): $p"
    fi
done

# B. Clean PyApp Runtime Cache (OS Sensitive)
OS_NAME=$(uname -s)
if [ "$OS_NAME" == "Darwin" ]; then
    RUNTIME_CACHE="$HOME/Library/Application Support/pyapp/$PROJECT_NAME"
elif [ "$OS_NAME" == "Linux" ]; then
    RUNTIME_CACHE="$HOME/.local/share/pyapp/$PROJECT_NAME"
else
    RUNTIME_CACHE=""
    echo "  -> WARNING: Unknown OS. Skipping runtime cache clean."
fi

if [ -n "$RUNTIME_CACHE" ]; then
    if [ -d "$RUNTIME_CACHE" ]; then
        rm -rf "$RUNTIME_CACHE"
        echo "  -> Runtime cache nuked: $RUNTIME_CACHE"
    else
        echo "  -> Runtime cache not found (clean): $RUNTIME_CACHE"
    fi
fi


# --- STEP 2: BUILD PYTHON WHEEL ---
echo "[2/4] Building Python Wheel..."

# Ensure we use the specific pyenv version
PYENV_VERSION=quant-trader-3.13.7 pyenv exec python -m build --wheel

WHEEL_REL_PATH=$(ls dist/*.whl | head -n 1)
WHEEL_FILENAME=$(basename "$WHEEL_REL_PATH")
FULL_WHEEL_PATH="$PROJECT_ROOT/dist/$WHEEL_FILENAME"

if [ ! -f "$FULL_WHEEL_PATH" ]; then
    echo "CRITICAL ERROR: Wheel creation failed."
    exit 1
fi
echo "  -> Wheel built: $WHEEL_FILENAME"


# --- STEP 3: COMPILE BINARIES (MULTI-TARGET) ---
echo "[3/4] Compiling Binaries..."

if [ ! -d "$PYAPP_SOURCE_DIR" ]; then
    echo "CRITICAL ERROR: PyApp source not found at $PYAPP_SOURCE_DIR"
    exit 1
fi

pushd "$PYAPP_SOURCE_DIR" > /dev/null

export PYAPP_PROJECT_NAME="$PROJECT_NAME"
export PYAPP_PROJECT_VERSION="$PROJECT_VERSION"
export PYAPP_PROJECT_PATH="$FULL_WHEEL_PATH"
export PYAPP_EXEC_MODULE="$PYTHON_PKG_NAME.main"

# Define Targets: "RUST_TRIPLE:OUTPUT_SUFFIX"
# NOTE: You must have these targets installed via `rustup target add ...`
# TIP: Comment out targets you don't need if builds are failing!
TARGETS=(
    "x86_64-unknown-linux-gnu:linux_x86-64"
    "x86_64-pc-windows-gnu:windows_x86-64"
    "aarch64-apple-darwin:mac_arm64"
    "x86_64-apple-darwin:mac_x86-64"
)

# Check if user has the magic 'zigbuild' tool (fixes cross-compilation)
BUILDER="cargo build"
if cargo --list | grep -q "zigbuild"; then
    echo "   [+] Found cargo-zigbuild. Cross-compilation enabled."
    BUILDER="cargo zigbuild"
else
    echo "   [!] cargo-zigbuild not found. Using standard cargo build."
    echo "       (Non-native targets may fail without system linkers)"
fi

SUCCESS_COUNT=0

for PAIR in "${TARGETS[@]}"; do
    TARGET="${PAIR%%:*}"
    SUFFIX="${PAIR##*:}"
    
    echo "   -- Target: $SUFFIX ($TARGET) --"
    
    # Try to build. If it fails (missing toolchain), warn and continue.
    if $BUILDER --release --target "$TARGET"; then
        
        # Determine extension (Windows needs .exe)
        BIN_EXT=""
        [[ "$TARGET" == *"windows"* ]] && BIN_EXT=".exe"
        
        # Locate the binary (Rust puts it in target/<TRIPLE>/release/)
        # Check standard 'pyapp' name first, then fallback to PROJECT_NAME
        SRC="target/$TARGET/release/pyapp$BIN_EXT"
        if [ ! -f "$SRC" ]; then
            SRC="target/$TARGET/release/$PROJECT_NAME$BIN_EXT"
        fi

        if [ -f "$SRC" ]; then
            # Move and Rename
            DEST="$PROJECT_ROOT/${PROJECT_NAME}_${SUFFIX}${BIN_EXT}"
            cp "$SRC" "$DEST"
            chmod +x "$DEST"
            echo "      -> Success! Created: $DEST"
            SUCCESS_COUNT=$((SUCCESS_COUNT+1))
        else
            echo "      -> ERROR: Build succeeded but binary not found at $SRC"
        fi
    else
        echo "      -> FAILED: Could not build for $TARGET. (Check rustup/cross-compilation setup)"
    fi
done

popd > /dev/null

# --- STEP 4: SUMMARY ---
echo "=========================================="
if [ "$SUCCESS_COUNT" -gt 0 ]; then
    echo "DONE. Created $SUCCESS_COUNT binaries in $PROJECT_ROOT"
else
    echo "FAILED. No binaries were created."
    exit 1
fi
