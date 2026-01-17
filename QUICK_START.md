# Quick Start - Interactive Motor Tester

## If you get "COM3 is locked" error:

### Step 1: Free COM3
Double-click `free_com3.ps1` to check if COM3 is available.

**Or manually:**
1. Close ALL terminal windows (Command Prompt, PowerShell)
2. Close Arduino IDE (if open)
3. Close PlatformIO Serial Monitor (if open)
4. Close any Python scripts that might be running
5. **OR** unplug and replug the USB-to-CAN adapter

### Step 2: Run the tester
Double-click `test_motors.bat`

## Controls (while tester is running):
- **W** = Move motor forward (small jog)
- **S** = Move motor backward (small jog)  
- **SPACE** = Next motor
- **Q** = Quit

## Troubleshooting:

**"Access is denied" error:**
- COM3 is locked by another program
- Run `free_com3.ps1` first
- Close all terminal/serial programs
- Unplug/replug USB adapter

**Script closes immediately:**
- Check error message
- Make sure COM3 is free (run `free_com3.ps1`)
- Make sure motors are powered on

**No response from motors:**
- Check motor power
- Check CAN bus connections
- Verify motors are properly connected

