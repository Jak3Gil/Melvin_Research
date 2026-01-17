# Motor CAN ID Mapping Summary
**Last Updated:** January 6, 2025  
**Platform:** NVIDIA Jetson  
**USB-to-CAN:** `/dev/ttyUSB0` (CH340, 921600 baud)

## Motor Mapping (CONFIRMED)

### Motor 1
- **CAN IDs:** 8-15 (0x08-0x0F)
- **Total IDs:** 8
- **Recommended ID:** 8 (0x08)
- **Status:** ✅ Responding

### Motor 2
- **CAN IDs:** 16-31 (0x10-0x1F)
- **Total IDs:** 16
- **Recommended ID:** 16 (0x10)
- **Status:** ✅ Responding

## Important Notes

⚠️ **All CAN IDs in each range control the same physical motor.**
- Motor 1 responds to ANY CAN ID from 8-15
- Motor 2 responds to ANY CAN ID from 16-31
- This means motors are NOT configured with unique CAN IDs

## Quick Control Commands

### Test Motor 1 (CAN ID 8):
```bash
ssh melvin@192.168.1.119 "python3 scan_robstride_motors.py /dev/ttyUSB0 921600 --test 8"
```

### Test Motor 2 (CAN ID 16):
```bash
ssh melvin@192.168.1.119 "python3 scan_robstride_motors.py /dev/ttyUSB0 921600 --test 16"
```

### Scan All Motors:
```bash
ssh melvin@192.168.1.119 "python3 scan_robstride_motors.py /dev/ttyUSB0 921600 --scan-all"
```

## Current Status

- **Motors Found:** 2 out of expected 15
- **CAN IDs Responding:** 24 total (8 for Motor 1, 16 for Motor 2)
- **CAN IDs Not Responding:** 1-7 (0x01-0x07)

## Next Steps

To enable individual control of all motors:
1. Configure each motor with a unique CAN ID
2. Check motor documentation for CAN ID configuration method
3. May require hardware configuration (DIP switches/jumpers) or manufacturer software

