#!/bin/bash
# Demo the voice assistant pipeline without microphone
# Tests: Text -> LLM -> TTS -> Audio output

echo "=========================================="
echo "Voice Assistant Demo (Text-based)"
echo "=========================================="
echo ""
echo "This demo tests the LLM + TTS pipeline"
echo "without requiring a microphone."
echo ""

# Test question
QUESTION="What is 2 plus 2?"

echo "Question: '$QUESTION'"
echo ""

echo "Step 1: Getting LLM response..."
echo "----------------------------------------"
RESPONSE=$(ollama run llama3.2:1b "$QUESTION" 2>/dev/null)

if [ -z "$RESPONSE" ]; then
    echo "✗ Failed to get LLM response"
    exit 1
fi

echo "Response: $RESPONSE"
echo ""

echo "Step 2: Converting to speech..."
echo "----------------------------------------"
OUTPUT_FILE="/tmp/demo_response.wav"

echo "$RESPONSE" | /home/melvin/piper/piper/piper \
    --model /home/melvin/piper/models/en_US-lessac-medium.onnx \
    --output_file "$OUTPUT_FILE" 2>&1 | grep -E "(Loaded|Real-time|Terminated)"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "✗ Failed to generate audio"
    exit 1
fi

echo ""
echo "Step 3: Playing audio..."
echo "----------------------------------------"

# Find USB audio device
USB_DEVICE=$(aplay -l | grep -i "usb\|headphone" | head -1 | grep -oP "card \K[0-9]+" | head -1)

if [ -z "$USB_DEVICE" ]; then
    echo "Using default audio device..."
    aplay "$OUTPUT_FILE"
else
    echo "Using USB audio device (card $USB_DEVICE)..."
    aplay -D "plughw:$USB_DEVICE,0" "$OUTPUT_FILE" || aplay "$OUTPUT_FILE"
fi

echo ""
echo "=========================================="
echo "✓ Demo complete!"
echo "=========================================="
echo ""
echo "The voice assistant pipeline is working:"
echo "  1. ✓ LLM (Ollama) generated response"
echo "  2. ✓ TTS (Piper) converted to speech"
echo "  3. ✓ Audio played through speakers"
echo ""
echo "To use with microphone (STT):"
echo "  python3 voice_assistant_jetson.py"
echo ""

