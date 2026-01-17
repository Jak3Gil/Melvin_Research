# Protocol Switch Guide: L91 → RobStride Direct CAN

## Critical Discovery

According to the [official RobStride documentation](https://wiki.seeedstudio.com/robstride_control/), **RobStride motors use direct CAN bus communication, NOT the L91 protocol!**

### The Problem

You've been using:
- ❌ **L91 protocol** over USB-to-Serial (AT commands)
- ❌ **8-bit CAN IDs** (0-255)
- ❌ **Serial communication** at 921600 baud

RobStride motors actually use:
- ✅ **Direct SocketCAN** communication
- ✅ **Extended CAN frames** (29-bit IDs)
- ✅ **Standard CAN bus** at 1 Mbps

## Why Only 5 Motors Were Found

The L91 protocol you've been using is likely for a **different motor controller** or an **adapter/protocol converter**. The missing 10 motors are probably:

1. **Not responding to L91 commands** (wrong protocol)
2. **Configured for direct CAN** communication
3. **Waiting for proper SocketCAN frames**

## Solution: Switch to Proper Protocol

### Step 1: Setup USB-to-CAN as SocketCAN Interface

The USB-to-CAN adapter needs to be configured as a CAN interface (slcan0):

```bash
# Stop any existing slcan
sudo pkill slcand
sudo ip link set slcan0 down

# Start slcan daemon (converts serial to CAN)
sudo slcand -o -c -s8 -S 1000000 /dev/ttyUSB0 slcan0

# Wait a moment
sleep 2

# Bring up the CAN interface
sudo ip link set slcan0 up type can bitrate 1000000

# Verify
ip -details link show slcan0
```

### Step 2: Install CAN Tools

```bash
sudo apt-get update
sudo apt-get install -y can-utils
```

### Step 3: Install RobStride Python Library

```bash
# Option 1: Install from pip (if available)
pip install robstride-dynamics

# Option 2: Clone from GitHub
git clone https://github.com/Seeed-Projects/RobStride_Control.git
cd RobStride_Control/python
pip install .
```

### Step 4: Scan for Motors

```python
from robstride_dynamics import RobstrideBus

# Initialize CAN bus
bus = RobstrideBus('slcan0')

# Scan for motors
motors = bus.scan_channel()
print(f"Found motors: {motors}")
```

### Step 5: Control Motors

```python
from robstride_dynamics import RobstrideBus

bus = RobstrideBus('slcan0')

# Control motor ID 1 in MIT mode
motor_id = 1
target_position = 0.0

bus.write_operation_frame(
    motor_id=motor_id,
    p_des=target_position,
    v_des=0.0,
    kp=500.0,
    kd=5.0,
    t_ff=0.0
)
```

## CAN Frame Format

### RobStride Protocol (from documentation):

- **Frame Type**: Extended CAN (29-bit ID)
- **ID Format**: `0x200 + motor_id` for control, `0x200 + motor_id + 0x100` for status
- **Bitrate**: 1 Mbps (1,000,000 bps)
- **Data Length**: 8 bytes

### Example CAN Frames:

```bash
# Control Motor 1 (MIT mode)
cansend slcan0 201#<8_bytes_of_data>

# Request status from Motor 1
cansend slcan0 301#
```

## Differences: L91 vs RobStride Protocol

| Aspect | L91 Protocol (Current) | RobStride Protocol (Correct) |
|--------|------------------------|------------------------------|
| **Interface** | Serial port (`/dev/ttyUSB0`) | CAN interface (`slcan0`) |
| **Protocol** | AT commands | Direct CAN frames |
| **ID Format** | 8-bit (0-255) | Extended 29-bit |
| **Bitrate** | 921600 baud (serial) | 1 Mbps (CAN) |
| **Library** | Custom AT command parsing | `robstride_dynamics` |
| **Motor IDs** | 1-15 (assumed) | 1-15 (properly scanned) |

## Expected Results

After switching to proper protocol:

1. **All 15 motors should be found** using `bus.scan_channel()`
2. **Each motor has unique CAN ID** (properly configured)
3. **Individual motor control** works correctly
4. **No more range-based responses** (that was L91 adapter behavior)

## Troubleshooting

### If slcan0 doesn't work:

1. Check if USB-to-CAN adapter supports slcan:
   ```bash
   dmesg | grep -i can
   ```

2. Try different slcan parameters:
   ```bash
   # Try 500kbps instead
   sudo slcand -o -c -s8 -S 500000 /dev/ttyUSB0 slcan0
   ```

3. Check if adapter needs different driver:
   ```bash
   lsusb
   # Identify adapter chipset
   ```

### If motors still not found:

1. Monitor CAN traffic:
   ```bash
   candump slcan0
   ```

2. Verify motors are powered

3. Check CAN bus termination (120Ω resistors)

4. Verify bitrate matches motor configuration

## Next Steps

1. ✅ Run `setup_robstride_can.py` to setup CAN interface
2. ✅ Install RobStride library
3. ✅ Scan for all 15 motors
4. ✅ Test individual motor control
5. ✅ Update control scripts to use proper protocol

## References

- [RobStride Control Documentation](https://wiki.seeedstudio.com/robstride_control/)
- [GitHub Repository](https://github.com/Seeed-Projects/RobStride_Control)
- SocketCAN Documentation: `man slcan`

