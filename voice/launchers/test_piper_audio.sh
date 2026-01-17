#!/bin/bash
# Test Piper TTS with USB headphones

echo "Testing Piper TTS with USB Headphones"
echo "======================================"
echo ""

# Model path
MODEL_PATH="$HOME/piper/models/en_US-amy-medium.onnx"
PIPER_BIN="$HOME/piper/piper/piper"
OUTPUT_FILE="$HOME/test_tts.wav"

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Voice model not found at $MODEL_PATH"
    exit 1
fi

# Generate test audio
echo "Generating test audio..."
echo "Hello, this is a test of Piper text to speech running on the Jetson. If you can hear this clearly, the USB headphones are working correctly." | \
    "$PIPER_BIN" --model "$MODEL_PATH" --output_file "$OUTPUT_FILE"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: Failed to generate audio file"
    exit 1
fi

echo "Audio generated: $OUTPUT_FILE"
echo ""

# List available audio devices
echo "Available audio devices:"
aplay -l
echo ""

# Try to find USB audio device
USB_DEVICE=$(aplay -l | grep -i "usb\|headphone" | head -1 | grep -oP "card \K[0-9]+" | head -1)

if [ -z "$USB_DEVICE" ]; then
    echo "No USB audio device found in list. Trying default device..."
    echo "Playing audio on default device..."
    aplay "$OUTPUT_FILE"
else
    echo "Found USB audio device: card $USB_DEVICE"
    echo "Playing audio on USB device..."
    aplay -D "plughw:$USB_DEVICE,0" "$OUTPUT_FILE" || aplay "$OUTPUT_FILE"
fi

echo ""
echo "Test complete!"

