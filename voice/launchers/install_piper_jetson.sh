#!/bin/bash
# Piper TTS Installation Script for NVIDIA Jetson
# This script installs Piper TTS and required dependencies

set -e  # Exit on error

echo "========================================"
echo "Piper TTS Installation for Jetson"
echo "========================================"
echo ""

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    echo "Warning: This doesn't appear to be a Jetson device."
    read -p "Continue anyway? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        exit 1
    fi
fi

echo "Step 1: Updating package list..."
sudo apt-get update

echo ""
echo "Step 2: Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    espeak-ng \
    libsndfile1 \
    libsndfile1-dev \
    portaudio19-dev \
    python3-dev \
    build-essential \
    wget \
    curl

echo ""
echo "Step 3: Upgrading pip..."
python3 -m pip install --upgrade pip

echo ""
echo "Step 4: Installing ONNX Runtime for GPU (Jetson optimized)..."
# Try GPU version first, fall back to CPU if needed
python3 -m pip install onnxruntime-gpu || {
    echo "GPU runtime not available, installing CPU version..."
    python3 -m pip install onnxruntime
}

echo ""
echo "Step 5: Installing Piper TTS..."
echo "Building piper-phonemize from source (required for ARM64)..."

# Install build dependencies
sudo apt-get install -y git cmake libespeak-ng-dev espeak-ng-data

# Build and install piper-phonemize from source
cd ~
if [ -d "piper-phonemize" ]; then
    echo "Updating existing piper-phonemize repository..."
    cd piper-phonemize
    git pull
else
    echo "Cloning piper-phonemize repository..."
    git clone https://github.com/rhasspy/piper-phonemize.git
    cd piper-phonemize
fi

echo "Building piper-phonemize..."
python3 -m pip install --no-cache-dir . || {
    echo "Building with setuptools..."
    python3 setup.py build_ext --inplace
    python3 -m pip install --no-cache-dir .
}

echo ""
echo "Step 6: Installing Piper TTS Python package..."
python3 -m pip install --no-cache-dir --upgrade piper-tts

# Add ~/.local/bin to PATH if not already there
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo "" >> ~/.bashrc
    echo "# Add local bin to PATH" >> ~/.bashrc
    echo "export PATH=\"\$PATH:\$HOME/.local/bin\"" >> ~/.bashrc
    export PATH="$PATH:$HOME/.local/bin"
fi

echo ""
echo "Verifying installation..."
if command -v piper &> /dev/null || [ -f ~/.local/bin/piper ]; then
    echo "✓ Piper TTS installed successfully!"
    ~/.local/bin/piper --version 2>/dev/null || echo "Piper command available"
else
    echo "⚠ Installation may not be complete. Try running: source ~/.bashrc"
fi

echo ""
echo "Step 6: Creating models directory..."
mkdir -p ~/piper_models
cd ~/piper_models

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Download a voice model from: https://huggingface.co/rhasspy/piper-voices"
echo "2. Place the .onnx and .onnx.json files in ~/piper_models/"
echo ""
echo "Example voice download (English - en_US-amy-medium):"
echo "  cd ~/piper_models"
echo "  wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"
echo "  wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
echo ""
echo "Test Piper TTS:"
echo "  echo 'Hello from Piper TTS' | piper --model ~/piper_models/en_US-amy-medium.onnx --output_file test.wav"
echo "  aplay test.wav  # or use your audio player"
echo ""

