#!/bin/bash
# Simple USB microphone test

echo "Testing USB microphone (card 0)..."
echo ""

echo "Recording 3 seconds - SPEAK LOUDLY..."
arecord -D plughw:0,0 -d 3 -f cd /tmp/mic_test.wav 2>&1

if [ -f /tmp/mic_test.wav ]; then
    FILE_SIZE=$(stat -c%s /tmp/mic_test.wav 2>/dev/null || echo "0")
    echo ""
    echo "✓ Recording created: $FILE_SIZE bytes"
    
    if [ "$FILE_SIZE" -gt 10000 ]; then
        echo "✓ File size looks good"
        echo ""
        echo "Playing back - do you hear your voice?"
        aplay -D plughw:0,0 /tmp/mic_test.wav 2>&1 | head -3
    else
        echo "⚠ File is very small - microphone may not be working"
    fi
else
    echo "✗ Recording failed - no file created"
fi

echo ""
echo "Checking microphone settings:"
amixer -c 0 sget 'Mic Capture Volume' 2>/dev/null || amixer -c 0 sget 'Mic' 2>/dev/null

