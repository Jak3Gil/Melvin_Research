#!/bin/bash
# Test Piper TTS installation

export PATH="$PATH:/home/melvin/.local/bin"

echo "Testing Piper TTS installation..."
echo ""

# Check if piper command exists
if command -v piper &> /dev/null; then
    echo "✓ Piper command found"
    piper --version
else
    echo "✗ Piper command not found in PATH"
    echo "Checking ~/.local/bin..."
    if [ -f ~/.local/bin/piper ]; then
        echo "✓ Found piper at ~/.local/bin/piper"
        ~/.local/bin/piper --version
    else
        echo "✗ Piper not found"
    fi
fi

echo ""
echo "Python package check:"
python3 -m pip show piper-tts 2>/dev/null || echo "piper-tts package not installed"

