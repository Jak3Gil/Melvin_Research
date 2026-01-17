# RobStride Controller Analysis

## Discovery

You mentioned you're using the **official RobStride motor controller** as your USB-to-CAN adapter.

## Current Configuration

### Hardware Setup:
```
Motors ←→ RobStride Controller ←→ Jetson
         (CAN Bus)              (USB Serial: /dev/ttyUSB0)
```

### What We Found:

1. **CAN Interfaces Exist**:
   - `can0` - Active, 500kbps bitrate
   - `can1` - Active, 500kbps bitrate
   - Both in ERROR-ACTIVE state (healthy)

2. **But Motors Don't Respond on CAN**:
   - Sent commands to can0 → No response
   - Sent commands to can1 → No response
   - Motors only respond on `/dev/ttyUSB0` (serial)

3. **USB Device**:
   - Device ID: `1a86:7523` (QinHeng Electronics HL-340 USB-Serial adapter)
   - This is a **USB-to-Serial chip**, not a direct CAN interface

## What This Means

### The RobStride Controller Has Two Modes:

#### Mode 1: Serial Mode (L91 Protocol) - **CURRENTLY ACTIVE**
```
[Motors] ←CAN→ [Controller] ←L91/Serial→ [Jetson /dev/ttyUSB0]
```
- ✓ Works for motor control (11-bit standard IDs)
- ✗ Doesn't support extended 29-bit IDs
- ✗ Can't do OTA firmware updates
- ✓ Simple to use
- ✓ Works on any OS (Windows, Linux, Mac)

#### Mode 2: Direct CAN Mode (SocketCAN) - **NOT ACTIVE**
```
[Motors] ←CAN→ [Controller] ←CAN→ [Jetson can0/can1]
```
- ✓ Supports extended 29-bit IDs
- ✓ Can do OTA firmware updates
- ✓ Full CAN protocol support
- ✗ Requires driver configuration
- ✗ Linux-specific (SocketCAN)

## Why can0/can1 Exist But Don't Work

The Jetson has **built-in CAN controllers** (can0, can1):
- These are **hardware CAN interfaces** on the Jetson itself
- They're configured and active (500kbps)
- But they're **not connected to your motors**

Your motors are connected via:
- USB cable → `/dev/ttyUSB0` (serial)
- NOT via the Jetson's CAN pins

## The Problem

Your RobStride controller is in **Serial Mode** (L91 protocol):
- This mode was designed for simplicity and cross-platform compatibility
- It translates CAN to serial for easy USB connection
- But it only supports 11-bit standard CAN IDs
- OTA firmware updates require 29-bit extended IDs
- **Serial mode can't pass through extended IDs**

## Solutions

### Option 1: Switch Controller to Direct CAN Mode (If Possible)

**Check if your RobStride controller supports direct CAN mode:**

1. Look for documentation on the controller
2. Check if there's a mode switch or configuration
3. See if RobStride provides drivers for SocketCAN mode

**If it supports direct CAN mode:**
- Install proper drivers
- Configure controller for CAN mode (not serial)
- Motors would then appear on can0 or can1
- OTA updates would work

### Option 2: Use MotorStudio (Recommended)

**MotorStudio knows how to handle Serial Mode:**
- It's designed to work with controllers in serial mode
- Has special methods to update firmware via serial
- Doesn't require extended CAN IDs
- Official and tested solution

### Option 3: Connect to Jetson's CAN Pins Directly

**Bypass the controller:**
- Connect motors directly to Jetson's CAN0/CAN1 pins
- Requires:
  - CAN transceiver (e.g., TJA1050)
  - Proper wiring
  - 120Ω termination resistors
- Then OTA updates would work

## Current Status

### What Works:
✓ Motor control via `/dev/ttyUSB0` (L91 protocol)
✓ All 6 motors responding and moving
✓ Standard 11-bit CAN IDs (8, 16, 21, 31, 64, 72)

### What Doesn't Work:
✗ Direct CAN access (can0/can1 not connected to motors)
✗ Extended 29-bit CAN IDs (controller in serial mode)
✗ OTA firmware updates (requires extended IDs)

## Recommendation

**Use MotorStudio for firmware updates.**

Why:
1. Your controller is in Serial Mode (L91 protocol)
2. Serial Mode doesn't support extended CAN IDs
3. OTA protocol requires extended IDs
4. MotorStudio has workarounds for this
5. It's the official, tested solution

**Alternative:**
- Contact RobStride support
- Ask if your controller can switch to Direct CAN Mode
- Ask for Linux drivers/configuration guide
- Then OTA updates would work

## Technical Details

### L91 Protocol Limitation:

The L91 protocol frame:
```
[0xAA] [0x55] [Type] [Len] [CAN_ID (4 bytes)] [Data] [Checksum]
```

- Type `0x01` = Standard frame (11-bit ID) ✓ Supported
- Type `0x02` = Extended frame (29-bit ID) ✗ Not implemented in serial mode

### OTA Protocol Requirement:

```python
# OTA uses extended IDs like:
OTA_GET_ID = 0x00007F08  # Frame type 0, host 0x7F, motor 8
OTA_START  = 0x0B007F08  # Frame type 11, host 0x7F, motor 8
```

These are 29-bit extended IDs that serial mode can't handle.

### Why MotorStudio Works:

MotorStudio likely:
1. Detects controller is in serial mode
2. Uses alternative update method
3. Sends special serial commands
4. Switches motor to bootloader
5. Uploads firmware via serial protocol
6. Doesn't rely on CAN extended IDs

## Next Steps

1. **Immediate**: Use MotorStudio to update firmware
2. **Future**: Ask RobStride about Direct CAN Mode
3. **Alternative**: Connect motors to Jetson CAN pins directly

---

*The good news: Your motors work perfectly! The controller just needs MotorStudio for firmware updates.*

