#!/bin/bash
# Test if USB-to-CAN adapter supports SLCAN

echo "======================================================================"
echo "Testing SLCAN Support on USB-to-CAN Adapter"
echo "======================================================================"

# Kill any existing slcan
echo ""
echo "1. Cleaning up existing SLCAN interfaces..."
sudo killall slcand 2>/dev/null
sleep 1

# Check if device exists
echo ""
echo "2. Checking USB device..."
if [ ! -e /dev/ttyUSB0 ]; then
    echo "❌ /dev/ttyUSB0 not found!"
    echo "   Check if USB-to-CAN adapter is connected"
    exit 1
fi

ls -la /dev/ttyUSB0
echo "✅ Device found"

# Try to create SLCAN interface
echo ""
echo "3. Attempting to create SLCAN interface..."
echo "   Command: sudo slcand -o -c -s8 /dev/ttyUSB0 slcan0"

sudo slcand -o -c -s8 /dev/ttyUSB0 slcan0 2>&1

if [ $? -eq 0 ]; then
    echo "✅ SLCAN daemon started successfully!"
    
    # Bring up interface
    echo ""
    echo "4. Bringing up slcan0 interface..."
    sudo ip link set slcan0 up
    
    if [ $? -eq 0 ]; then
        echo "✅ Interface is UP!"
        
        # Show interface details
        echo ""
        echo "5. Interface details:"
        ip -details link show slcan0
        
        echo ""
        echo "======================================================================"
        echo "✅ SUCCESS! SLCAN is working!"
        echo "======================================================================"
        echo ""
        echo "Your USB-to-CAN adapter supports SLCAN!"
        echo ""
        echo "Next steps:"
        echo "  1. Use 'slcan0' instead of /dev/ttyUSB0"
        echo "  2. Use SocketCAN commands (candump, cansend)"
        echo "  3. Use python-can with interface='socketcan'"
        echo ""
        echo "Test with:"
        echo "  candump slcan0"
        echo ""
        
    else
        echo "❌ Failed to bring up interface"
        sudo killall slcand
    fi
    
else
    echo "❌ SLCAN not supported or failed to start"
    echo ""
    echo "This means your USB-to-CAN adapter:"
    echo "  - Uses custom protocol (L91)"
    echo "  - Does not support standard SLCAN"
    echo ""
    echo "Solutions:"
    echo "  1. Continue using /dev/ttyUSB0 with L91 protocol"
    echo "  2. Use python-can with serial interface"
    echo "  3. Get a proper CAN adapter (CANable, PEAK, etc.)"
    echo ""
fi

