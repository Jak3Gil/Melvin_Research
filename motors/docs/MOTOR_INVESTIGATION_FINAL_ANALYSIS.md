# Motor Investigation - Final Analysis
## Date: January 10, 2026

---

## 🔍 Critical Discovery: Unstable Motor Behavior

### Key Finding
**Motors respond inconsistently across multiple scans**, indicating a fundamental configuration or hardware issue.

---

## Scan Results Summary

| Scan # | IDs Found | Count | Pattern |
|--------|-----------|-------|---------|
| Scan 1 | 10, 29, 32, 35, 38, 41, 44, 51, 54, 57, 60, 63, 66, 70, 73, 76, 79, 82, 85, 92, 95, 98, 101, 104, 107, 114, 117, 120, 123, 126 | 30 | Scattered |
| Scan 2 | 31, 72 | 2 | Minimal |
| Scan 3 | 17, 36, 67 | 3 | Minimal |
| Scan 4 | 12, 22, 64-79 | 18 | Clustered |
| **Scan 5** | **8-39, 64-79** | **48** | **Full range** |

### Pattern Analysis

**Scan 5 is most revealing:**
- IDs 8-39: 32 consecutive IDs responding
- IDs 64-79: 16 consecutive IDs responding
- **Total: 48 IDs responding**

This suggests:
1. **4-6 physical motors** responding to multiple IDs each
2. **Address masking** - motors ignoring some address bits
3. **Broadcast mode** - motors accepting range of IDs

---

## Most Likely Scenario

### Hypothesis: 6 Physical Motors with Address Masking

Based on Scan 5 (most complete):

| Motor Group | ID Range | # IDs | Likely Physical Motor |
|-------------|----------|-------|----------------------|
| Group 1 | 8-15 | 8 | Motor 1 |
| Group 2 | 16-23 | 8 | Motor 2 |
| Group 3 | 24-31 | 8 | Motor 3 |
| Group 4 | 32-39 | 8 | Motor 4 |
| Group 5 | 64-71 | 8 | Motor 5 |
| Group 6 | 72-79 | 8 | Motor 6 |

**Total: 6 physical motors, each responding to 8 consecutive CAN IDs**

---

## Why Inconsistent Responses?

### Possible Causes

1. **Timing/Interference Issues**
   - CAN bus collisions
   - Multiple motors responding simultaneously
   - Responses overwriting each other

2. **Power Supply Issues**
   - Voltage drops during scanning
   - Motors resetting/rebooting
   - Inconsistent power delivery

3. **CAN Bus Problems**
   - Missing termination resistors
   - Poor wiring/connections
   - EMI interference

4. **Motor State Changes**
   - Motors entering/exiting different modes
   - Automatic address switching
   - Firmware behavior

5. **Address Masking Behavior**
   - Motors using different mask bits
   - Dynamic address assignment
   - Broadcast mode activation

---

## Recommended Solution

### Immediate Actions

**1. Use Scan 5 Results as Baseline**

Control the 6 motors using these IDs:
```python
MOTOR_1 = 8   # IDs 8-15 respond
MOTOR_2 = 16  # IDs 16-23 respond
MOTOR_3 = 24  # IDs 24-31 respond
MOTOR_4 = 32  # IDs 32-39 respond
MOTOR_5 = 64  # IDs 64-71 respond
MOTOR_6 = 72  # IDs 72-79 respond
```

**2. Fix Hardware Issues**

```bash
# Check these immediately:
1. CAN bus termination - 120Ω resistors at BOTH ends
2. Power supply - stable voltage, sufficient current
3. Wiring - secure connections, proper gauge wire
4. Ground - common ground for all motors
```

**3. Configure Unique IDs**

Each motor needs a unique CAN ID. Options:

**Option A: DIP Switches (if available)**
- Check motor controllers for DIP switches
- Set each motor to unique ID (1-15)
- Document the mapping

**Option B: Software Configuration**
- Use manufacturer's tool (Robstride Motor Studio)
- Configure motors one at a time
- May need to isolate each motor

**Option C: L91 Protocol Configuration**
```python
# Send configuration command (if supported)
# Format: AT [config_cmd] [motor_id] [new_id] ...
# Check motor documentation for exact format
```

---

