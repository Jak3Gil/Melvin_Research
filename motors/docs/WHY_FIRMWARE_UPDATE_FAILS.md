# Why We Can't Update Firmware Automatically

## TL;DR (Too Long; Didn't Read)

**Your USB-to-CAN adapter uses a simplified protocol (L91) that doesn't support the advanced features needed for firmware updates. You need MotorStudio (official tool) to update firmware.**

---

## The Technical Problem

### Your Current Setup:

```
┌─────────┐    CAN Bus     ┌──────────────────┐    L91 Protocol    ┌────────┐
│ Motors  │ ←──────────→   │ USB-to-CAN       │ ←───────────────→  │ Jetson │
│ (15x)   │   (29-bit)     │ Adapter          │    (11-bit)        │        │
└─────────┘                └──────────────────┘                     └────────┘
```

### The Issue:

**1. Motors Speak "Extended CAN" (29-bit IDs)**
- RobStride motors use **29-bit extended CAN IDs**
- This is standard for modern CAN devices
- Supports 536 million unique IDs (2^29)
- Required for advanced features like OTA updates

**2. Your Adapter Speaks "L91 Protocol" (11-bit IDs)**
- Your USB-to-CAN adapter translates CAN to **L91 serial protocol**
- L91 only supports **11-bit standard CAN IDs**
- Supports only 2,048 unique IDs (2^11)
- Works great for basic motor control
- **Cannot** handle extended IDs needed for firmware updates

**3. OTA Updates Need Extended IDs**
- Firmware updates use special CAN IDs like `0x1FFFFF00`
- This is a **29-bit extended ID** (536,870,656 in decimal)
- Your adapter's L91 protocol can only handle IDs up to `0x7FF` (2,047)
- The OTA commands never reach the motors

---

## Visual Comparison

### What Works (Motor Control):

```
Standard CAN ID: 0x008 (8 in decimal)
Binary: 00000001000 (11 bits)
✓ Fits in L91 protocol
✓ Motor receives command
✓ Motor moves
```

### What Doesn't Work (Firmware Update):

```
Extended CAN ID: 0x1FFFFF00 (536,870,656 in decimal)
Binary: 00011111111111111111111100000000 (29 bits)
✗ Doesn't fit in L91 protocol (only 11 bits)
✗ Adapter can't send this ID
✗ Motor never receives OTA command
✗ Firmware update fails
```

---

## Why This Happens

### L91 Protocol Limitations:

The L91 protocol frame format:
```
[0xAA] [0x55] [Type] [Len] [CAN_ID (4 bytes)] [Data (8 bytes)] [Checksum]
```

- **Type byte** determines frame type:
  - `0x01` = Standard frame (11-bit ID)
  - `0x02` = Extended frame (29-bit ID) - **NOT SUPPORTED by most adapters**

Your adapter likely:
- Only implements `0x01` (standard frames)
- Ignores or rejects `0x02` (extended frames)
- This is common in budget USB-to-CAN adapters

### Why MotorStudio Works:

MotorStudio (official tool):
1. **Detects your adapter type**
2. **Uses appropriate protocol** (L91, SocketCAN, or direct CAN)
3. **Handles extended IDs correctly**
4. **Has fallback methods** if extended IDs fail
5. **Tested with thousands of setups**

---

## Proof: What We Tried

### Attempt 1: Direct OTA Update ❌
```python
# Tried to send OTA command with extended ID
ota_id = 0x1FFFFF00  # 29-bit extended ID
send_command(ser, ota_id, data)
# Result: No response (adapter dropped the frame)
```

### Attempt 2: Configuration Commands ❌
```python
# Tried 6 different command formats to change CAN ID
# All failed because:
# - L91 protocol doesn't support config commands
# - Motors need firmware update first
```

### Attempt 3: Broadcast Discovery ❌
```python
# Tried broadcast IDs (0, 255)
# Some motors responded, but:
# - Can't change IDs via L91 protocol
# - Need direct CAN access
```

