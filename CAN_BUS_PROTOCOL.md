# CAN Bus Protocol Documentation - Robstride Motors

## Overview

This document describes the CAN bus communication protocol used to control Robstride motors. The system uses USB-to-CAN adapters to communicate with motors over CAN bus using the **L91 protocol** (Robstride proprietary protocol).

---

## ⚠️ CRITICAL: Robstride 02 and 03 Motor Separation

**IMPORTANT:** **Robstride 02 and Robstride 03 motors MUST be on separate CAN buses.**

- **Robstride 02 motors** must be on one CAN bus
- **Robstride 03 motors** must be on a different CAN bus
- **They cannot share the same CAN bus**

This is a hardware/firmware requirement. Mixing Robstride 02 and 03 motors on the same bus will cause communication failures.

---

## Hardware Setup

### USB-to-CAN Adapters

The system uses USB-to-CAN adapters that appear as serial devices:
- **Windows**: `COM6`, `COM7`, etc.
- **Linux/Jetson**: `/dev/ttyUSB0`, `/dev/ttyUSB1`, etc.

### Communication Parameters

- **Baud Rate**: `921600` (for serial communication with USB-CAN adapter)
- **CAN Bus Speed**: `1 Mbps` (configured via AT commands)
- **Protocol**: L91 (Robstride proprietary protocol)

### Jetson Setup

On the Jetson device, we use two USB-CAN adapters:
- **Motor 6**: `/dev/ttyUSB0`
- **Motor 8**: `/dev/ttyUSB1`

---

## Protocol: L91 (Robstride Proprietary)

The L91 protocol is a proprietary protocol used by Robstride motors. It uses a specific command format sent over CAN bus via USB-CAN adapters.

### Command Format

Commands are sent as hexadecimal byte sequences with the following structure:

#### Extended Format (Most Common)
```
41 54 20 07 e8 [BYTE] 08 00 c4 00 00 00 00 00 00 0d 0a
```

Where:
- `41 54` = "AT" prefix
- `20` = Extended format flag
- `07 e8` = Base CAN ID (0x07e8 = 2024 decimal)
- `[BYTE]` = Motor-specific byte value (see Motor ID Mapping below)
- `08 00 c4 00 00 00 00 00 00` = Protocol-specific data
- `0d 0a` = CRLF terminator

#### Standard Format (Some Motors)
```
41 54 00 07 e8 [BYTE] 01 00 0d 0a
```

### Motor ID to Byte Value Mapping

| Motor ID | Byte Value (Hex) | Extended Format Command | Notes |
|----------|------------------|-------------------------|-------|
| 1        | 0x0c             | `41542007e80c0800c40000000000000d0a` | Extended |
| 2        | 0x54             | `41540007e85401000d0a` | Standard |
| 3        | 0x1c             | `41542007e81c0800c40000000000000d0a` | Extended |
| 4        | 0x64             | `41540007e86401000d0a` | Standard |
| 5        | 0x6c             | `41540007e86c01000d0a` | Standard |
| 6        | 0x34             | `41542007e8340800c40000000000000d0a` | Extended |
| 7        | 0x3c             | `41542007e83c0800c40000000000000d0a` | Extended |
| 8        | 0x44             | `41542007e8440800c40000000000000d0a` | Extended |
| 9        | 0x4c             | `41542007e84c0800c40000000000000d0a` | Extended |
| 10       | 0x54             | `41542007e8540800c40000000000000d0a` | Extended |
| 11       | 0x9c             | `41540007e89c01000d0a` | Standard |
| 12       | 0x64             | `41542007e8640800c40000000000000d0a` | Extended |
| 13       | 0x6c             | `41542007e86c0800c40000000000000d0a` | Extended |
| 14       | 0x74             | `41542007e8740800c40000000000000d0a` | Extended |

**Note**: The byte value is NOT the same as the motor ID. Use the mapping table above.

---

## Initialization Sequence

Before sending motor commands, the USB-CAN adapter must be initialized:

### Step 1: Connect to Serial Port
```python
import serial
ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=2.0)
time.sleep(0.5)
```

### Step 2: Initialize Adapter with AT Commands
```python
# AT+AT command (reset/initialize)
ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
time.sleep(0.5)
ser.read(500)  # Clear response buffer

# AT+A0 command (set CAN speed to 1 Mbps)
ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
time.sleep(0.5)
ser.read(500)  # Clear response buffer
```

### Step 3: Activate Motor
```python
# Example: Activate Motor 6 (byte 0x34, extended format)
cmd_activate = bytes.fromhex("41542007e8340800c40000000000000d0a")
ser.write(cmd_activate)
ser.flush()
time.sleep(0.1)

# Read response
response = bytearray()
start = time.time()
while time.time() - start < 1.0:
    if ser.in_waiting > 0:
        response.extend(ser.read(ser.in_waiting))
    time.sleep(0.03)

if response:
    print(f"Motor activated: {response.hex()}")
```

---

## Movement Commands

### JOG Command (Extended Format)

To move a motor, use the JOG command with extended format:

```python
def move_motor_jog_extended(ser, byte_val, speed, flag=1):
    """
    Move motor using JOG command (extended format)
    
    Args:
        ser: Serial port object
        byte_val: Motor byte value (e.g., 0x34 for Motor 6, 0x44 for Motor 8)
        speed: Speed value (-1.0 to 1.0)
        flag: Movement flag (1 = move, 0 = stop)
    """
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    # Extended format JOG command
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, byte_val])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)

def stop_motor(ser, byte_val):
    """Stop motor"""
    move_motor_jog_extended(ser, byte_val, 0.0, 0)
```

