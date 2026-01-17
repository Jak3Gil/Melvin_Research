#!/bin/bash
# Fix microphone volume for USB audio device (same device as speakers)

echo "=========================================="
echo "Fixing USB Audio Device Microphone"
echo "=========================================="
echo ""

# Check USB audio device
echo "Step 1: Checking USB audio device..."
USB_CARD=$(arecord -l | grep -i "usb" | head -1 | grep -oP "card \K[0-9]+" | head -1)

if [ -z "$USB_CARD" ]; then
    echo "⚠ Could not find USB audio device, assuming card 0"
    USB_CARD=0
else
    echo "✓ Found USB audio device on card $USB_CARD"
fi

echo ""
echo "Step 2: Current microphone settings..."
echo "----------------------------------------"
amixer -c $USB_CARD sget Capture 2>/dev/null || echo "Could not get capture settings"

echo ""
echo "Step 3: Setting microphone volume to 80%..."
echo "----------------------------------------"
# Set capture volume
amixer -c $USB_CARD set Capture 80% 2>/dev/null && echo "✓ Capture volume set to 80%" || echo "✗ Failed to set capture volume"

# Enable capture
amixer -c $USB_CARD set Capture cap 2>/dev/null && echo "✓ Capture enabled" || echo "✗ Failed to enable capture"

# Some devices use different control names
amixer -c $USB_CARD set 'Mic Capture Volume' 80% 2>/dev/null && echo "✓ Mic Capture Volume set" || echo "  (Mic Capture Volume not available)"

echo ""
echo "Step 4: Verifying settings..."
echo "----------------------------------------"
amixer -c $USB_CARD sget Capture 2>/dev/null || echo "Could not verify settings"

echo ""
echo "Step 5: Testing microphone..."
echo "----------------------------------------"
echo "Recording 3 seconds - SPEAK LOUDLY into the microphone..."
arecord -D plughw:$USB_CARD,0 -d 3 -f cd /tmp/usb_mic_test.wav 2>/dev/null

if [ -f /tmp/usb_mic_test.wav ]; then
    FILE_SIZE=$(stat -c%s /tmp/usb_mic_test.wav 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -gt 1000 ]; then
        echo "✓ Recording successful ($FILE_SIZE bytes)"
        echo ""
        echo "Playing back - do you hear your voice?"
        aplay -D plughw:$USB_CARD,0 /tmp/usb_mic_test.wav 2>/dev/null || aplay /tmp/usb_mic_test.wav
    else
        echo "⚠ Recording file is very small ($FILE_SIZE bytes) - microphone may still be too quiet"
    fi
else
    echo "✗ Recording failed"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Test microphone levels:"
echo "   python3 test_microphone_jetson.py"
echo ""
echo "2. If still too quiet, try:"
echo "   alsamixer -c $USB_CARD"
echo "   (Press F4 for Capture, increase volume with UP arrow)"
echo ""
echo "3. Or try higher volume:"
echo "   amixer -c $USB_CARD set Capture 90%"
echo "   amixer -c $USB_CARD set Capture 100%"
echo ""
echo "4. Then test voice assistant:"
echo "   python3 voice_assistant_jetson.py"
echo ""