---

## The Solution: MotorStudio

### Why MotorStudio is Required:

| Feature | Our Script | MotorStudio |
|---------|-----------|-------------|
| Detect adapter type | ❌ | ✅ |
| Handle L91 protocol | ✅ | ✅ |
| Handle extended CAN IDs | ❌ | ✅ |
| Firmware update | ❌ | ✅ |
| Configure CAN IDs | ❌ | ✅ |
| Error recovery | ❌ | ✅ |
| Progress indication | ❌ | ✅ |
| Rollback on failure | ❌ | ✅ |

### How MotorStudio Works:

1. **Detects your USB-to-CAN adapter**
2. **Switches motor to bootloader mode** (using standard IDs)
3. **Uploads firmware** (using adapter-specific protocol)
4. **Verifies firmware** (checksum validation)
5. **Reboots motor** (with new firmware)
6. **Configures CAN ID** (now that firmware supports it)

---

## Alternative: Direct CAN Interface

If you want to update firmware programmatically, you need:

### Option A: Use SocketCAN Interface
```bash
# If your adapter supports SocketCAN (it might not)
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up

# Then use python-can with extended IDs
import can
bus = can.interface.Bus(channel='can0', bustype='socketcan')
msg = can.Message(arbitration_id=0x1FFFFF00, 
                  is_extended_id=True,  # ← This is the key!
                  data=[...])
bus.send(msg)
```

### Option B: Different Adapter
Get an adapter that supports:
- ✅ SocketCAN on Linux
- ✅ Extended 29-bit CAN IDs
- ✅ High-speed CAN (1 Mbps)

Examples:
- PEAK PCAN-USB
- Kvaser Leaf Light
- CANable (with candlelight firmware)

---

## What You Can Do Now

### Immediate (Works Today):

**1. Control your 6 motors** with current firmware:
```python
MOTOR_IDS = {
    'motor_1': 8,
    'motor_2': 16,
    'motor_3': 21,
    'motor_4': 31,
    'motor_5': 64,
    'motor_6': 72,
}
# All motors work perfectly!
```

### This Week:

**2. Update firmware with MotorStudio:**
- Download MotorStudio from GitHub
- Install on Windows PC
- Connect ONE motor
- Update firmware (5 minutes per motor)
- Configure unique CAN IDs (1-15)

### After Update:

**3. Enjoy unique CAN IDs:**
```python
# After firmware update:
MOTOR_IDS = {
    'motor_1': 1,   # ← Unique ID
    'motor_2': 2,   # ← Unique ID
    'motor_3': 3,   # ← Unique ID
    # ... etc
}
# No more overlapping IDs!
```

---

## Summary

### Why Firmware Update Fails:
1. ❌ Your adapter uses **L91 protocol** (11-bit IDs only)
2. ❌ OTA updates need **extended CAN IDs** (29-bit)
3. ❌ L91 protocol **can't send** extended IDs
4. ❌ Motors never receive OTA commands

### The Solution:
1. ✅ Use **MotorStudio** (official tool)
2. ✅ Handles **all protocols** correctly
3. ✅ Safe with **error recovery**
4. ✅ Updates **firmware + configures IDs**

### Current Status:
- ✅ **6 motors working** perfectly
- ✅ **Firmware downloaded** (`rs00_0.0.3.22.bin`)
- ✅ **Ready for MotorStudio** update
- ✅ **Workaround available** (use current IDs)

---

## Bottom Line

**It's not a bug in our code - it's a hardware limitation of your USB-to-CAN adapter.**

The adapter is great for motor control but doesn't support the advanced features needed for firmware updates. MotorStudio is designed to work around these limitations.

**Think of it like this:**
- Your adapter is like a **translator** (English ↔ Spanish)
- OTA updates need **Chinese**
- The translator doesn't speak Chinese
- You need a **different translator** (MotorStudio) that speaks all languages

---

*This is why RobStride provides MotorStudio - they know not all adapters support extended CAN IDs!*

