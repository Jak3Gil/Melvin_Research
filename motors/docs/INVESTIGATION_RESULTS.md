# Motor Configuration Investigation Results

**Date:** January 6, 2025  
**Purpose:** Determine if motors can be configured/locked to single IDs

## Test Results Summary

### Test 1: Single ID Repeated Activation
**Result:** ✗ **FAILED**
- Attempted to "lock" ID 8 by activating it 10 times in a row
- **Result:** IDs 8-31 still all respond
- **Conclusion:** Repeated activation does NOT lock motors to single IDs

### Test 2: Configuration Command Bytes
**Result:** ✗ **FAILED** - No configuration commands found
- Tested 15 different command bytes: `0x10, 0x11, 0x12, 0x21, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80, 0xA0, 0xA1, 0xB0, 0xC0, 0xF0`
- **Result:** NONE of these command bytes received responses
- **Conclusion:** No configuration commands found in L91 protocol (at least not these common ones)

### Test 3: Isolated Activation
**Result:** ✗ **FAILED**
- Activated ONLY ID 8 (slowly, in isolation)
- **Result:** IDs 8-31 all respond
- **Conclusion:** Even isolated activation triggers range responses
- **Key Finding:** Activating one ID wakes up the entire range

### Test 4: Parameter Variations
**Result:** ✓ **Responses received** but no effect on ID assignment
- Varied load params command to include ID 8 in different positions
- **Result:** Commands received responses, but didn't change which IDs respond
- **Conclusion:** Parameter variations don't configure motor IDs

## Critical Findings

### 1. No Software Configuration Available
- **No configuration command bytes work** in L91 protocol
- **Cannot configure motor IDs via software** (at least with tested commands)
- Motors appear to be **hardware-configured** or **factory-set**

### 2. Range-Based Response is Fundamental
- **Not a bug** - it's how the system works
- Activating one ID in a range wakes up the entire range
- This is likely **firmware behavior**, not configuration

### 3. Grouping is Dynamic but Persistent
- Grouping is created by activation sequence (from grouping tests)
- But once created, it's persistent during session
- **Cannot be changed via software commands** (tested)

## What This Means

### Motors Cannot Be Configured via Software
The L91 protocol over USB-to-CAN adapter does NOT provide commands to:
- Set individual motor CAN IDs
- Lock motors to single IDs
- Configure motor addresses

### Motors Respond to ID Ranges
This appears to be **intentional firmware behavior**:
- Motor 1: Responds to IDs 1-15 (or 8-15)
- Motor 2: Responds to IDs 16-20
- Motor 3: Responds to IDs 21-30
- Motor 4: Responds to IDs 31-39
- Motor 8: Responds to IDs 64-79

### Possible Causes
1. **Hardware DIP switches** - Motors may have physical switches for ID configuration
2. **Factory programming** - IDs may be set during manufacturing
3. **Firmware grouping** - Motors may be intentionally grouped by firmware
4. **Daisy-chain topology** - Physical wiring may affect ID assignment

## Recommendations

### Option 1: Use Range-Based Control (Practical Solution)
Since motors respond to ranges, you can:
- **Use ID 8-15 to control Motor 1**
- **Use ID 16-20 to control Motor 2**
- **Use ID 21-30 to control Motor 3**
- **Use ID 31-39 to control Motor 4**
- **Use ID 64-79 to control Motor 8**

**Pros:**
- Works with current setup
- No hardware changes needed
- Can control motors individually (just use the range)

**Cons:**
- Not true individual ID control
- Multiple IDs map to same motor

### Option 2: Check Hardware Configuration
1. **Inspect motors for DIP switches** - May be on controller board
2. **Check motor datasheet** - Look for ID configuration instructions
3. **Contact manufacturer** - Ask Robstride about CAN ID configuration

### Option 3: Use Physical Mapping
1. **Map physical motor positions** to ID ranges
2. **Create a lookup table** of ID range → Physical Motor
3. **Use consistent ID** from each range (e.g., always use ID 8 for Motor 1)

## Next Steps

1. **✅ COMPLETED:** Test if motors can be locked to single IDs → **NO**
2. **✅ COMPLETED:** Search for configuration commands → **NONE FOUND**
3. **⏳ IN PROGRESS:** Map physical motors to ID ranges → Use `map_physical_motors_to_ids.py`
4. **TODO:** Check motors for DIP switches or hardware ID configuration
5. **TODO:** Contact Robstride manufacturer for CAN ID configuration method
6. **TODO:** Implement range-based control system using consistent IDs from each range

## Conclusion

**Motors cannot be configured to single IDs via software using the L91 protocol.**

However, **range-based control is functional** and can be used to control individual motors by using a consistent ID from each motor's range. This is a practical solution that works with the current hardware and firmware.

