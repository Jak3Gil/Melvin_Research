# Motor Discovery Findings
**Date:** January 10, 2026  
**Platform:** NVIDIA Jetson (melvin@192.168.1.119)  
**Device:** /dev/ttyUSB0 (921600 baud)

## Summary

**48 CAN IDs responding** across two ranges, but they control **fewer physical motors** (likely 6-15 motors).

## Discovered CAN ID Ranges

### Range 1: IDs 8-39 (32 IDs)
- **IDs 8-15** (8 IDs)
- **IDs 16-20** (5 IDs)  
- **IDs 21-30** (10 IDs) ← **Motor 3** (per user)
- **IDs 31-39** (9 IDs)

### Range 2: IDs 64-79 (16 IDs)
- **IDs 64-71** (8 IDs) ← **Motor 8 at ID 64** (per user)
- **IDs 72-79** (8 IDs) ← **Motor 9 at ID 73** (per user)

## The Problem

**Multiple CAN IDs control the same physical motor.**

### Known Mappings (from user):
- **Motor 3**: Responds to IDs 21-30 (10 IDs for 1 motor)
- **Motor 8**: Responds to ID 64 (and likely 64-71)
- **Motor 9**: Responds to ID 73 (and likely 72-79)

### Pattern Analysis:
Looking at the ranges, it appears each motor responds to **8-10 consecutive CAN IDs**:
- Motor 1: IDs 8-15 (8 IDs)
- Motor 2: IDs 16-23 (8 IDs)
- Motor 3: IDs 21-30 (10 IDs) ← **OVERLAPS with Motor 2!**
- Motor 4: IDs 32-39 (8 IDs)
- Motor 8: IDs 64-71 (8 IDs)
- Motor 9: IDs 72-79 (8 IDs)

## Why This Happens

### Root Cause: Motors Not Configured with Unique IDs

Motors are likely:
1. **At factory default settings** - Each motor responds to a range of IDs
2. **Not individually configured** - No unique CAN ID assigned per motor
3. **Using broadcast/group addressing** - Responding to ID ranges instead of single IDs

### Why We Can't Find All Motors

If you have 15 motors total, but only see responses from 6 ranges:
- **9 motors may be:**
  - Not powered on
  - Not connected to CAN bus
  - At different ID ranges we haven't scanned yet
  - Using different base addresses (not 0x07e8)
  - In sleep/disabled state

## Next Steps

### 1. Identify Physical Motor Mapping

Run the identification script to map which IDs control which motors:

```bash
ssh melvin@192.168.1.119
python3 identify_physical_motors.py /dev/ttyUSB0 921600
```

This will test each ID range and ask you to identify which physical motor moved.

### 2. Check for More Motors

**Possible reasons for missing motors:**

#### A. Different base address
Current scans use base address `0x07e8`. Try other addresses:
- `0x07e0` - `0x07ef` (common CAN addresses)

#### B. Higher ID ranges
Scan IDs 80-255:
```bash
python3 scan_all_motors_wide.py /dev/ttyUSB0 921600 --start 80 --end 255
```

#### C. Motors not powered/connected
- Check power connections to all motors
- Verify CAN bus wiring (CAN-H, CAN-L, GND)
- Check for termination resistors on CAN bus

#### D. Motors in sleep mode
Some motors need activation before responding. Try:
- Power cycle all motors
- Send broadcast activation commands
- Check motor documentation for wake-up procedure

### 3. Configure Unique CAN IDs

Once all motors are found, configure each with a unique ID:
- Use manufacturer software (Robstride Motor Studio)
- Or use configuration commands (if supported)
- Or configure via hardware (DIP switches/jumpers)

## Expected Motor Configuration

For 15 motors, ideal configuration:
- **Motor 1** → CAN ID 1
- **Motor 2** → CAN ID 2
- **Motor 3** → CAN ID 3
- ...
- **Motor 15** → CAN ID 15

Each motor should respond to **only ONE** CAN ID.

## Current Status

✅ **Connected to Jetson**  
✅ **USB-to-CAN working** (/dev/ttyUSB0)  
✅ **48 CAN IDs responding**  
⚠️  **Multiple IDs per motor** (not configured)  
❓ **Unknown number of physical motors** (need to test)  
❓ **Missing motors** (9+ motors not found)

## Scripts Available

1. `scan_all_motors_wide.py` - Comprehensive scan (IDs 1-127)
2. `identify_physical_motors.py` - Map IDs to physical motors
3. `verify_motor_mapping.py` - Verify which IDs control same motor
4. `scan_robstride_motors.py` - Original scanner (limited range)

## Questions to Answer

1. **How many physical motors are actually connected?**
   - Run `identify_physical_motors.py` to find out

2. **Where are the missing motors?**
   - Check power/connections
   - Scan higher ID ranges
   - Try different base addresses

3. **Why do motors respond to multiple IDs?**
   - Motors not configured with unique IDs
   - Need manufacturer software or config commands

4. **How to fix the ID mapping?**
   - Configure each motor individually with unique ID
   - May require disconnecting motors one at a time

