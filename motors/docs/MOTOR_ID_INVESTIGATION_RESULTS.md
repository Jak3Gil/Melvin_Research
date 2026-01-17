# Motor ID Investigation Results - January 10, 2026

## Summary
**Date:** January 10, 2026  
**Platform:** NVIDIA Jetson (192.168.1.119)  
**USB-to-CAN Adapter:** `/dev/ttyUSB0` @ 921600 baud  
**Investigation Status:** ✅ BREAKTHROUGH - Found 4 distinct physical motors!

---

## Key Findings

### 🎯 **4 Physical Motors Identified**

Based on the unique response signatures, we have identified **4 distinct physical motors**:

#### **Motor Group 1: CAN IDs 8-15 (8 IDs)**
- **Response Signature:** `41 54 00 00 0f f4 08 36 45 3b 4e 20 71 30 18 0d 0a`
- **CAN IDs:** 8, 9, 10, 11, 12, 13, 14, 15
- **Status:** ✅ Responding
- **Recommended CAN ID:** Use **ID 8** for this motor

#### **Motor Group 2: CAN IDs 16-23 (8 IDs)**
- **Response Signature:** `41 54 00 00 17 f4 08 b0 46 30 02 14 33 b2 17 0d 0a`
- **CAN IDs:** 16, 17, 18, 19, 20, 21, 22, 23
- **Status:** ✅ Responding
- **Recommended CAN ID:** Use **ID 16** for this motor

#### **Motor Group 3: CAN IDs 24-31 (8 IDs)**
- **Response Signature:** `41 54 00 00 1f f4 08 40 64 3b 4e 20 71 30 18 0d 0a`
- **CAN IDs:** 24, 25, 26, 27, 28, 29, 30, 31
- **Status:** ✅ Responding
- **Recommended CAN ID:** Use **ID 24** for this motor

#### **Motor Group 4: CAN IDs 32-39 (8 IDs)**
- **Response Signature:** `41 54 00 00 27 f4 08 3b 44 30 02 14 33 b2 17 0d 0a`
- **CAN IDs:** 32, 33, 34, 35, 36, 37, 38, 39
- **Status:** ✅ Responding
- **Recommended CAN ID:** Use **ID 32** for this motor

---

## Response Analysis

### Pattern Discovered
Each physical motor responds to **8 consecutive CAN IDs**, and each group has a **unique response signature**. This indicates:

1. **Motors are NOT properly configured with unique IDs**
2. **Each motor accepts a range of 8 CAN IDs** (likely due to address masking or broadcast mode)
3. **We can distinguish motors by their response data** (different position/status values)

### Response Data Breakdown

The activate response format appears to be:
```
41 54 00 00 [ID] f4 08 [position/status data] 0d 0a
```

Key differences in responses:
- **Byte 4:** Changes with ID range (0x0f, 0x17, 0x1f, 0x27)
- **Bytes 7-13:** Unique motor position/status data

---

## Missing Motors

### Expected vs Found
- **Expected:** 15 motors
- **Found:** 4 physical motors responding
- **Missing:** 11 motors

### Possible Reasons
1. **Not powered on** - Check power connections to remaining motors
2. **Not on CAN bus** - Verify CAN-H, CAN-L, GND connections
3. **Different CAN ID ranges** - May respond to IDs > 39 (scan was interrupted at ID 44)
4. **Need activation** - May require special wake-up sequence
5. **Hardware issues** - Faulty motors or controllers

---

## Recommended Actions

### Immediate Next Steps

1. **Complete the extended scan (40-127)**
   ```bash
   ssh melvin@192.168.1.119 "python3 investigate_motor_ids_jetson.py"
   ```
   Let it run to completion to find remaining motors.

2. **Test physical motor movement**
   Run the physical mapping test to confirm which motors move for each group.

3. **Check motor power and connections**
   - Verify all 15 motors have power
   - Check CAN bus daisy-chain connections
   - Verify 120Ω termination resistors at both ends

### Motor Control Commands

To control the 4 identified motors individually:

```python
# Motor 1 - Use CAN ID 8
activate_motor(8)
move_motor(8, speed, direction)

# Motor 2 - Use CAN ID 16
activate_motor(16)
move_motor(16, speed, direction)

# Motor 3 - Use CAN ID 24
activate_motor(24)
move_motor(24, speed, direction)

# Motor 4 - Use CAN ID 32
activate_motor(32)
move_motor(32, speed, direction)
```

### Configuration Strategy

To give each motor a unique CAN ID:

**Option 1: Hardware Configuration**
- Check for DIP switches on motor controllers
- Look for jumpers that set CAN ID
- Consult motor documentation

**Option 2: Software Configuration (if supported)**
- Use manufacturer's configuration tool
- Send configuration commands via L91 protocol
- May need to isolate motors one at a time

**Option 3: Work with current setup**
- Use the lowest ID in each range (8, 16, 24, 32)
- Accept that each motor responds to 8 IDs
- Implement software layer to map logical IDs to physical motors

---

## Technical Details

### CAN IDs Not Responding
- **IDs 1-7:** No response (may be reserved or unused)
- **IDs 40+:** Scan interrupted, need to complete

### Response Consistency
All motors show consistent response patterns:
- **Activate response:** 17 bytes
- **LoadParams response:** 17 bytes
- **Format:** L91 protocol standard

### Serial Communication
- **Port:** `/dev/ttyUSB0`
- **Baud Rate:** 921600 (confirmed working)
- **Protocol:** L91 over USB-to-CAN adapter
- **Adapter:** QinHeng Electronics HL-340 (CH340 chipset)

---

## Next Investigation Tasks

1. ✅ **Scan IDs 1-39** - COMPLETED
2. ⏳ **Scan IDs 40-127** - INTERRUPTED (need to complete)
3. ⏳ **Physical motor mapping test** - Pending user input
4. ⏳ **Check power/connections** - Manual inspection needed
5. ⏳ **Find configuration method** - Documentation review needed

---

## Files Created

- `investigate_motor_ids_jetson.py` - Comprehensive scanning script
- `MOTOR_ID_INVESTIGATION_RESULTS.md` - This document

## Previous Documentation

- `MOTOR_STATUS.md` - Previous scan results (outdated)
- `JETSON_MOTOR_SCAN_RESULTS.md` - Earlier findings
- `MOTOR_DISCOVERY_BREAKTHROUGH.md` - Historical investigation

---

**Status:** Investigation in progress - 4 motors confirmed, 11 motors to locate

