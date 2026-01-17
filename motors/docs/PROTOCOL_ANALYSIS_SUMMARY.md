# Protocol Analysis Summary

## Critical Discovery

Based on the [official RobStride documentation](https://wiki.seeedstudio.com/robstride_control/), RobStride motors are designed to use **direct SocketCAN communication**, not L91 protocol.

## Current Situation

### What You've Been Using:
- **L91 Protocol** via USB-to-Serial adapter (`/dev/ttyUSB0` at 921600 baud)
- **AT commands** format (`AT 00 07 e8 <id> ...`)
- **8-bit CAN IDs** (0-255)

### What RobStride Actually Uses:
- **Direct SocketCAN** interface (`slcan0` or `can0`)
- **Extended CAN frames** (29-bit IDs)
- **Standard CAN bus** at 1 Mbps

## The Problem: Missing 10 Motors

You've found **5 motors** responding via L91 protocol:
- Motor 1: IDs 1-15
- Motor 2: IDs 16-20  
- Motor 3: IDs 21-30
- Motor 4: IDs 31-39
- Motor 8: IDs 64-79

**10 motors are missing** - likely because:
1. They're not responding to L91 commands (wrong protocol)
2. The L91 protocol might be a translation layer that only works for some motors
3. Missing motors may require direct CAN protocol

## Possible Explanations

### Theory 1: USB-to-CAN Adapter is Protocol Converter
The USB-to-CAN adapter you're using might be:
- A **protocol converter** that translates L91/AT commands to CAN
- Only partially working (converting for some motors, not others)
- The missing motors might need **direct CAN** instead of converted commands

### Theory 2: Mixed Protocol Setup
- **5 motors** might be configured for L91 protocol (via adapter)
- **10 motors** might be configured for direct CAN (not responding to L91)

### Theory 3: Hardware Configuration
- Missing motors might need **hardware configuration** (DIP switches, etc.)
- They might be on a **different CAN segment** or need different initialization

## Next Steps

### Option 1: Try SocketCAN Setup (Recommended)
Even if slcan failed, try setting up CAN interface directly:

```bash
# Check what USB-to-CAN adapters are available
lsusb
dmesg | grep -i can

# Some adapters create can0 directly
ip link show

# Try setting up can0 if it exists
sudo ip link set can0 up type can bitrate 1000000
```

### Option 2: Use RobStride Python Library
Install and try the official library:

```bash
# Clone RobStride control library
git clone https://github.com/Seeed-Projects/RobStride_Control.git
cd RobStride_Control/python
pip install .

# Try using it
python3 -c "
from robstride_dynamics import RobstrideBus
bus = RobstrideBus('can0')  # or 'slcan0'
motors = bus.scan_channel()
print(f'Found: {motors}')
"
```

### Option 3: Check Adapter Documentation
Your USB-to-CAN adapter (CH340 chipset) might:
- Have specific setup requirements
- Need different driver/firmware
- Support different protocols

### Option 4: Direct CAN Testing
Try sending CAN frames directly:

```bash
# Monitor CAN traffic
candump can0

# Send test frame to motor 1
cansend can0 201#0000000000000000
```

### Option 5: Hybrid Approach
Since 5 motors work with L91:
- **Continue using L91 for the 5 working motors**
- **Set up direct CAN for the 10 missing motors**
- Use both protocols simultaneously if needed

## Important Questions

1. **What is your USB-to-CAN adapter model?**
   - Is it specifically a "L91-to-CAN" adapter?
   - Or a generic USB-to-CAN adapter?

2. **How are motors physically connected?**
   - All on one CAN bus?
   - Multiple CAN segments?
   - Daisy-chain?

3. **Can you access motors via another interface?**
   - Direct CAN interface on Jetson?
   - Another CAN adapter?

## Recommendations

1. ✅ **First Priority**: Try to get SocketCAN working with your adapter
   - Check adapter documentation
   - Try different bitrates (500kbps, 1Mbps)
   - Check if adapter needs specific driver

2. ✅ **Second Priority**: Install RobStride library and test
   - May have built-in adapter support
   - Proper protocol implementation

3. ✅ **Third Priority**: Physical inspection
   - Check if missing motors are powered
   - Verify CAN bus wiring
   - Check for CAN bus termination resistors

4. ✅ **Fourth Priority**: Contact manufacturer
   - Ask Robstride about CAN ID configuration
   - Ask about L91 vs direct CAN protocol
   - Request motor configuration guide

## Resources

- [RobStride Control Documentation](https://wiki.seeedstudio.com/robstride_control/)
- [RobStride GitHub Repository](https://github.com/Seeed-Projects/RobStride_Control)
- SocketCAN Documentation: `man slcan`, `man can`

## Conclusion

The **root cause** of missing 10 motors is likely:
- **Protocol mismatch** - L91 adapter might not support all motors
- **Need direct CAN** - Missing motors may require SocketCAN protocol
- **Configuration issue** - Motors may need hardware/software configuration

**Immediate action**: Try to set up direct CAN interface and use RobStride library to scan for all motors.

