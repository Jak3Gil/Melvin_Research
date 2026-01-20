# Jetson – Connect and Tests

Jetson Nano/Orin connection and quick test scripts.

## Launchers

- **connect_jetson.bat** / **connect_jetson.ps1** – SSH/shell to Jetson
- **find_usb_can_jetson.bat** / **find_usb_can_jetson.ps1** / **find_usb_can_jetson.py** – Find USB-CAN adapters on Jetson via USB connection
- **find_usb_can_jetson.sh** – Shell script to run directly on Jetson to find USB-CAN adapters
- **test_hello_jetson.sh** – basic connectivity test
- **test_ollama_jetson.sh** – Ollama / LLM test

## Finding USB-CAN Adapters

To find USB-CAN adapters connected to the Jetson:

1. **From Windows (via USB network connection):**
   ```powershell
   .\jetson\launchers\find_usb_can_jetson.ps1
   ```
   Or use the Python version:
   ```bash
   python jetson\launchers\find_usb_can_jetson.py
   ```

2. **Directly on Jetson:**
   ```bash
   bash jetson/launchers/find_usb_can_jetson.sh
   ```

The scripts will check for:
- USB devices (lsusb)
- USB serial devices (/dev/ttyUSB*)
- CAN interfaces (can0, can1, etc.)
- Network interfaces
- Recent kernel messages
- Required tools and libraries

