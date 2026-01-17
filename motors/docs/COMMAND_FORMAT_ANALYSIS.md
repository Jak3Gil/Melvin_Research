# Command Format Analysis Results

**Date:** January 6, 2025  
**Test:** Verification of L91 protocol command format

## Key Finding: Address Bytes Don't Matter

**Test Results:**
- **13 different address combinations work** (0x07 0xE8, 0x00 0x00, 0x01 0x00, 0x7E 0x08, etc.)
- **All addresses produce the same motor responses**
- **Alternative formats without address bytes don't work**

## Conclusion

### What We Learned:

1. **Address bytes are required** - Commands without them don't work
2. **Address value doesn't matter** - Many different addresses work
3. **Address doesn't affect motors** - All addresses produce same motor responses
4. **Address is likely for adapter** - The USB-to-CAN adapter uses these bytes, not the motors

### What This Means:

The `0x07 0xE8` (or any working address) is likely:
- **Protocol identifier for the USB-to-CAN adapter**
- **Not used by the motors themselves**
- **Required by the adapter to convert serial AT commands to CAN frames**

The motors respond based on **CAN ID only**, not the address bytes.

## Command Format Confirmed

**Current format is correct:**
```
AT <cmd_byte> <addr_high> <addr_low> <can_id> <data> \r\n
```

Where:
- `AT` = 0x41 0x54 (command prefix)
- `<cmd_byte>` = Command type (0x00=activate, 0x20=load params, 0x90=move)
- `<addr_high> <addr_low>` = Address bytes (0x07 0xE8 or any working combination)
- `<can_id>` = Target motor CAN ID
- `<data>` = Command-specific data
- `\r\n` = 0x0D 0x0A (line terminator)

**The address bytes are a protocol requirement but don't affect motor targeting.**

## Why Motors Respond to Ranges

Since the address doesn't affect motors, the range-based response behavior is **NOT** due to the command format. It's likely due to:

1. **Motor firmware configuration** - Motors configured to respond to multiple IDs
2. **State-dependent behavior** - Activation sequence changes motor state
3. **Firmware grouping** - Motors grouped by physical position or configuration

## Next Steps

The command format is correct. The issue is **motor configuration**, not command format. We need to:
1. Find how to configure each motor with a unique CAN ID
2. Understand why the activation sequence changes motor behavior
3. Determine if this is normal operation or configuration mode

