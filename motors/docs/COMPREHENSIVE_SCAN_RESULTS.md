# Comprehensive CAN ID Scan Results

**Date:** January 8, 2025  
**Scan Range:** IDs 0-255 (all 8-bit CAN IDs)  
**Protocol:** L91 over `/dev/ttyUSB0` @ 921600 baud

## Scan Results

### Responding ID Ranges:
1. **Range 1:** IDs 8-39 (32 IDs)
2. **Range 2:** IDs 64-79 (16 IDs)

**Total:** 48 IDs responding across 2 ranges

## Comparison with Previous Findings

### Previous Motor Mapping (before comprehensive scan):
- Motor 1: IDs 1-15
- Motor 2: IDs 16-20
- Motor 3: IDs 21-30
- Motor 4: IDs 31-39
- Motor 8: IDs 64-79

### Current Scan Results:
- **Range 1:** IDs 8-39 (combines previous Motors 1-4 ranges)
- **Range 2:** IDs 64-79 (same as Motor 8)

## Analysis

### What Changed:
After comprehensive rapid activation (all IDs 0-255):
- Previous separate motor ranges (1, 2, 3, 4) are now consolidated into one large range (8-39)
- Motor 8 range (64-79) remains the same
- Lower IDs (0-7) and middle IDs (40-63, 80-255) do NOT respond

### Implications:
1. **Range-based response is confirmed** - Motors respond to ranges, not individual IDs
2. **Activation sequence affects grouping** - Rapid activation of all IDs changed the grouping
3. **Only 2 motor groups active** - Despite 15 motors expected, only 2 ID ranges respond
4. **Missing motors** - 13 motors are not responding at all

## Possible Explanations

### Theory 1: Motors Are Grouped by Physical Connection
- Motors may be wired in groups
- Only 2 physical groups are active/responding
- Other 13 motors might be:
  - Not powered
  - Not connected
  - On different CAN segment
  - Require different initialization

### Theory 2: Protocol/Interface Issue
- L91 protocol might only work for 2 motor groups
- Missing motors might require:
  - Direct CAN protocol (not L91)
  - Different CAN interface
  - Different initialization sequence

### Theory 3: Hardware Configuration
- Motors might need hardware configuration (DIP switches)
- Missing motors might be configured for different IDs
- Missing motors might be in sleep/disabled state

## Next Steps

### 1. Physical Verification
- Verify all 15 motors are powered and connected
- Check CAN bus wiring for all motors
- Verify CAN bus termination resistors

### 2. Try Direct CAN Protocol
Since L91 found only 2 ranges, try:
```bash
# Setup CAN interface
sudo slcand -o -c -s8 -S 1000000 /dev/ttyUSB0 slcan0
sudo ip link set slcan0 up type can bitrate 1000000

# Use RobStride SDK to scan
python3 scan_with_robstride_sdk.py slcan0
```

### 3. Test Individual Motor Activation
Try activating motors one at a time, in different orders:
- Activate IDs 0-7 first
- Activate IDs 40-63
- Activate IDs 80-255
- See if different activation sequences reveal more motors

### 4. Check Motor Hardware
- Look for DIP switches on motor controllers
- Check motor documentation for ID configuration
- Verify motor firmware versions

### 5. Monitor CAN Bus Directly
```bash
# Monitor raw CAN traffic
candump slcan0 -L

# Send test frames to missing ID ranges
cansend slcan0 001#0000000000000000  # Test ID 0
cansend slcan0 040#0000000000000000  # Test ID 40
```

## Summary

✅ **Found:** 2 ID ranges (8-39, 64-79) with 48 responding IDs  
❌ **Missing:** 13 motors (if each range represents one motor group)  
⚠️ **Issue:** Range-based response suggests motors are grouped, not individually accessible via current method

## Recommendations

1. **Continue using L91 for working motors** - IDs 8-39 and 64-79 work
2. **Investigate missing motors** - Check power, connections, configuration
3. **Try direct CAN protocol** - May reveal additional motors
4. **Physical inspection** - Verify all 15 motors are actually connected and powered

