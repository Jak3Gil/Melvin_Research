#!/bin/bash
# Test different CAN bitrates to find motors

echo "======================================================================"
echo "CAN BITRATE TEST - Find the correct bitrate for motors"
echo "======================================================================"

# Common bitrates for RobStride motors
BITRATES=(250000 500000 1000000 2000000)

for BITRATE in "${BITRATES[@]}"; do
    echo ""
    echo "======================================================================"
    echo "Testing bitrate: $BITRATE"
    echo "======================================================================"
    
    # Configure can0
    echo "Configuring can0..."
    sudo ip link set can0 down
    sudo ip link set can0 type can bitrate $BITRATE
    sudo ip link set can0 up
    
    sleep 0.5
    
    # Check status
    echo "CAN0 Status:"
    ip -details link show can0 | grep bitrate
    
    # Listen for traffic (background)
    echo ""
    echo "Listening for CAN traffic (5 seconds)..."
    timeout 5 candump can0 &
    CANDUMP_PID=$!
    
    sleep 1
    
    # Try sending enable commands to common IDs
    echo "Sending test commands to motor IDs: 1, 8, 16, 20, 24, 31, 32, 64, 72..."
    
    for MOTOR_ID in 1 8 16 20 24 31 32 64 72; do
        # Send CAN frame: ID=MOTOR_ID, Data=01 00 00 00 00 00 00 00
        cansend can0 $(printf "%03X" $MOTOR_ID)#0100000000000000
        sleep 0.05
    done
    
    # Wait for candump to finish
    wait $CANDUMP_PID 2>/dev/null
    
    echo ""
    echo "Test complete for bitrate $BITRATE"
    sleep 1
done

echo ""
echo "======================================================================"
echo "Testing can1 interface"
echo "======================================================================"

# Also try can1 at 1000000 (most common for RobStride)
echo "Configuring can1 at 1000000..."
sudo ip link set can1 down
sudo ip link set can1 type can bitrate 1000000
sudo ip link set can1 up

sleep 0.5

echo "CAN1 Status:"
ip -details link show can1 | grep bitrate

echo ""
echo "Listening for CAN traffic on can1 (5 seconds)..."
timeout 5 candump can1 &
CANDUMP_PID=$!

sleep 1

echo "Sending test commands on can1..."
for MOTOR_ID in 1 8 16 20 24 31 32 64 72; do
    cansend can1 $(printf "%03X" $MOTOR_ID)#0100000000000000
    sleep 0.05
done

wait $CANDUMP_PID 2>/dev/null

echo ""
echo "======================================================================"
echo "FINAL STATUS"
echo "======================================================================"
echo ""
echo "If you saw CAN messages above, motors are responding!"
echo "If not, check:"
echo "  1. Are motors physically connected to can0 or can1?"
echo "  2. Are motors powered on?"
echo "  3. Is CAN-H and CAN-L wired correctly?"
echo "  4. Are 120Ω termination resistors installed?"
echo ""
echo "Current CAN configuration:"
ip link show can0 | head -2
ip link show can1 | head -2
echo ""

