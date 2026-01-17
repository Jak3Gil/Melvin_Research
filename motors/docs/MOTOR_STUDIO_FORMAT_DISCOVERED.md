# Motor Studio Command Format - Discovered

## Format Discovered

Motor Studio uses this command format:

### Initialization:
```
41542b41540d0a  = AT+AT + CRLF
```

### Motor Command Format:
```
41540007____01000d0a  = AT + 00 07 + [4 bytes CAN ID] + 01 00 + CRLF
```

Where `____` are 4 bytes that encode the motor's CAN ID.

## Known Example

**Motor 11:**
- Command: `41540007e89c010001000d0a`
- 4 bytes: `e8 9c 01 00`
- Decoded (little-endian): `0x00019CE8` = 105704 (decimal)

## What We Need

To find the pattern for calculating the 4 bytes for motors 1, 2, 4, 8, 9, we need to see what Motor Studio sends for other motors:

**Please check Motor Studio's debug/log window and provide:**
- Motor 5: What 4 bytes does it use?
- Motor 6: What 4 bytes does it use?
- Motor 7: What 4 bytes does it use?
- Motor 10: What 4 bytes does it use?
- Motor 12: What 4 bytes does it use?
- Motor 13: What 4 bytes does it use?
- Motor 14: What 4 bytes does it use?

Once we have 2-3 examples, we can figure out the pattern!

## Testing Script

Script created: `test_motor_studio_exact_format.py`

This script:
1. Sends `AT+AT` to initialize
2. Sends `AT + 00 07 + [4 bytes] + 01 00 + CRLF` format
3. Tests Motor 11's known format

## Next Steps

1. **Get more examples** from Motor Studio's log
2. **Find the pattern** in the 4-byte encoding
3. **Calculate 4 bytes** for motors 1, 2, 4, 8, 9
4. **Test those motors** with calculated values
5. **Configure all motors** to work with Motor Studio

## Current Status

✅ **Format discovered:** `AT + 00 07 + [4 bytes] + 01 00 + CRLF`
✅ **One example:** Motor 11 = `e8 9c 01 00`
⏳ **Need:** More examples to find pattern
⏳ **Goal:** Calculate 4 bytes for motors 1, 2, 4, 8, 9

