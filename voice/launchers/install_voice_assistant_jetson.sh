#!/bin/bash
# Install Voice Assistant components on Jetson
# This script installs: Whisper (STT), Ollama (LLM), and configures Piper (TTS)

echo "=========================================="
echo "Melvin Voice Assistant Installation"
echo "=========================================="
echo ""

# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    echo "⚠ Warning: This doesn't appear to be a Jetson device"
    echo "  Continuing anyway..."
fi

echo "This will install:"
echo "  1. Whisper (Speech-to-Text)"
echo "  2. Ollama (Large Language Model)"
echo "  3. PyAudio (Audio recording)"
echo "  4. Required dependencies"
echo ""
echo "Piper TTS should already be installed."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 1: Update system packages"
echo "=========================================="
sudo apt-get update

echo ""
echo "=========================================="
echo "Step 2: Install audio dependencies"
echo "=========================================="
sudo apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    alsa-utils

echo ""
echo "=========================================="
echo "Step 3: Install Python packages"
echo "=========================================="
pip3 install --upgrade pip

# Install PyAudio
echo "Installing PyAudio..."
pip3 install pyaudio

# Install Whisper
echo "Installing OpenAI Whisper..."
pip3 install openai-whisper

# Install additional dependencies
echo "Installing additional dependencies..."
pip3 install numpy scipy

echo ""
echo "=========================================="
echo "Step 4: Install Ollama"
echo "=========================================="

if command -v ollama &> /dev/null; then
    echo "✓ Ollama already installed"
    ollama --version
else
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

echo ""
echo "=========================================="
echo "Step 5: Download LLM model"
echo "=========================================="

echo "Downloading lightweight LLM model (llama3.2:1b)..."
echo "This may take several minutes..."
ollama pull llama3.2:1b

echo ""
echo "=========================================="
echo "Step 6: Test Whisper installation"
echo "=========================================="

python3 << 'EOF'
try:
    import whisper
    print("✓ Whisper installed successfully")
    print(f"  Available models: tiny, base, small, medium, large")
except ImportError as e:
    print(f"✗ Whisper import failed: {e}")
EOF

echo ""
echo "=========================================="
echo "Step 7: Test PyAudio installation"
echo "=========================================="

python3 << 'EOF'
try:
    import pyaudio
    p = pyaudio.PyAudio()
    print("✓ PyAudio installed successfully")
    print(f"  Audio devices: {p.get_device_count()}")
    p.terminate()
except ImportError as e:
    print(f"✗ PyAudio import failed: {e}")
EOF

echo ""
echo "=========================================="
echo "Step 8: Test Ollama"
echo "=========================================="

if ollama list | grep -q "llama3.2:1b"; then
    echo "✓ Ollama model installed successfully"
else
    echo "⚠ Ollama model not found, trying to pull again..."
    ollama pull llama3.2:1b
fi

echo ""
echo "=========================================="
echo "Step 9: Verify Piper TTS"
echo "=========================================="

if [ -f "/home/melvin/piper/piper/piper" ]; then
    echo "✓ Piper TTS binary found"
else
    echo "✗ Piper TTS binary not found at /home/melvin/piper/piper/piper"
    echo "  Please install Piper TTS first"
fi

if [ -f "/home/melvin/piper/models/en_US-lessac-medium.onnx" ]; then
    echo "✓ Piper voice model found"
else
    echo "⚠ Piper voice model not found"
    echo "  Downloading male voice model..."
    mkdir -p ~/piper/models
    cd ~/piper/models
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
fi

echo ""
echo "=========================================="
echo "Step 10: Download Whisper model"
echo "=========================================="

echo "Pre-downloading Whisper 'base' model..."
python3 << 'EOF'
import whisper
print("Downloading Whisper base model...")
model = whisper.load_model("base")
print("✓ Whisper base model downloaded")
EOF

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ Whisper (STT) - Speech to Text"
echo "  ✓ Ollama (LLM) - Language Model"
echo "  ✓ Piper (TTS) - Text to Speech"
echo ""
echo "To test the voice assistant:"
echo "  python3 voice_assistant_jetson.py"
echo ""
echo "To test individual components:"
echo "  - Whisper: python3 test_whisper_jetson.py"
echo "  - Ollama: ollama run llama3.2:1b 'Hello!'"
echo "  - Piper: bash test_hello_jetson.sh"
echo ""
echo "Note: Make sure your USB microphone and speakers are connected!"
echo ""

