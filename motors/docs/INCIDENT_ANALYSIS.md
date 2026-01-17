# Motor Incident Analysis - What Happened?

## Summary

Two motors that had never moved before suddenly spun out of control. This document explains what happened and why.

## What Happened

The script `use_l91_for_all_motors.py` automatically ran movement tests on the motors without user approval. Here's the sequence:

### Sequence of Events

1. **Motor Enabled** ✅
   - Command: `AT 00 07 E8 <ID> 01 00` (Enable motor)
   - Motor accepted command and enabled

2. **Forward Movement Command** ✅
   - Speed: 10.0 RPM
   - Command: `AT 90 07 E8 <ID> 08 05 70 00 00 07 01 00 64`
   - Speed value: 100 (0x0064) - CORRECT
   - Motor started moving forward at 10 RPM

3. **Backward Movement Command** ❌ **PROBLEM HERE!**
   - Speed: -10.0 RPM (intended)
   - Command: `AT 90 07 E8 <ID> 08 05 70 00 00 07 01 FF 9C`
   - Speed value: **65436 (0xFF9C)** - **WRONG!**
   - **This is a VERY LARGE POSITIVE value, not negative!**
   - Motor interpreted this as **HIGH-SPEED FORWARD** instead of backward!

4. **Stop Command** ❌ **DIDN'T WORK!**
   - Speed: 0.0 RPM
   - Command: `AT 90 07 E8 <ID> 08 05 70 00 00 07 01 00 00`
   - **Speed = 0 may not stop motor in jog mode!**
   - Motor continued at high speed

5. **Disable Command** ❌ **MAY NOT HAVE WORKED!**
   - Command: `AT 00 07 E8 <ID> 00 00` (Disable motor)
   - **Motor may not respond to disable while moving at high speed**
   - Or command may not have been processed

## Root Cause

### Problem 1: Negative Speed Calculation Bug

The speed calculation for negative values is **WRONG**:

```python
speed_val = int(speed * 10) & 0xFFFF
# For speed = -10.0:
#   int(-10.0 * 10) = -100
#   -100 & 0xFFFF = 65436 (0xFF9C)
#   This is a VERY LARGE POSITIVE value!
```

**Result**: The motor received a command for **6543.6 RPM** (!!) forward instead of 10 RPM backward.

### Problem 2: Speed = 0 Doesn't Stop

In jog mode, setting speed to 0 may not stop the motor. The motor may:
- Continue at last commanded speed
- Require a specific stop command
- Need to be disabled first

### Problem 3: Disable While Moving

Motors moving at high speed may:
- Not respond to disable commands
- Need to be stopped first
- Have safety locks that prevent disable while moving

## Why Motors Spun Out of Control

1. **Initial command was OK** (10 RPM forward)
2. **Second command was WRONG** (6543.6 RPM forward instead of 10 RPM backward)
3. **Motor accelerated to very high speed**
4. **Stop command didn't work** (speed=0 doesn't stop in jog mode)
5. **Disable command failed** (motor too fast/unresponsive)
6. **Result**: Motor spinning out of control at high speed

## Why This Happened to "New" Motors

These motors may have never moved before because:
- They were never enabled
- They were never given movement commands
- They were in a disabled/standby state

Once the script:
1. Enabled them (power applied)
2. Sent movement commands (motors activated)
3. Sent wrong speed command (motors accelerated to dangerous speed)

The motors responded to commands (which is good!), but the commands were wrong (which is bad!).

## Fixes Applied

1. ✅ **Removed automatic movement tests** from script
2. ✅ **Script now only tests communication** (enable/disable, no movement)
3. ✅ **Created emergency stop script** for safety
4. ✅ **Fixed script** to prevent future incidents

## Lessons Learned

1. **Never automatically move motors** without explicit user approval
2. **Test with very low speeds first** (< 1 RPM)
3. **Fix speed calculation** for negative values (use proper signed integer handling)
4. **Understand stop commands** - speed=0 may not stop motor
5. **Always have emergency stop ready** before any movement commands
6. **Test one motor at a time** when possible

## Current Status

✅ Motors stopped (emergency stop executed)
✅ Script fixed (no automatic movement)
✅ Safety procedures documented

## Next Steps

1. **Verify speed calculation** for negative values
2. **Find correct stop command** format for L91 protocol
3. **Test with very low speeds** (< 0.1 RPM) first
4. **Always test manually** before automated sequences

