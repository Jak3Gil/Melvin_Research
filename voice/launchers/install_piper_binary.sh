#!/bin/bash
# Install Piper TTS Binary (standalone) for Jetson

set -e

echo "========================================"
echo "Installing Piper TTS Binary for Jetson"
echo "========================================"
echo ""

PIPER_DIR="$HOME/piper"
mkdir -p "$PIPER_DIR"
cd "$PIPER_DIR"

echo "Downloading Piper binary..."
# Find a release with ARM64 binary
# Try v1.2.0 first (known to have ARM64 binary)
LATEST_VERSION="v1.2.0"
DOWNLOAD_URL="https://github.com/rhasspy/piper/releases/download/${LATEST_VERSION}/piper_arm64.tar.gz"

echo "Using version: $LATEST_VERSION"
echo "Download URL: $DOWNLOAD_URL"

# Download with wget or curl
if command -v wget &> /dev/null; then
    wget --progress=bar:force "$DOWNLOAD_URL" -O piper_arm64.tar.gz
else
    curl -L -o piper_arm64.tar.gz "$DOWNLOAD_URL"
fi

if [ ! -f "piper_arm64.tar.gz" ]; then
    echo "Error: Failed to download Piper binary"
    exit 1
fi

echo "Extracting..."
tar -xzf piper_arm64.tar.gz
rm piper_arm64.tar.gz

# Find the piper binary
if [ -f "piper/piper" ]; then
    PIPER_BIN="piper/piper"
elif [ -f "piper" ]; then
    PIPER_BIN="piper"
else
    echo "Error: Could not find piper binary after extraction"
    exit 1
fi

chmod +x "$PIPER_BIN"

# Add to PATH
if ! grep -q "export PATH.*piper" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Piper TTS" >> ~/.bashrc
    echo "export PATH=\"\$PATH:$PIPER_DIR\"" >> ~/.bashrc
fi

# Create models directory
mkdir -p "$PIPER_DIR/models"

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Piper binary installed at: $PIPER_DIR/$PIPER_BIN"
echo ""
echo "To use Piper, add to PATH:"
echo "  export PATH=\"\$PATH:$PIPER_DIR\""
echo ""
echo "Or reload your shell:"
echo "  source ~/.bashrc"
echo ""
echo "Next steps:"
echo "1. Download a voice model from: https://huggingface.co/rhasspy/piper-voices"
echo "2. Place the .onnx and .onnx.json files in $PIPER_DIR/models/"
echo ""
echo "Example:"
echo "  cd $PIPER_DIR/models"
echo "  wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"
echo "  wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
echo ""
echo "Test:"
echo "  echo 'Hello from Piper TTS' | $PIPER_DIR/$PIPER_BIN --model $PIPER_DIR/models/en_US-amy-medium.onnx --output_file test.wav"

