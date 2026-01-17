# Robstride Motor Scanner

Scans for and tests Robstride motors using L91 protocol over USB-to-CAN adapter.

Based on code from: https://github.com/Jak3Gil/Melvin_november

## Quick Start

### Prerequisites

1. **USB-to-CAN adapter** connected (CH340 or similar, typically COM3)
2. **Python 3** with `pyserial` library
3. **Robstride motors** powered and connected via CAN bus

### Install Python Serial Library

```powershell
pip install pyserial
```

### Run Scanner

**Option 1: Using PowerShell script (recommended)**
```powershell
.\scan_motors.ps1
```

**Option 2: Using Python directly**
```powershell
python scan_robstride_motors.py COM3 921600
```

### Scan All Motor IDs

```powershell
python scan_robstride_motors.py COM3 921600 --scan-all
```

### Test a Specific Motor

```powershell
python scan_robstride_motors.py COM3 921600 --test 12
```

This will:
1. Activate the motor
2. Send a small forward movement
3. Stop
4. Send a small backward movement
4. Stop and deactivate

**⚠️ WARNING: The motor will move during testing!**

## Command Line Options

```
python scan_robstride_motors.py [COM_PORT] [BAUD_RATE] [OPTIONS]

Arguments:
  COM_PORT              Serial port (default: COM3)
  BAUD_RATE             Baud rate (default: 921600)

Options:
  --scan-all            Scan all motor IDs (1-14)
  --test CAN_ID         Test specific motor ID (e.g., 12 for 0x0C)

Examples:
  python scan_robstride_motors.py COM3 921600
  python scan_robstride_motors.py COM3 921600 --scan-all
  python scan_robstride_motors.py COM3 921600 --test 12
```

## Common Motor IDs

- **Motor 12**: CAN ID 0x0C (12)
- **Motor 13**: CAN ID 0x0D (13)
- **Motor 14**: CAN ID 0x0E (14)

The scanner defaults to checking these three IDs.

## L91 Protocol

The scanner uses L91 protocol AT commands sent over serial:

- **Detect**: `AT+AT\r\n` (0x41 0x54 0x2B 0x41 0x54 0x0D 0x0A)
- **Activate**: `AT 00 07 e8 <can_id> 01 00 0d 0a`
- **Load Params**: `AT 20 07 e8 <can_id> 08 00 c4 00 00 00 00 00 00 0d 0a`
- **Move Jog**: `AT 90 07 e8 <can_id> 08 05 70 00 00 07 <flag> <speed> 0d 0a`
- **Deactivate**: `AT 00 07 e8 <can_id> 00 00 0d 0a`

## Troubleshooting

### Port Not Found
- Check Device Manager for COM ports
- Try different COM port: `python scan_robstride_motors.py COM4 921600`
- Verify USB-to-CAN adapter is connected

### No Motors Found
1. **Check connections**:
   - USB-to-CAN adapter connected
   - Motors powered on
   - CAN bus connections (CAN-H, CAN-L)
   - Termination resistors (120Ω at both ends)

2. **Try different baud rate**:
   ```powershell
   python scan_robstride_motors.py COM3 115200
   ```

3. **Check motor power**:
   - Verify motors are receiving power
   - Check CAN bus voltage levels

4. **Try scanning all IDs**:
   ```powershell
   python scan_robstride_motors.py COM3 921600 --scan-all
   ```

### Serial Port Already in Use
- Close any other programs using the COM port
- Close Arduino IDE Serial Monitor
- Close PlatformIO Serial Monitor
- Close any terminal programs

### Python Serial Error
- Install pyserial: `pip install pyserial`
- Verify Python version: `python --version` (need 3.x)
- Run as administrator if needed

## Hardware Setup

1. **USB-to-CAN Adapter**
   - Connect to computer via USB
   - Typically shows as COM3 (CH340) or similar
   - Should support 921600 baud (or 115200)

2. **CAN Bus Connections**
   - CAN-H (High) - connect to motor CAN-H
   - CAN-L (Low) - connect to motor CAN-L
   - GND - common ground
   - 120Ω termination resistor at both ends

3. **Motor Power**
   - Ensure motors are powered
   - Check voltage levels
   - Verify CAN bus communication is enabled

## Output Example

```
╔═══════════════════════════════════════════════════════╗
║  Robstride Motor Scanner (L91 Protocol)              ║
╚═══════════════════════════════════════════════════════╝

Port: COM3
Baud Rate: 921600

Opening serial port COM3 at 921600 baud...
✓ Serial port opened

==================================================
Step 1: Detecting motors (AT+AT command)
==================================================
Sending: AT+AT\r\n
  Hex: 41 54 2b 41 54 0d 0a
✓ Detection command sent

==================================================
Step 2: Scanning Motor IDs
==================================================

Testing Motor ID 0x0C (12)...
  Sending activate command...
  Hex: 41 54 00 07 e8 0c 01 00 0d 0a
  ✓ Commands sent to Motor ID 0x0C

Testing Motor ID 0x0D (13)...
  ...

==================================================
Scan Results
==================================================

✓ Found 3 motor(s):
  - Motor ID 0x0C (12)
  - Motor ID 0x0D (13)
  - Motor ID 0x0E (14)
```

## References

- Repository: https://github.com/Jak3Gil/Melvin_november
- L91 Protocol implementation in: `test_motors_l91_921600.c`, `map_can_ids_to_physical_motors.c`

