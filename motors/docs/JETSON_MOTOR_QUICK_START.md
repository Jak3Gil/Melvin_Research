# Jetson Motor Control - Quick Start Guide

## ✅ Connection Established!

**Status:** Successfully connected to 32 motors via USB-to-CAN at 921600 baud

### Hardware Setup
- **Jetson:** melvin@192.168.1.119
- **Port:** `/dev/ttyUSB1`
- **Baud Rate:** 921600
- **Protocol:** L91 (RobStride AT commands)

## Motors Found

### Range 1: IDs 8-31 (24 motors)
```
8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
```

### Range 2: IDs 72-79 (8 motors)
```
72, 73, 74, 75, 76, 77, 78, 79
```

## Quick Start - Python Interface

### 1. Basic Usage

```python
from jetson_motor_interface import JetsonMotorController

# Create controller
controller = JetsonMotorController()

# Connect
controller.connect()

# Scan for motors
motors = controller.scan_motors(start_id=1, end_id=127)
print(f"Found {len(motors)} motors: {motors}")

# Test a motor
controller.pulse_motor(21, pulses=3)

# Disconnect
controller.disconnect()
```

### 2. Context Manager (Recommended)

```python
from jetson_motor_interface import JetsonMotorController

with JetsonMotorController() as controller:
    # Scan for motors
    motors = controller.scan_motors()
    
    # Test first motor
    if motors:
        controller.pulse_motor(motors[0], pulses=3)
```

### 3. Manual Motor Control

```python
from jetson_motor_interface import JetsonMotorController

controller = JetsonMotorController()
controller.connect()

motor_id = 21

# Enable motor
controller.enable_motor(motor_id)
controller.load_params(motor_id)

# Move motor
controller.move_motor(motor_id, speed=0.08, flag=1)
time.sleep(0.5)

# Stop motor
controller.move_motor(motor_id, speed=0.0, flag=0)

# Disable motor
controller.disable_motor(motor_id)

controller.disconnect()
```

### 4. Emergency Stop

```python
controller = JetsonMotorController()
controller.connect()

# Stop all motors immediately
controller.emergency_stop_all()

controller.disconnect()
```

## Command Line Usage

### Connect to Jetson
```bash
ssh melvin@192.168.1.119
```

### Run the demo interface
```bash
python3 jetson_motor_interface.py
```

### Scan for motors
```bash
python3 scan_all_motors_wide.py /dev/ttyUSB1 921600 --start 1 --end 127
```

### Test a specific motor
```bash
python3 quick_motor_test.py /dev/ttyUSB1 921600 21
```

### Test all motor ranges
```bash
python3 test_all_ranges.py /dev/ttyUSB1 921600
```

## Available Methods

### JetsonMotorController Methods

| Method | Description |
|--------|-------------|
| `connect()` | Connect to USB-to-CAN adapter |
| `disconnect()` | Close connection |
| `scan_motors(start_id, end_id)` | Scan for motors in ID range |
| `enable_motor(motor_id)` | Enable a motor |
| `disable_motor(motor_id)` | Disable a motor |
| `load_params(motor_id)` | Load motor parameters |
| `move_motor(motor_id, speed, flag)` | Move motor with jog command |
| `pulse_motor(motor_id, pulses, duration)` | Pulse motor for identification |
| `emergency_stop_all()` | Emergency stop all motors |
| `get_motor_info()` | Get connection information |

## Motor ID Mapping (From Previous Tests)

Based on earlier testing, the physical motor mapping is:

| Physical Motor | CAN ID Range | Primary ID |
|----------------|--------------|------------|
| Motor 1 | 8-15 | 8 |
| Motor 2 | 16-20 | 16 |
| Motor 3 | 21-30 | 21 |
| Motor 4 | 31-39 | 31 |
| Motor 8 | 64-71 | 64 |
| Motor 9 | 72-79 | 72 |

**Note:** Some motors respond to multiple CAN IDs. This is normal behavior for RobStride motors.

## Troubleshooting

### No motors found
```bash
# Check USB device
ls -la /dev/ttyUSB*

# Set permissions
sudo chmod 666 /dev/ttyUSB1

# Check if motors are powered
# Verify CAN bus wiring (CAN-H, CAN-L)
```

### Connection refused
```bash
# Check if another process is using the port
lsof /dev/ttyUSB1

# Kill the process if needed
sudo killall python3
```

### Motor not responding
```python
# Try scanning to verify motor is online
controller.scan_motors(start_id=1, end_id=127)

# Try different ID in the motor's range
# Example: If motor 3 doesn't respond at ID 21, try 22-30
```

## Protocol Details

### AT Command Format
The motors use AT protocol commands over serial:

```python
# Activate motor
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])

# Deactivate motor
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x00, 0x00, 0x0d, 0x0a])

# Load parameters
cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
             0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

# Move (jog command)
# See jetson_motor_interface.py for full implementation
```

## Next Steps

1. **Map Physical Motors:** Use `pulse_motor()` to identify which CAN ID corresponds to which physical motor
2. **Configure Single IDs:** If needed, reconfigure motors to respond to single IDs only
3. **Integrate with Main System:** Import `JetsonMotorController` into your main robot control code
4. **Test Coordinated Movement:** Test multiple motors moving together
5. **Implement Safety:** Add position limits and emergency stop buttons

## Files on Jetson

- `jetson_motor_interface.py` - Main Python interface (recommended)
- `JETSON_MOTOR_CONNECTION_SUMMARY.md` - Detailed connection info
- `scan_all_motors_wide.py` - Motor scanner
- `quick_motor_test.py` - Quick motor tester
- `test_all_ranges.py` - Test all motor ranges with patterns

## Example: Test All Motors

```python
from jetson_motor_interface import JetsonMotorController
import time

with JetsonMotorController() as controller:
    # Scan for all motors
    motors = controller.scan_motors()
    
    print(f"\nTesting {len(motors)} motors...")
    
    # Test each motor
    for motor_id in motors:
        print(f"\nTesting motor {motor_id}...")
        controller.pulse_motor(motor_id, pulses=2, duration=0.3)
        time.sleep(1)  # Pause between motors
    
    print("\n✅ All motors tested!")
```

## Support

For issues or questions:
1. Check the terminal output for error messages
2. Verify USB connection: `ls -la /dev/ttyUSB*`
3. Check motor power and CAN bus wiring
4. Review `JETSON_MOTOR_CONNECTION_SUMMARY.md` for detailed info

