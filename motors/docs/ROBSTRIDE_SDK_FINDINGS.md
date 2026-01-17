# RobStride SDK Findings

## SDK Discovery

Found a RobStride SDK at: https://github.com/LyraLiu1208/robstride-sdk

### SDK Features:
- ✅ Uses **python-can** library for SocketCAN communication
- ✅ Supports direct CAN bus communication (not L91 protocol)
- ✅ Proper RobStride protocol implementation
- ✅ Supports multiple motor types (RS05, RS09, RS03, RS06)
- ✅ Thread-safe CAN communication
- ✅ Command-line interface included

### SDK API:
```python
from robstride import RobStrideMotor, MotorType

motor = RobStrideMotor(
    can_id=1,
    interface='can0',  # CAN interface name
    motor_type=MotorType.RS05
)

motor.connect()
motor.enable()
motor.set_position(1.0, 5.0)  # position, speed_limit
motor.disable()
motor.disconnect()
```

## Current Status

### CAN Interfaces Available:
- ✅ `can0` - UP and active
- ✅ `can1` - UP and active  
- ⚠️ `slcan0` - DOWN

### Test Results:
- ❌ **No motors found** using SDK with can0/can1
- ⚠️ **CAN buffer full errors** - suggests interface is active but may be misconfigured

## Issues Encountered

1. **"No buffer space available [Error Code 105]"**
   - CAN transmit buffer is full
   - May indicate:
     - CAN interface is sending/receiving too much traffic
     - Buffer size too small
     - Interface needs reset/restart

2. **No motors responding**
   - Motors may not be on can0/can1
   - Motors may need different initialization
   - Protocol mismatch (SDK vs actual motors)

## Next Steps

### 1. Check CAN Interface Configuration
```bash
# Check interface details
ip -details link show can0
ip -details link show can1

# Check CAN statistics
cat /proc/net/can/stats

# Check for errors
dmesg | grep -i can
```

### 2. Monitor CAN Traffic
```bash
# Monitor can0
candump can0

# Monitor can1
candump can1

# Look for any motor responses
```

### 3. Verify Motors Are On These Interfaces
- The L91 protocol worked on `/dev/ttyUSB0` (serial)
- But SDK needs CAN interfaces (`can0`, `can1`)
- **Question**: Are the motors actually on can0/can1, or are they on the USB-to-CAN adapter?

### 4. Map USB-to-CAN to CAN Interface
The USB-to-CAN adapter (`/dev/ttyUSB0`) might need to be:
- Set up as `slcan0` (Serial Line CAN)
- Or mapped to `can0`/`can1`

### 5. Try Direct CAN Commands
```bash
# Send test frame to motor 1 (RobStride protocol)
# Format depends on RobStride protocol specification
cansend can0 201#0000000000000000

# Monitor for responses
candump can0
```

## Protocol Comparison

| Aspect | L91 (Current Working) | RobStride SDK (Trying) |
|--------|----------------------|------------------------|
| **Interface** | `/dev/ttyUSB0` (serial) | `can0`/`can1` (CAN) |
| **Protocol** | AT commands → CAN | Direct CAN frames |
| **Status** | ✅ 5 motors found | ❌ 0 motors found |
| **Issue** | Wrong protocol? | Interface mismatch? |

## Hypothesis

**The motors that respond to L91 might actually be:**
- Using a protocol converter (L91 → CAN)
- Connected through a different path
- The missing 10 motors might be on a direct CAN interface

**Possible Setup:**
```
Motors 1-5: USB-to-CAN adapter (/dev/ttyUSB0) → L91 protocol ✓
Motors 6-15: Direct CAN interface (can0/can1) → Need SDK ✗
```

## Recommendations

1. **Check if `/dev/ttyUSB0` maps to can0/can1**
   ```bash
   dmesg | grep ttyUSB0
   ls -l /dev/ | grep ttyUSB
   ```

2. **Try setting up slcan0 from /dev/ttyUSB0**
   ```bash
   sudo slcand -o -c -s8 -S 1000000 /dev/ttyUSB0 slcan0
   sudo ip link set slcan0 up type can bitrate 1000000
   python3 scan_with_robstride_sdk.py slcan0
   ```

3. **Use L91 for working motors, SDK for missing motors**
   - Keep using L91 protocol for the 5 working motors
   - Use SDK to find the 10 missing motors on CAN interfaces

4. **Check motor documentation**
   - How should motors be configured for CAN communication?
   - What CAN IDs should motors have?
   - Are there DIP switches or configuration tools?

## References

- [RobStride SDK](https://github.com/LyraLiu1208/robstride-sdk)
- [RobStride Control Guide](https://wiki.seeedstudio.com/robstride_control/)
- [python-can Documentation](https://python-can.readthedocs.io/)

