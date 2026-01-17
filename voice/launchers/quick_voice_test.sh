#!/bin/bash
# Quick test of the voice assistant - makes Melvin say a fun greeting

echo "🤖 Quick Voice Assistant Test"
echo "=============================="
echo ""

TEXT="Hello! I am Melvin, your local voice assistant. All my processing happens right here on the Jetson. I can listen to your questions, think about them, and speak back to you. Let's have a conversation!"

echo "Making Melvin say:"
echo "  '$TEXT'"
echo ""

# Generate speech
echo "🔊 Generating speech..."
/home/melvin/piper/piper/piper \
    --model /home/melvin/piper/models/en_US-lessac-medium.onnx \
    --output_file /tmp/quick_test.wav << EOF
$TEXT
EOF

# Play it
echo "🔈 Playing audio..."
USB_DEVICE=$(aplay -l | grep -i "usb" | head -1 | grep -oP "card \K[0-9]+" | head -1)

if [ -z "$USB_DEVICE" ]; then
    aplay /tmp/quick_test.wav
else
    aplay -D "plughw:$USB_DEVICE,0" /tmp/quick_test.wav
fi

echo ""
echo "✓ Test complete!"
echo ""
echo "To try the full assistant with LLM:"
echo "  bash demo_voice_assistant.sh"
echo ""
echo "To use with microphone:"
echo "  python3 voice_assistant_jetson.py"

