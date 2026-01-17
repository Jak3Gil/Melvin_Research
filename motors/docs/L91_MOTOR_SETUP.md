# L91 Motor Control Setup

This ESP32 code bridges CAN bus commands from a vision system to Robstride motors using the L91 protocol.

## Hardware Connections

### CAN Bus (Vision System → ESP32)
- **CAN TX**: GPIO 5 (connect to CAN transceiver TX)
- **CAN RX**: GPIO 18 (connect to CAN transceiver RX)
- **CAN Transceiver**: MCP2551 or similar (3.3V compatible)
- **CAN Termination**: 120Ω resistor at both ends of CAN bus

### L91 Motor Control (ESP32 → Motors)
- **Serial2 TX**: GPIO 16 (connect to L91-to-CAN adapter RX)
- **Serial2 RX**: GPIO 17 (connect to L91-to-CAN adapter TX)
- **L91 Adapter**: CH340 USB-to-Serial adapter configured for L91 protocol
- **Baud Rate**: 921600 baud
- **Protocol**: AT commands over serial

### Existing Hardware
- **Servo**: GPIO 13 (PWM)
- **RGB LED**: GPIO 15 (R), GPIO 2 (G), GPIO 4 (B)
- **MPU-6050**: I2C (GPIO 21 = SDA, GPIO 22 = SCL)

## CAN Message Protocol

The ESP32 receives CAN messages and converts them to L91 motor commands:

### Message Format
- **CAN ID**: Motor ID (0x0C = Motor 12, 0x0D = Motor 13, 0x0E = Motor 14)
- **Data[0]**: Speed command as signed byte (-128 to 127)
  - 127 = +1.0 (full forward)
  - 0 = 0.0 (stop)
  - -128 = -1.0 (full reverse)

### Example CAN Messages
```
ID=0x0C, Data=[0x40]  → Motor 12, speed = 0.5 (50% forward)
ID=0x0D, Data=[0xC0]  → Motor 13, speed = -0.5 (50% reverse)
ID=0x0E, Data=[0x00]  → Motor 14, speed = 0.0 (stop)
```

## L91 Protocol Details

The L91 protocol uses AT commands sent over serial at 921600 baud.

### Command Format
All commands start with `AT` (0x41 0x54) and end with `\r\n` (0x0D 0x0A).

### Key Commands

#### Activate Motor
```
AT 00 07 e8 <can_id> 01 00 0d 0a
```
Activates the motor with the specified CAN ID.

#### Load Parameters
```
AT 20 07 e8 <can_id> 08 00 c4 00 00 00 00 00 00 0d 0a
```
Loads motor parameters (required after activation).

#### Move Jog (Velocity Control)
```
AT 90 07 e8 <can_id> 08 05 70 00 00 07 <flag> <speed_bytes> 0d 0a
```
- `flag`: 0 = stop, 1 = move
- `speed_bytes`: 16-bit signed value (0x7FFF = 0.0, 0x8000+ = forward, 0x7FFF- = reverse)

## Software Architecture

### Files
- `src/l91_motor.h` / `src/l91_motor.cpp`: L91 protocol library
- `src/main.cpp`: Main code with CAN-to-L91 bridge

### Key Functions

#### L91Motor Class
```cpp
L91Motor motor(&Serial2, 921600);  // Initialize
motor.begin();                      // Start serial
motor.activateMotor(can_id);        // Activate motor
motor.loadParams(can_id);           // Load parameters
motor.moveMotor(can_id, speed);     // Move motor (-1.0 to 1.0)
motor.stopMotor(can_id);            // Stop motor
```

#### CAN Bus
- Uses ESP32 TWAI (Two-Wire Automotive Interface)
- 500kbps bitrate
- Accepts all CAN IDs (filter can be customized)

## Setup Steps

1. **Hardware Connections**
   - Connect CAN transceiver to GPIO 4/5
   - Connect L91 adapter to GPIO 16/17
   - Power motors and ensure proper termination

2. **Upload Code**
   ```powershell
   .\upload.ps1
   ```

3. **Monitor Serial Output**
   ```powershell
   python -m platformio device monitor
   ```

4. **Verify Initialization**
   - Check for "CAN bus ready" message
   - Check for "L91 Motor Controller ready" message
   - Check for motor activation messages

## Testing

### Test CAN Messages
You can send test CAN messages using a CAN analyzer or another CAN device:
- Send ID=0x0C, Data=[0x40] to test Motor 12 at 50% speed
- Send ID=0x0D, Data=[0xC0] to test Motor 13 at -50% speed
- Send ID=0x0E, Data=[0x00] to stop Motor 14

### Monitor L91 Commands
Connect a serial monitor to Serial2 (GPIO 16/17) at 921600 baud to see L91 commands being sent.

## Troubleshooting

### CAN Bus Issues
- **No messages received**: Check CAN transceiver connections, termination resistors
- **Wrong bitrate**: Modify `TWAI_TIMING_CONFIG_500KBITS()` in main.cpp
- **GPIO conflicts**: Change CAN_TX_PIN and CAN_RX_PIN if needed

### L91 Motor Issues
- **Motors don't activate**: Check Serial2 connections, verify L91 adapter is powered
- **Wrong baud rate**: Verify adapter supports 921600 baud
- **No response**: Check motor power, CAN bus connections from adapter to motors

### Serial Port Conflicts
- GPIO 17 (Serial2 RX) may conflict with other pins
- If using different GPIO, modify `L91Motor` constructor to use different Serial port

## Customization

### Change Motor IDs
Edit `MOTOR_12_CAN_ID`, `MOTOR_13_CAN_ID`, `MOTOR_14_CAN_ID` in `l91_motor.h`.

### Change CAN Protocol
Modify `processCANMessage()` in `main.cpp` to parse different CAN message formats.

### Add More Motors
1. Add motor ID defines in `l91_motor.h`
2. Add activation/initialization in `setup()`
3. Add CAN message handling in `processCANMessage()`

## References

- L91 protocol implementation from: https://github.com/Jak3Gil/Melvin_november
- ESP32 TWAI documentation: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/twai.html

