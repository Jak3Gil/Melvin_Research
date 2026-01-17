#!/bin/bash
# Setup RobStride Actuator Bridge on Jetson
# Based on: https://github.com/RobStride/robstride_actuator_bridge

echo "======================================================================"
echo "RobStride Actuator Bridge Setup"
echo "======================================================================"

# Install dependencies
echo ""
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y net-tools can-utils git

# Setup CAN interface (using can0 which already exists on Jetson)
echo ""
echo "Configuring CAN interface..."
sudo modprobe can
sudo modprobe can_raw
sudo modprobe can_dev

# Set bitrate to 1Mbps (RobStride standard)
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
sudo ifconfig can0 txqueuelen 100

echo ""
echo "CAN0 Status:"
ip -details link show can0

# Clone repository
echo ""
echo "Cloning RobStride actuator bridge..."
cd ~
if [ -d "robstride_actuator_bridge" ]; then
    echo "Repository already exists, pulling latest..."
    cd robstride_actuator_bridge
    git pull
else
    git clone https://github.com/RobStride/robstride_actuator_bridge.git
    cd robstride_actuator_bridge
fi

echo ""
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "CAN interface can0 is configured at 1Mbps"
echo ""
echo "Next steps:"
echo "  1. The C++ code in src/ shows how to control motors"
echo "  2. We can adapt it to Python for motor configuration"
echo "  3. This uses proper SocketCAN, should handle address masks correctly"
echo ""
echo "Key files:"
echo "  - src/motor_control.cpp: Motor control implementation"
echo "  - include/motor_control/motor_control.h: Motor control header"
echo ""

