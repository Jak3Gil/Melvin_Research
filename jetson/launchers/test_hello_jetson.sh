#!/bin/bash
# Simple test to make Jetson say "hello" using Piper TTS

echo "Testing Piper TTS on Jetson - saying 'hello'"
echo "=============================================="
echo ""

# Piper configuration
PIPER_BIN="/home/melvin/piper/piper/piper"
MODEL_PATH="/home/melvin/piper/models/en_US-lessac-medium.onnx"
OUTPUT_FILE="/tmp/hello_test.wav"

# Check if Piper binary exists
if [ ! -f "$PIPER_BIN" ]; then
    echo "Error: Piper binary not found at $PIPER_BIN"
    echo "Please install Piper TTS first."
    exit 1
fi

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Voice model not found at $MODEL_PATH"
    echo "Trying alternative female voice model..."
    MODEL_PATH="/home/melvin/piper/models/en_US-amy-medium.onnx"
    
    if [ ! -f "$MODEL_PATH" ]; then
        echo "Error: No voice models found."
        echo "Please download a voice model first."
        exit 1
    fi
fi

echo "Using voice model: $MODEL_PATH"
echo ""

# Generate the audio
echo "Generating audio for 'hello'..."
echo "hello" | "$PIPER_BIN" --model "$MODEL_PATH" --output_file "$OUTPUT_FILE"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: Failed to generate audio file"
    exit 1
fi

echo "Audio generated successfully!"
echo ""

# List available audio devices
echo "Available audio devices:"
aplay -l
echo ""

# Try to find USB audio device
USB_DEVICE=$(aplay -l | grep -i "usb\|headphone" | head -1 | grep -oP "card \K[0-9]+" | head -1)

if [ -z "$USB_DEVICE" ]; then
    echo "No USB audio device found. Using default device..."
    echo "Playing 'hello' on default device..."
    aplay "$OUTPUT_FILE"
else
    echo "Found USB audio device: card $USB_DEVICE"
    echo "Playing 'hello' on USB device..."
    aplay -D "plughw:$USB_DEVICE,0" "$OUTPUT_FILE" || aplay "$OUTPUT_FILE"
fi

echo ""
echo "Test complete! You should have heard 'hello' through the speakers."
echo ""
echo "To test again, run: bash test_hello_jetson.sh"

