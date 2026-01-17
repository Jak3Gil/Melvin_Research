# Motor Discovery Status

## ✅ SUCCESS - Motors Responding!

We found the correct protocol! Using the RobStride USB-to-CAN adapter protocol from `l91_motor.cpp`.

## Current Status

### Found: 2 Physical Motors (out of 15)

**Motor 1:**
- Responds to CAN IDs: 8-39 (32 IDs)
- Location: Unknown
- Status: Misconfigured (should respond to only 1 ID)

**Motor 2:**
- Responds to CAN IDs: 64-79 (16 IDs)  
- Location: Unknown
- Status: Misconfigured (should respond to only 1 ID)

### Missing: 13 Motors

The other 13 motors are not responding. Possible reasons:
1. **Powered OFF** - Check power connections
2. **Different baud rate** - May be configured for 115200, 230400, or 460800
3. **Different CAN bus** - May be on a second USB-to-CAN adapter
4. **Not connected** - May be physically disconnected

## Next Steps

### Priority 1: Find All 15 Motors

1. **Check Power**
   - Verify all 15 motors have power LEDs ON
   - Check power supply voltage and current capacity

2. **Try Different Baud Rates**
   - Test 115200, 230400, 460800, 921600
   - Some motors may be at different baud rates

3. **Check for Multiple Adapters**
   - Look for /dev/ttyUSB1, /dev/ttyUSB2, etc.
   - Motors may be split across multiple CAN buses

4. **Physical Identification**
   - Power motors ON one at a time
   - Map which physical motor = which CAN ID range

### Priority 2: Reconfigure Motors to Unique IDs

Once all 15 motors are found, reconfigure them:
- Motor 1 → CAN ID 1
- Motor 2 → CAN ID 2
- ...
- Motor 15 → CAN ID 15

## Commands to Run

### 1. Check for additional USB devices:
```bash
ssh melvin@192.168.1.119 "ls -la /dev/ttyUSB*"
```

### 2. Test different baud rates:
```bash
ssh melvin@192.168.1.119 "python3 test_all_baud_rates.py"
```

### 3. Power cycle detection:
Power motors ON one at a time and run:
```bash
ssh melvin@192.168.1.119 "python3 find_motors_robstride_adapter.py"
```

## Technical Details

### Working Protocol
- **Adapter**: RobStride USB-to-CAN adapter
- **Port**: /dev/ttyUSB0
- **Baud**: 921600
- **Format**: `AT <cmd> 07 e8 <can_id> <data> 0d 0a`

### Activate Motor Command
```
41 54 00 07 e8 <CAN_ID> 01 00 0d 0a
```

### Motor Response Format
```
41 54 00 00 <id_high> f4 08 <data...> 0d 0a
```

## Problem: Multiple IDs per Motor

Each motor is responding to a **range of CAN IDs** instead of a single ID. This is likely due to:
- **Address masking** - Motors configured with wildcard/mask bits
- **Factory default** - Motors never configured with unique IDs
- **Broadcast mode** - Motors in a special discovery mode

**Solution**: Use the SET_CAN_ID command to assign unique IDs to each motor.

