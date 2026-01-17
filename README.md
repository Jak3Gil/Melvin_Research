# Melvin_Research

## ESP32 Servo Control Project

> **See also:** [`motors/`](motors/) (CAN/L91/Robstride), [`cameras/`](cameras/) (vision, YOLO, streaming), [`voice/`](voice/) (Piper TTS, Whisper), [`jetson/`](jetson/), [`upload/`](upload/) (ESP32), [`tools/`](tools/).

This project controls a servo motor connected to GPIO pin 13 on an ESP32.

### Hardware Setup
- ESP32 connected via USB
- Servo motor connected to GPIO pin 13
- Servo power: Red wire to 5V, Black wire to GND, Yellow/Orange wire (signal) to GPIO 13

### Software Requirements
- Python 3.x (for PlatformIO)
- PlatformIO Core (installed via pip)

### Installation & Setup

1. **Install USB Drivers** (if ESP32 is not detected):
   - CH340 driver: Download from [CH340 driver page](https://www.wch.cn/downloads/CH341SER_EXE.html)
   - CP2102 driver: Download from [Silicon Labs](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
   - Install the appropriate driver for your ESP32 board

2. **Identify COM Port**:
   ```powershell
   python -m platformio device list
   ```
   Look for a USB Serial Port (usually shows as "USB Serial" or "CH340" or "CP2102")

3. **Upload Code**:
   - **IMPORTANT**: Before uploading, put ESP32 in bootloader mode:
     - Hold the **BOOT** button on your ESP32
     - Press and release the **RESET** button (while holding BOOT)
     - Release the **BOOT** button
     - The ESP32 is now in bootloader mode
   
   - **Option 1**: Use the upload script (recommended):
     ```powershell
     .\upload\upload.ps1
     ```
     The script will prompt you to put ESP32 in bootloader mode
   
   - **Option 2**: Manual upload:
     ```powershell
     python -m platformio run --target upload --upload-port COMX
     ```
     Replace `COMX` with your ESP32's COM port (e.g., COM3, COM4, COM6)
     **Make sure ESP32 is in bootloader mode before running this command!**

### Code Description
The code moves the servo through a sequence:
- Starts at center position (90°)
- Moves to 0°, then 90°, then 180°
- Performs a small movement demonstration (85° to 95°)
- Repeats the cycle

### Monitor Serial Output
To see the serial output from the ESP32:
```powershell
python -m platformio device monitor
```

### Troubleshooting
- **Port not found**: Check Device Manager for COM ports, ensure USB drivers are installed
- **Upload fails**: Put ESP32 in bootloader mode (see step 4 above)
- **Servo doesn't move**: Check wiring, ensure servo is powered (5V), verify GPIO 13 connection