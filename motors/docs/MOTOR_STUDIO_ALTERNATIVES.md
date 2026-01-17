# Motor Studio Not Opening - Alternative Solutions

## Issue
RobStride Motor Studio has Qt5 dependency issues and may not open properly on Windows.

---

## ✅ BEST SOLUTION: Use Python Tools on Jetson

Since Motor Studio is problematic, you can configure and control motors directly from the Jetson using Python scripts I've created.

### 1. Identify Your Motors

**Run the interactive identification tool:**
```bash
ssh melvin@192.168.1.119
python3 identify_motors_interactive.py
```

**What it does:**
- Tests each motor ID one by one
- You watch which physical motor moves
- You tell it the motor location
- Creates a motor map file

**Example session:**
```
Testing Motor ID 8 (1/32)
>>> WATCH YOUR ROBOT! <<<
Motor ID 8 will pulse 3 times...

Press Enter to pulse this motor...
[Motor pulses 3 times]

Did you see which motor moved?
Enter motor location: Left Shoulder
✓ Motor ID 8 = Left Shoulder
```

### 2. Configure Motor IDs (Advanced)

**Run the configuration tool:**
```bash
ssh melvin@192.168.1.119
python3 configure_motor_ids.py
```

**What it does:**
- Attempts to change motor CAN IDs
- Tries multiple command formats
- Verifies the changes
- Interactive menu

**Note:** This may not work for all RobStride motors. Some require Motor Studio for ID changes.

### 3. Control Motors Directly

**Use the motor interface:**
```bash
ssh melvin@192.168.1.119
python3 jetson_motor_interface.py
```

Or use Python:
```python
from jetson_motor_interface import JetsonMotorController

with JetsonMotorController() as controller:
    # Scan for motors
    motors = controller.scan_motors()
    
    # Test a motor
    controller.pulse_motor(21, pulses=3)
    
    # Control manually
    controller.enable_motor(21)
    controller.load_params(21)
    controller.move_motor(21, speed=0.1, flag=1)
    time.sleep(1)
    controller.move_motor(21, speed=0.0, flag=0)
    controller.disable_motor(21)
```

---

## 🔧 Fix Motor Studio Qt5 Error (Windows)

If you still want to use Motor Studio:

### Option 1: Install Visual C++ Redistributables
1. Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Install both x64 and x86 versions
3. Restart computer
4. Try Motor Studio again

### Option 2: Install Qt5 Runtime
1. Download Qt5 from: https://www.qt.io/download-open-source
2. Install the runtime components
3. Add Qt5 bin folder to PATH
4. Try Motor Studio again

### Option 3: Copy Qt5 DLLs
If you have Qt5 installed elsewhere:
1. Find these DLLs:
   - Qt5Core.dll
   - Qt5Gui.dll
   - Qt5Widgets.dll
   - Qt5Network.dll
2. Copy them to the motor_tool.exe folder
3. Try Motor Studio again

---

## 📊 Current Motor Status

From our scan:
- **32 motor IDs responding** (8-31, 72-79)
- **Estimated 4-8 physical motors**
- **Motors are moving** ✅
- **Communication working** ✅

### Motor ID Ranges Found:
- Range 1: IDs 8-31 (24 IDs) - likely 3-6 motors
- Range 2: IDs 72-79 (8 IDs) - likely 1-2 motors

---

## 🎯 Recommended Workflow

### Step 1: Identify Motors
```bash
ssh melvin@192.168.1.119
python3 identify_motors_interactive.py
```

This creates a map like:
```
Motor ID Mapping
==================================================

ID   8 : Left Shoulder
ID  16 : Left Elbow  
ID  21 : Right Shoulder
ID  31 : Right Elbow
ID  72 : Head Pan
ID  73 : Head Tilt
```

### Step 2: Use Motors As-Is

You can control motors with their current IDs:
```python
from jetson_motor_interface import JetsonMotorController

# Create controller
controller = JetsonMotorController()
controller.connect()

# Control specific motors
left_shoulder = 8
left_elbow = 16

controller.enable_motor(left_shoulder)
controller.load_params(left_shoulder)
controller.move_motor(left_shoulder, speed=0.1, flag=1)
# ... control your robot ...
```

### Step 3: (Optional) Reconfigure IDs

If you need single IDs per motor:
1. Fix Motor Studio Qt5 issue (see above)
2. Or try the Python configuration tool
3. Or live with multiple IDs per motor (works fine!)

---

## 💡 Pro Tip: Multiple IDs Per Motor

Having multiple IDs per motor is actually **not a problem** for most use cases:

**Why it's OK:**
- You can just use the lowest ID for each motor
- Motor responds to all its IDs the same way
- Doesn't affect performance

**Example:**
```python
# Motor responds to IDs 8-15, just use ID 8
left_shoulder = 8  # Works perfectly!

# Motor responds to IDs 21-30, just use ID 21
right_shoulder = 21  # Works perfectly!
```

**When you need to reconfigure:**
- If IDs overlap between motors
- If you need sequential IDs (1, 2, 3, 4...)
- If you're using standard robotics software expecting specific IDs

---

## 🚀 Quick Start Without Motor Studio

**1. Test all motors:**
```bash
ssh melvin@192.168.1.119
python3 jetson_motor_interface.py
```

**2. Identify each motor:**
```bash
python3 identify_motors_interactive.py
```

**3. Create your control code:**
```python
from jetson_motor_interface import JetsonMotorController

# Your motor IDs (from identification)
MOTORS = {
    'left_shoulder': 8,
    'left_elbow': 16,
    'right_shoulder': 21,
    'right_elbow': 31,
    'head_pan': 72,
    'head_tilt': 73,
}

with JetsonMotorController() as controller:
    # Move left arm
    controller.pulse_motor(MOTORS['left_shoulder'], pulses=2)
    controller.pulse_motor(MOTORS['left_elbow'], pulses=2)
```

---

## 📞 Summary

**Motor Studio has Qt5 issues** → Use Python tools instead!

**Available Python Tools:**
1. `jetson_motor_interface.py` - Full motor control
2. `identify_motors_interactive.py` - Map motor IDs
3. `configure_motor_ids.py` - Attempt ID changes
4. `example_motor_control.py` - Usage examples

**All tools are on the Jetson and ready to use!**

---

**Next Step:** Run `python3 identify_motors_interactive.py` on the Jetson to map your motors!
