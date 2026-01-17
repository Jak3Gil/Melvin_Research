#!/bin/bash
# Quick guide to fix microphone volume on Jetson

echo "=========================================="
echo "Fixing USB Microphone Volume"
echo "=========================================="
echo ""

echo "Your microphone audio level is very low (54/32767)"
echo "This needs to be fixed for the voice assistant to work."
echo ""

echo "Step 1: Check current audio devices"
echo "----------------------------------------"
arecord -l
echo ""

echo "Step 2: Test microphone recording"
echo "----------------------------------------"
echo "Recording 3 seconds - SPEAK LOUDLY..."
arecord -D plughw:0,0 -d 3 -f cd /tmp/mic_test.wav 2>/dev/null

if [ -f /tmp/mic_test.wav ]; then
    echo "✓ Recording saved to /tmp/mic_test.wav"
    echo ""
    echo "Playing it back - do you hear your voice?"
    aplay /tmp/mic_test.wav
    echo ""
else
    echo "✗ Recording failed"
    echo ""
fi

echo "Step 3: Adjust microphone volume"
echo "----------------------------------------"
echo ""
echo "To increase microphone volume, run:"
echo "  alsamixer"
echo ""
echo "Instructions:"
echo "  1. Press F4 to switch to 'Capture' view"
echo "  2. Use arrow keys to select 'Capture' volume"
echo "  3. Press UP arrow to increase volume (aim for 80-100%)"
echo "  4. Press ESC to exit"
echo ""
echo "Or use this command to set capture volume to 80%:"
echo "  amixer set Capture 80%"
echo ""
echo "Step 4: Test again"
echo "----------------------------------------"
echo "After adjusting volume, test again:"
echo "  python3 test_microphone_jetson.py"
echo ""

