# RobStride Motor Configuration - Complete Solution

## The Problem

All 15 motors have address masking and respond to overlapping ID ranges. We were using the wrong interface (USB serial `/dev/ttyUSB0` with L91 protocol) instead of the proper CAN interface.

## The Solution: Use SocketCAN with MIT Protocol

Based on [RobStride actuator bridge](https://github.com/RobStride/robstride_actuator_bridge), motors should be controlled via:
- **Interface**: SocketCAN (can0 or can1)
- **Protocol**: MIT mode (not L91)
- **Bitrate**: 1000000 (1Mbps)

## Setup Instructions

### 1. Configure CAN Interface

```bash
# On Jetson
sudo modprobe can
sudo modprobe can_raw  
sudo modprobe can_dev

# Configure can0 at 1Mbps
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
sudo ifconfig can0 txqueuelen 100

# Verify
ip -details link show can0
```

### 2. Check Motor Connection

**IMPORTANT**: Motors must be physically connected to:
- Jetson's **CAN0** pins (not USB adapter)
- OR use a proper CAN adapter that creates can0 interface

The `/dev/ttyUSB0` adapter we were using is for:
- L91 protocol only
- Limited functionality
- Cannot properly clear address masks

### 3. Test with SocketCAN

```bash
# Install python-can
pip3 install python-can

# Run test
python3 configure_motors_socketcan.py
```

### 4. Motor Configuration via SocketCAN

Once motors respond on can0, use MIT protocol commands:
- Enable: `0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFC`
- Disable: `0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFD`
- Set Zero: `0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFE`

## Current Status

### What Works:
✅ Found RobStride USB-to-CAN adapter protocol (L91)
✅ Can communicate with motors via `/dev/ttyUSB0`
✅ Can move motors
✅ Identified address masking issue

### What Doesn't Work:
❌ Cannot clear address masks via L91 protocol
❌ All motors respond to overlapping IDs
❌ SET_CAN_ID adds IDs but doesn't remove masks

## Next Steps

### Option A: Use Proper CAN Interface (RECOMMENDED)

1. **Check Physical Connection**:
   - Are motors connected to Jetson CAN0 pins?
   - Or only to USB adapter?

2. **If connected to CAN0**:
   - Configure can0 (see setup above)
   - Run `configure_motors_socketcan.py`
   - Use MIT protocol for proper control

3. **If only USB adapter**:
   - Get proper CAN connection to Jetson
   - Or use RobStride Motor Studio on Windows

### Option B: Physical Isolation (WORKS BUT TEDIOUS)

1. Disconnect 14 motors from CAN bus
2. Configure the 1 connected motor via `/dev/ttyUSB0`
3. Repeat for all 15 motors

### Option C: RobStride Motor Studio (EASIEST)

1. Download from robstride.com
2. Run on Windows PC
3. Connect USB-to-CAN adapter to PC
4. Configure all motors via GUI

## Files Created

- `setup_robstride_bridge.sh`: Setup script for SocketCAN
- `configure_motors_socketcan.py`: Python SocketCAN motor control
- `find_motors_robstride_adapter.py`: Working L91 protocol scanner
- `move_motor_test.py`: Working L91 motor movement
- `test_all_working_motors.py`: Test multiple motors

## Summary

The USB-to-CAN adapter with L91 protocol is **working** but **limited**. For proper motor configuration and control, you need:

1. **SocketCAN interface** (can0/can1)
2. **MIT protocol** (not L91)
3. **Proper CAN connection** to Jetson

OR use RobStride Motor Studio software on Windows for easy configuration.

