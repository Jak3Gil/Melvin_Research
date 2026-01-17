# Motor CAN ID Mapping Progress

**Date:** January 6, 2025  
**Method:** Rapid activation sequence (activate all IDs, load params, then test)

## Discovered Motor Mappings

### Motor 1
- **CAN IDs:** 1-15
- **Total IDs:** 15
- **Status:** ✅ Confirmed

### Motor 2
- **CAN IDs:** 16-20
- **Total IDs:** 5
- **Status:** ✅ Confirmed

### Motor 3
- **CAN IDs:** 21-30
- **Total IDs:** 10
- **Status:** ✅ Confirmed

### Motor 4
- **CAN IDs:** 31-39
- **Total IDs:** 9
- **Status:** ✅ Confirmed

## Remaining Motors to Find

**Motors Found:** 4 of 15  
**Motors Remaining:** 11 (Motors 5-15)

**Next Range to Test:** IDs 40+

## Key Discovery

The **rapid activation sequence** changes motor behavior:
1. Rapidly activate ALL IDs in a range (0.05s delays)
2. Load params on ALL IDs
3. Motors then respond to specific ID ranges

This sequence appears to "wake up" or configure motors to respond to different ID ranges.

## Activation Sequence That Works

```python
# Step 1: Rapidly activate all IDs
for can_id in range(start, end + 1):
    send_activate_command(can_id)
    time.sleep(0.05)

# Step 2: Load params on all IDs
for can_id in range(start, end + 1):
    send_load_params_command(can_id)
    time.sleep(0.05)

# Step 3: Test each ID individually
for can_id in range(start, end + 1):
    test_motor_movement(can_id)
```

## Next Steps

1. Continue testing higher ID ranges (40+, 100+, etc.)
2. Apply activation sequence to each new range
3. Map which physical motor responds to which ID ranges
4. Continue until all 15 motors are found

