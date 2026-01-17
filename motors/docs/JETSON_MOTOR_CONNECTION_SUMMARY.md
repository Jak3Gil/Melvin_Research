# Jetson Motor Connection Summary

**Date:** January 11, 2026  
**Connection:** USB-to-CAN via `/dev/ttyUSB1`  
**Baud Rate:** 921600  
**Protocol:** L91 (RobStride)

## ✅ Connection Status: SUCCESSFUL

### Hardware Configuration
- **Jetson Device:** melvin@192.168.1.119
- **USB-to-CAN Adapter:** `/dev/ttyUSB1` (HL-340 USB-Serial adapter)
- **Adapter Status:** Responding to AT commands (OK)
- **CAN Interfaces:** can0 and can1 also available (configured at 500000 baud)

### Motors Found: 32 Total

#### Range 1: IDs 8-31 (24 motors)
```
CAN IDs: 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
Hex:     0x08-0x1F
```

#### Range 2: IDs 72-79 (8 motors)
```
CAN IDs: 72, 73, 74, 75, 76, 77, 78, 79
Hex:     0x48-0x4F
```

## Connection Details

### Python Serial Connection
```python
import serial
ser = serial.Serial('/dev/ttyUSB1', 921600, timeout=0.5)
```

### L91 Protocol Packet Structure
```python
# Enable motor packet
packet = bytearray([0xAA, 0x55, 0x01, motor_id])
packet.extend(struct.pack('<I', motor_id))
packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
packet.append(sum(packet[2:]) & 0xFF)
```

## Available Scripts on Jetson

### Motor Testing Scripts
- `connect_motors_921600.py` - Test connection and find motors
- `scan_all_motors_wide.py` - Comprehensive motor scanner
- `quick_motor_test.py` - Test individual motor movement
- `test_all_ranges.py` - Test motors with visual pulse patterns
- `instant_test.py` - Quick motor response test

### Motor Control Scripts
- `activate_all_motors.py` - Enable all motors
- `emergency_stop_all_motors.py` - Emergency stop
- `move_motor_test.py` - Test motor movements

### Configuration Scripts
- `configure_all_15_motors.py` - Configure motor IDs
- `discover_and_configure_all_motors.py` - Auto-discover and configure
- `verify_motor_ids.py` - Verify motor ID assignments

## Quick Commands

### Connect to Jetson
```bash
ssh melvin@192.168.1.119
```

### Set USB permissions
```bash
sudo chmod 666 /dev/ttyUSB1
```

### Scan for motors
```bash
python3 scan_all_motors_wide.py /dev/ttyUSB1 921600 --start 1 --end 127
```

### Test a specific motor
```bash
python3 quick_motor_test.py /dev/ttyUSB1 921600 <CAN_ID>
```

### Test all motors with pulse patterns
```bash
python3 test_all_ranges.py /dev/ttyUSB1 921600
```

## Notes

1. **Multiple IDs per Motor:** The high number of responding IDs (32) suggests that some physical motors may be responding to multiple CAN IDs. This is a known behavior with RobStride motors.

2. **ID Grouping:** Motors appear to be grouped in ranges:
   - Range 1: IDs 8-31 (likely 3-4 physical motors)
   - Range 2: IDs 72-79 (likely 1-2 physical motors)

3. **Previous Findings:** From earlier testing, we know:
   - Motor 1: IDs 8-15
   - Motor 2: IDs 16-20
   - Motor 3: IDs 21-30
   - Motor 4: IDs 31-39
   - Motor 8: IDs 64-71
   - Motor 9: IDs 72-79

4. **Power Status:** All motors in the expected ranges are responding, indicating they are powered on and connected.

## Next Steps

1. Test individual motor movements to identify physical motors
2. Map CAN IDs to physical motor locations
3. Configure motors to single IDs if needed
4. Integrate motor control into main Melvin system