### Speed Calculation

- **Forward (positive speed)**: `speed_val = 0x8000 + int(speed * 3283.0)`
- **Backward (negative speed)**: `speed_val = 0x7fff + int(speed * 3283.0)`
- **Stop**: `speed_val = 0x7fff` with `flag = 0`

**Speed Range**: `-1.0` to `1.0` (normalized)

---

## Complete Example: Moving Motor 6 and Motor 8 on Jetson

```python
#!/usr/bin/env python3
import serial
import time

def send_and_get_response(ser, cmd, timeout=0.5):
    """Send command and get response"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.03)
    
    return response.hex() if len(response) > 0 else None

def move_motor_jog_extended(ser, byte_val, speed, flag=1):
    """Move motor using JOG command (extended format)"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, byte_val])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)

def stop_motor(ser, byte_val):
    """Stop motor"""
    move_motor_jog_extended(ser, byte_val, 0.0, 0)

# Open both serial ports
ser_m6 = serial.Serial('/dev/ttyUSB0', 921600, timeout=2.0)  # Motor 6
ser_m8 = serial.Serial('/dev/ttyUSB1', 921600, timeout=2.0)  # Motor 8
time.sleep(0.5)

# Initialize both adapters
print("Initializing adapters...")
ser_m6.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
time.sleep(0.5)
ser_m6.read(500)
ser_m6.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
time.sleep(0.5)
ser_m6.read(500)

ser_m8.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
time.sleep(0.5)
ser_m8.read(500)
ser_m8.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
time.sleep(0.5)
ser_m8.read(500)

# Activate both motors
print("Activating motors...")
cmd_6_act = bytes.fromhex("41542007e8340800c40000000000000d0a")  # Motor 6
cmd_8_act = bytes.fromhex("41542007e8440800c40000000000000d0a")  # Motor 8

resp6 = send_and_get_response(ser_m6, cmd_6_act, timeout=1.0)
resp8 = send_and_get_response(ser_m8, cmd_8_act, timeout=1.0)

if resp6:
    print(f"Motor 6 activated: {resp6}")
if resp8:
    print(f"Motor 8 activated: {resp8}")

# Move both motors forward
speed = 0.05
print(f"Moving both motors forward (speed={speed})...")
move_motor_jog_extended(ser_m6, 0x34, speed, 1)  # Motor 6 (byte 0x34)
move_motor_jog_extended(ser_m8, 0x44, speed, 1)  # Motor 8 (byte 0x44)
time.sleep(3.0)

# Stop both motors
print("Stopping both motors...")
stop_motor(ser_m6, 0x34)
stop_motor(ser_m8, 0x44)

# Close serial ports
ser_m6.close()
ser_m8.close()
```

---

## Response Format

When a motor responds to an activation command, it typically returns:

```
41 54 10 00 37 ec 08 00 c4 56 00 02 03 09 07 0d 0a
```

Where:
- `41 54` = "AT" prefix
- `10 00` = Response header
- `37 ec` = CAN ID (varies by motor)
- Remaining bytes = Motor status/data

---

## Troubleshooting

### No Response from Motor

1. **Check CAN bus wiring**:
   - Verify CAN_H and CAN_L are connected
   - Check for proper termination (120Ω resistors at both ends)
   - Verify GND connection

2. **Check motor power**:
   - Ensure motors are powered on
   - Check power supply voltage

3. **Verify adapter initialization**:
   - Check that AT+AT and AT+A0 commands return responses
   - Verify adapter responds to AT commands

4. **Check motor ID and byte value**:
   - Use the correct byte value from the mapping table
   - Verify motor is on the correct CAN bus (Robstride 02 vs 03 separation)

5. **Check USB port assignment**:
   - On Jetson: Verify `/dev/ttyUSB0` and `/dev/ttyUSB1` exist
   - On Windows: Verify `COM6` or other COM port is available
   - Close other programs using the port (e.g., Motor Studio)

### Motor Not Moving

1. **Verify activation**:
   - Motor must be activated before movement commands
   - Check that activation command received a response

2. **Check speed value**:
   - Speed should be between -1.0 and 1.0
   - Very small speeds (< 0.01) may not produce visible movement

3. **Verify command format**:
   - Use extended format JOG command
   - Check byte value matches motor ID

---

## Platform-Specific Notes

### Windows (COM6)

- Port: `COM6` (or other COM port)
- May need to close Motor Studio or other programs using the port
- Use `serial.Serial('COM6', 921600, timeout=2.0)`

### Jetson (Linux)

- Ports: `/dev/ttyUSB0`, `/dev/ttyUSB1`
- May need permissions: `sudo chmod 666 /dev/ttyUSB*`
- Use `serial.Serial('/dev/ttyUSB0', 921600, timeout=2.0)`

---

## Protocol Summary

1. **Initialize adapter**: AT+AT, then AT+A0
2. **Activate motor**: Send activation command with motor-specific byte value
3. **Move motor**: Send JOG command with speed and direction
4. **Stop motor**: Send JOG command with speed=0.0 and flag=0

**Remember**: Robstride 02 and 03 motors must be on separate CAN buses!

---

## References

- Working scripts:
  - `motors/scripts/move_motor8_slow.py` - Single motor movement example
  - `motors/scripts/move_m6_m8_jetson.py` - Dual motor movement on Jetson
  - `motors/scripts/detect_robstride02_canopen_com6.py` - Motor detection example

---

*Last Updated: Based on working implementation with Motor 6 and Motor 8 on Jetson*

