#!/bin/bash
# Check if voice assistant is ready to run

echo "=========================================="
echo "Voice Assistant Dependency Check"
echo "=========================================="
echo ""

# Run the dependency check from the Python script
python3 << 'EOF'
import sys
import os
import subprocess

print("Checking dependencies...")
print("=" * 50)

# Check Piper
piper_bin = "/home/melvin/piper/piper/piper"
piper_model = "/home/melvin/piper/models/en_US-lessac-medium.onnx"

if os.path.exists(piper_bin) and os.path.exists(piper_model):
    print("✓ Piper TTS: Installed")
else:
    print("✗ Piper TTS: Not found")

# Check Whisper
try:
    import whisper
    print("✓ Whisper STT: Installed")
except ImportError:
    print("✗ Whisper STT: Not installed")

# Check Ollama
try:
    result = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print("✓ Ollama LLM: Installed")
        if "llama3.2:1b" in result.stdout:
            print("  ✓ Model 'llama3.2:1b' available")
    else:
        print("✗ Ollama LLM: Not running")
except Exception:
    print("✗ Ollama LLM: Not installed")

# Check PyAudio
try:
    import pyaudio
    print("✓ PyAudio: Installed")
except ImportError:
    print("✗ PyAudio: Not installed")

print("=" * 50)
print("\n✓ All dependencies are ready!")
print("\nTo run the voice assistant:")
print("  python3 voice_assistant_jetson.py")
EOF

