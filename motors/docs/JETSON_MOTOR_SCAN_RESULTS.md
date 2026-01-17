# Jetson Motor Scan Results
**Date:** January 6, 2025  
**Platform:** NVIDIA Jetson  
**USB-to-CAN Adapter:** `/dev/ttyUSB0` (QinHeng Electronics HL-340 / CH340)

## USB-to-CAN Adapter Detection

✅ **Found USB-to-CAN adapter:**
- Device: `/dev/ttyUSB0`
- Vendor: QinHeng Electronics
- Model: HL-340 USB-Serial adapter (CH340 chipset)
- Baud Rate: 921600 (verified working)
- Permission: User `melvin` has access (in dialout group)

## Motor Scan Results

### CAN IDs Responding
✅ **24 CAN IDs responding:**

**Motor 1 - CAN IDs 8-15 (8 IDs):**
- CAN ID 0x08 (8)
- CAN ID 0x09 (9)
- CAN ID 0x0A (10)
- CAN ID 0x0B (11)
- CAN ID 0x0C (12)
- CAN ID 0x0D (13)
- CAN ID 0x0E (14)
- CAN ID 0x0F (15)

**Motor 2 - CAN IDs 16-31 (16 IDs):**
- CAN ID 0x10 (16)
- CAN ID 0x11 (17)
- CAN ID 0x12 (18)
- CAN ID 0x13 (19)
- CAN ID 0x14 (20)
- CAN ID 0x15 (21)
- CAN ID 0x16 (22)
- CAN ID 0x17 (23)
- CAN ID 0x18 (24)
- CAN ID 0x19 (25)
- CAN ID 0x1A (26)
- CAN ID 0x1B (27)
- CAN ID 0x1C (28)
- CAN ID 0x1D (29)
- CAN ID 0x1E (30)
- CAN ID 0x1F (31)

❌ **CAN IDs NOT responding:**
- CAN IDs 0x01-0x07 (1-7) - No response

### Physical Motor Status (CONFIRMED)

✅ **2 physical motors found and mapped:**

**Motor 1:**
- Controlled by **ALL** CAN IDs 8-15 (all 8 IDs control the same physical motor)
- Recommended: Use CAN ID 8 (0x08) for Motor 1

**Motor 2:**
- Controlled by **ALL** CAN IDs 16-31 (all 16 IDs control the same physical motor)
- Recommended: Use CAN ID 16 (0x10) for Motor 2

**Status:**
- Only 2 physical motors are responding out of expected 15 motors
- Each motor responds to multiple CAN IDs (not properly configured with unique IDs)
- Motors need to be configured with unique CAN IDs for individual control

### Response Data

All motors return identical response data:
- **Activate response:** `41 54 00 00 0f f4 08 36 45 3b 4e 20 71 30 18 0d 0a`
- **Load params response:** `41 54 10 00 0f ec 08 00 c4 56 00 03 01 0b 07 0d 0a`

This identical response suggests:
1. Motors may be configured with the same CAN ID (broadcast mode)
2. Motors are not properly configured with unique IDs
3. Multiple motors respond to the same CAN messages

## Tools Available on Jetson

✅ **Python 3.8.10** installed  
✅ **pyserial** library installed  
✅ **Scanner script** transferred: `scan_robstride_motors.py`  
✅ **Mapping script** transferred: `map_can_ids_to_physical_motors.py`

## Next Steps

### 1. Motor Control Commands

**Control Motor 1:**
```bash
ssh melvin@192.168.1.119 "python3 scan_robstride_motors.py /dev/ttyUSB0 921600 --test 8"
```

**Control Motor 2:**
```bash
ssh melvin@192.168.1.119 "python3 scan_robstride_motors.py /dev/ttyUSB0 921600 --test 16"
```

### 2. Verify Motor Count
- Check if only 2 motors are actually connected/powered
- Verify all 15 motors are on the CAN bus
- Check CAN bus connections (CAN-H, CAN-L, GND)
- Verify termination resistors (120Ω at both ends)

### 3. Configure Motor CAN IDs
Motors need unique CAN IDs for individual control. Based on documentation:
- Motors likely need hardware configuration (DIP switches, jumpers)
- Or motor manufacturer's configuration software
- Software configuration via L91 protocol may not be supported

## Commands Reference

### Scan all motors:
```bash
ssh melvin@192.168.1.119 "python3 scan_robstride_motors.py /dev/ttyUSB0 921600 --scan-all"
```

### Test specific motor:
```bash
ssh melvin@192.168.1.119 "python3 scan_robstride_motors.py /dev/ttyUSB0 921600 --test 12"
```

### Map CAN IDs to physical motors:
```bash
ssh melvin@192.168.1.119 "python3 map_can_ids_to_physical_motors.py /dev/ttyUSB0 921600"
```

## Troubleshooting

### If no motors respond:
1. Check USB-to-CAN adapter is connected
2. Verify motors are powered on
3. Check CAN bus connections
4. Try different baud rate: `python3 scan_robstride_motors.py /dev/ttyUSB0 115200`

### If all CAN IDs control same motor:
- Motors are not configured with unique CAN IDs
- Need to configure each motor with a unique ID
- See `CONFIGURE_MOTOR_IDS.md` for configuration options

### If motors don't move during test:
- Check motor power supply
- Verify CAN bus termination
- Check motor controller status LEDs
- Verify motors are enabled/activated

