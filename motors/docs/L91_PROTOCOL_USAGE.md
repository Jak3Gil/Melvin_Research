# Using L91 Protocol for All Motors

## Summary

We successfully use the existing L91 communication line to discover and control all motors on the Jetson via USB-to-CAN adapter.

## Current Status

✅ **L91 Protocol Working**
- Port: `/dev/ttyUSB0`
- Baud: `921600`
- Protocol: RobStride L91 (AT commands)

✅ **Motors Found**
- 2 physical motors discovered
- 64 total IDs responding
- Motor 1: Primary ID 40 (responds to IDs 40-63)
- Motor 2: Primary ID 80 (responds to IDs 80-119)

## How to Use

### 1. Discover All Motors

```bash
ssh melvin@192.168.1.119
python3 use_l91_for_all_motors.py
```

This will:
- Scan for all motors using L91 protocol
- Group motors by consecutive IDs
- Test each motor
- Save motor map to `motor_map_l91.txt`

### 2. Control Motors

Use the primary ID from each group to control motors:

- **Motor 1**: Use ID 40 (controls physical motor responding to IDs 40-63)
- **Motor 2**: Use ID 80 (controls physical motor responding to IDs 80-119)

Example scripts:
- `jetson_motor_interface.py` - Full motor control interface
- `test_single_motor.py` - Test individual motors
- `scan_all_motors_wide.py` - Scan for motors

## L91 Protocol Commands

### Activate Motor
```python
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
```

### Deactivate Motor
```python
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x00, 0x00, 0x0d, 0x0a])
```

### Load Parameters
```python
cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
             0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
```

### Move Jog
```python
# Speed in RPM (0.1 RPM = 1 count)
speed_val = int(speed * 10) & 0xFFFF
cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, motor_id, 0x08, 0x05, 0x70, 
                 0x00, 0x00, 0x07, flag])
cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
```

## Configuration

### Current Approach
- **Use motors as-is**: Each motor responds to a range of IDs
- **Use primary ID**: Control motors using the first ID in each group
- **No ID reconfiguration needed**: Works with current setup!

### Alternative: Motor Studio Configuration
If you need to reconfigure motor IDs:
1. Use Motor Studio on Windows PC
2. Connect USB-to-CAN adapter to Windows PC (COM port)
3. Follow Motor Studio instructions
4. Reconfigure IDs as needed
5. Move adapter back to Jetson if needed

**Note**: L91 protocol on Jetson works fine without reconfiguration!

## Files

- `use_l91_for_all_motors.py` - Discover and test all motors
- `jetson_motor_interface.py` - Full motor control interface
- `motor_map_l91.txt` - Motor mapping (on Jetson)
- `scan_all_motors_wide.py` - Comprehensive motor scanner

## Next Steps

1. ✅ **L91 Protocol Working** - Use existing communication line
2. ✅ **Motors Discovered** - Found 2 physical motors
3. ✅ **Control Working** - Can enable/disable/move motors
4. ⚠️ **More Motors?** - User mentioned 15 motors, found 2 groups
   - May need to power on/configure other motors
   - Or use Motor Studio to configure additional motors

## Reference

Motor Studio Instructions:
- PDF: https://gitee.com/robstride/MotorStudio/raw/main/使用说明书-Instructions/Instructions%20for%20using%20the%20Studio_241122.pdf
- Use for detailed configuration if needed