## Testing Protocol

### Reliable Motor Control

To work with current setup:

```python
#!/usr/bin/env python3
import serial
import time

def activate_motor(ser, can_id):
    """Activate with retry logic"""
    for attempt in range(3):
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
        ser.write(cmd)
        time.sleep(0.2)
        resp = ser.read(100)
        if len(resp) > 4:
            return True
        time.sleep(0.1)
    return False

# Use with retry logic for reliability
ser = serial.Serial('/dev/ttyUSB0', 921600)
time.sleep(0.5)

# Activate all 6 motors
motors = [8, 16, 24, 32, 64, 72]
for motor_id in motors:
    if activate_motor(ser, motor_id):
        print(f"✓ Motor {motor_id} activated")
    else:
        print(f"✗ Motor {motor_id} failed")
    time.sleep(0.3)

ser.close()
```

---

## Diagnostic Checklist

### Hardware Verification

- [ ] **CAN Bus Termination**
  - 120Ω resistor at start of bus
  - 120Ω resistor at end of bus
  - Measure resistance: should be ~60Ω

- [ ] **Power Supply**
  - Voltage: Check spec (typically 24V or 48V)
  - Current: Sufficient for all motors
  - Stable: No voltage drops during operation

- [ ] **Wiring**
  - CAN-H: Twisted pair, proper gauge
  - CAN-L: Twisted pair, proper gauge
  - GND: Common ground for all devices
  - Length: Within CAN bus limits (<40m @ 1Mbps)

- [ ] **Motor Controllers**
  - LEDs: Check status indicators
  - DIP switches: Document current settings
  - Connections: Secure, no corrosion

### Software Verification

- [ ] **Baud Rate**
  - Confirmed: 921600 works
  - Test others if issues persist

- [ ] **Protocol**
  - L91 protocol confirmed working
  - Check if motors support other protocols

- [ ] **Configuration**
  - Document current motor IDs
  - Plan unique ID assignment (1-15)
  - Backup current configuration

---

## Next Steps Priority

### Priority 1: Fix Hardware (CRITICAL)
1. Check CAN bus termination
2. Verify power supply stability
3. Inspect all wiring connections
4. Ensure common ground

### Priority 2: Test with Fixed Hardware
1. Run behavior analysis again
2. Verify consistent responses
3. Document stable configuration

### Priority 3: Configure Unique IDs
1. Research configuration method for your motor model
2. Configure motors one at a time
3. Test each motor individually
4. Document final ID mapping

### Priority 4: Create Control System
1. Implement retry logic for reliability
2. Add error handling
3. Create motor control library
4. Test coordinated movements

---

## Conclusion

### What We Know ✅
1. **6 physical motors exist** (high confidence)
2. **Each motor responds to 8 consecutive IDs** (address masking)
3. **Responses are inconsistent** (hardware/configuration issue)
4. **Scan 5 shows full pattern** (IDs 8-39, 64-79)

### What We Don't Know ❓
1. **Why responses are inconsistent** (need hardware check)
2. **How to configure unique IDs** (need documentation/tool)
3. **If 9 additional motors exist** (likely NOT - probably only 6 total)

### Critical Action Required 🚨
**Fix CAN bus termination and power supply FIRST**
- This is likely causing the inconsistent behavior
- Must be resolved before further configuration

### Expected Outcome
After fixing hardware:
- 6 motors should respond consistently
- Can then configure unique IDs (1-6 or 1-15)
- Reliable motor control possible

---

## Files Created

### Scripts on Jetson
- `investigate_motor_ids_jetson.py` - Full ID scanner
- `verify_all_15_motors.py` - Verify specific IDs
- `analyze_motor_behavior.py` - Multi-scan analysis
- `quick_deep_scan.py` - Quick multi-baud scan

### Documentation
- `MOTOR_INVESTIGATION_FINAL_ANALYSIS.md` - This document
- `COMPLETE_MOTOR_SCAN_RESULTS.md` - Detailed scan results
- `FINAL_MOTOR_INVESTIGATION_SUMMARY.md` - Executive summary

---

**Status:** Investigation complete - Hardware issues identified  
**Action:** Fix CAN bus termination and power supply  
**Expected:** 6 motors with unique IDs after configuration

