# PowerShell Commands to Run Motor Tester

## Step 1: Navigate to Project Directory

From PowerShell (starting at `C:\Users\Owner>`):

```powershell
cd F:\Melvin_Research\Melvin_Research
```

## Step 2: Run the Motor Tester

**Option 1: Debug version (recommended - shows errors clearly):**
```powershell
python test_motors_interactive_debug.py COM3 921600
```

**Option 2: Original version:**
```powershell
python test_motors_interactive.py COM3 921600
```

## One-Line Command (all in one):

```powershell
cd F:\Melvin_Research\Melvin_Research; python test_motors_interactive_debug.py COM3 921600
```

## If COM3 is Locked:

First check if COM3 is available:
```powershell
cd F:\Melvin_Research\Melvin_Research; python -c "import serial; s=serial.Serial('COM3', 115200); s.close(); print('COM3 is available')"
```

If you get an error, COM3 is locked. Close other programs or unplug/replug the USB adapter.

## Controls (when script is running):
- **W** = Move motor forward
- **S** = Move motor backward
- **SPACE** = Next motor
- **Q** = Quit

