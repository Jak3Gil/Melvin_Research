# Motor Scan Results Summary

## Latest Comprehensive Scan Results

### Scan Details:
- **Date:** January 8, 2025
- **Range Tested:** IDs 0-255 (all 8-bit CAN IDs)
- **Protocol:** L91 over `/dev/ttyUSB0` @ 921600 baud
- **Method:** Rapid activation of all IDs, then testing responses

### Results:

**Found 48 Responding IDs in 2 Ranges:**

1. **Range 1:** IDs 8-39 (32 IDs)
   - 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39

2. **Range 2:** IDs 64-79 (16 IDs)
   - 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79

### Missing ID Ranges:
- **IDs 0-7:** No response
- **IDs 40-63:** No response
- **IDs 80-255:** No response (except 64-79)

### Comparison with Previous Findings:

#### Before Comprehensive Activation:
- Motor 1: IDs 1-15
- Motor 2: IDs 16-20
- Motor 3: IDs 21-30
- Motor 4: IDs 31-39
- Motor 8: IDs 64-79

#### After Comprehensive Activation:
- **Consolidated Range:** IDs 8-39 (combines Motors 1-4)
- **Same Range:** IDs 64-79 (Motor 8)

### Analysis:

**Key Finding:** Rapid activation of all IDs (0-255) caused motor grouping to consolidate:
- Previous 4 separate motor ranges (1-15, 16-20, 21-30, 31-39) → Merged into one large range (8-39)
- This confirms that activation sequence affects motor grouping

**Motor Count:**
- **Found:** 2 ID ranges responding
- **Expected:** 15 motors
- **Missing:** 13 motors (or missing ID ranges)

### Current Investigation:

**Deep Investigation Running:**
- Testing 7 different strategies to find missing motors
- Strategies include: selective gaps, reverse order, powers of 2, slow activation, different baud rates, broadcast commands, CAN interface setup
- Status: Running (started ~21:09)

### Next Steps:

1. ⏳ Wait for deep investigation to complete
2. Analyze results from all 7 strategies
3. Test direct CAN protocol (RobStride SDK)
4. Physical verification of motor connections
5. Try alternative protocols/command formats

## Files:

- **Scan Script:** `investigate_all_ids.py`
- **Deep Investigation:** `deep_investigation.py` (running)
- **Alternative Protocols:** `test_alternative_protocols.py`
- **Log Files:** `all_ids_l91.log`, `deep_investigation.log`

