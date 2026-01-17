# Confirmed Motor Mappings for Short Format

## Summary

When all 6 motors are connected, Motors 7, 9, and 11 use a **different response format** than Motors 1, 3, and 14.

## Confirmed Mappings

### Motor 7 ✓ CONFIRMED
- **Short Format Bytes**: `0x70` to `0x77` (any byte in this range works)
- **Command Format**: `AT 00 07 e8 [0x70-0x77] 01 00 0d 0a`
- **Response Format**: `4154000077f408bc7d30209c23370d0d0a`
  - Pattern: `4154000077f4...`
  - Contains Motor 11 encoding (`9c`) in data
- **Long Format**: `0x3c` does NOT work when all motors connected (no response)

### Motor 9 ✓ CONFIRMED
- **Short Format Bytes**: `0x58` to `0x5f` (any byte in this range works)
- **Command Format**: `AT 00 07 e8 [0x58-0x5f] 01 00 0d 0a`
- **Response Format**: `415400005ff4084e4330209c23370d0d0a`
  - Pattern: `415400005ff4...`
  - Contains Motor 11 encoding (`9c`) in data
- **Long Format**: `0x4c` does NOT work when all motors connected (no response)

### Motor 11 ⚠️ PARTIAL
- **Short Format Byte**: `0x9c` (known to work individually)
- **Command Format**: `AT 00 07 e8 9c 01 00 0d 0a`
- **Status**: Does NOT respond when all motors connected with this format
- **Observation**: Motor 11's encoding (`9c`) appears in responses from Motors 7 and 9, suggesting it may be included in their responses or requires different timing/sequence

## Response Format Comparison

### Standard Format (Motors 1, 3, 14)
- **Pattern**: `41541000XXec...`
- **Example Motor 1**: `415410000fec0800c4560003010b070d0a`
- **Example Motor 3**: `415410001fec0800c4560003010b070d0a`
- **Example Motor 14**: `4154100077ec0800c45600020309070d0a`
- **Works**: Yes, reliable responses

### New Format (Motors 7, 9, 11)
- **Pattern**: `41540000XXXX...`
- **Example Motor 7**: `4154000077f408bc7d30209c23370d0d0a`
- **Example Motor 9**: `415400005ff4084e4330209c23370d0d0a`
- **Works**: Yes for Motors 7 and 9, but different format than expected

## Key Findings

1. **Motor 7** responds reliably with bytes `0x70-0x77` in short format
2. **Motor 9** responds reliably with bytes `0x58-0x5f` in short format
3. **Motor 11** does not respond with byte `0x9c` when all motors connected, but its encoding appears in Motor 7 and 9 responses
4. **Long format** commands (`0x3c` for Motor 7, `0x4c` for Motor 9) do NOT work when all motors are connected
5. All responses contain Motor 11's encoding (`9c`) in their data, suggesting Motor 11 information may be embedded in other motor responses

## Recommendations

To detect all 6 motors when connected:
1. Use **short format** for Motors 7, 9, 11
2. Use **long format** for Motors 1, 3, 14
3. Parse both response formats:
   - `41541000XXec...` for Motors 1, 3, 14
   - `4154000077f4...` for Motor 7
   - `415400005ff4...` for Motor 9
   - Motor 11 may require alternative detection (presence in other responses or different query method)

## Test Commands

```python
# Motor 7
ser.write(bytes.fromhex("41540007e87001000d0a"))  # or 0x71-0x77

# Motor 9  
ser.write(bytes.fromhex("41540007e85801000d0a"))  # or 0x59-0x5f

# Motor 11
ser.write(bytes.fromhex("41540007e89c01000d0a"))  # Works individually, not when all connected
```

