# Motor Reconfiguration Plan

## Current Situation
- **48 motor IDs responding** (8-39, 64-79)
- **Estimated 6-8 physical motors** (each responding to multiple IDs)
- **Need:** Each motor configured to single, unique ID

---

## 🎯 Goal: Reconfigure Motors to Single IDs

### Target Configuration:
```
Physical Motor          Current IDs        →  New ID
─────────────────────────────────────────────────────
Motor 1 (Left Shoulder)   8-15            →    1
Motor 2 (Left Elbow)      16-23           →    2
Motor 3 (Right Shoulder)  24-31           →    3
Motor 4 (Right Elbow)     32-39           →    4
Motor 5 (Head Pan)        64-71           →    5
Motor 6 (Head Tilt)       72-79           →    6
... additional motors ...                 →  7, 8, 9...
```

---

## 📋 Reconfiguration Methods

### Method 1: RobStride Motor Studio (Recommended)

**Step 1: Fix Qt5 Error**

I've opened the Visual C++ Redistributables download. Please:

1. **Download and install:**
   - File: `vc_redist.x64.exe`
   - Install the x64 version
   - Restart your computer after installation

2. **Also install x86 version (optional but recommended):**
   - Download: https://aka.ms/vs/17/release/vc_redist.x86.exe
   - Install and restart

**Step 2: Connect USB-to-CAN to Windows**

1. Unplug USB-to-CAN from Jetson
2. Plug into Windows PC
3. Windows should detect it (COM port)

**Step 3: Open Motor Studio**

After installing Visual C++ Redistributables:

```batch
# Run the launcher I created
.\launch_motor_studio.bat

# Or navigate manually to:
c:\Users\Owner\Downloads\Studio (2)\Studio\
  → Find motor_tool.exe or z1_motor_tool.exe
  → Double-click to open
```

**Step 4: Configure Each Motor**

In Motor Studio:
1. Select COM port (check Device Manager)
2. Set baud rate: **921600**
3. Click "Connect"
4. Click "Scan" to find motors
5. Select each motor
6. Change CAN ID to unique value (1, 2, 3, etc.)
7. Click "Save" or "Write"
8. Verify by rescanning

---

### Method 2: Python Configuration Tool (Backup)

If Motor Studio still doesn't work, use the Python tool:

```bash
ssh melvin@192.168.1.119
python3 configure_motor_ids.py
```

**Features:**
- Interactive menu
- Test motors before configuring
- Attempts multiple command formats
- Verifies changes

**Limitations:**
- May not work for all RobStride motor models
- Some motors require Motor Studio for ID changes
- Success depends on motor firmware version

---

## 🔍 Step-by-Step: Identify Then Reconfigure

### Phase 1: Identify Physical Motors (Do First!)

Before reconfiguring, you need to know which IDs control which physical motor:

```bash
ssh -t melvin@192.168.1.119 "python3 identify_motors_interactive.py"
```

**This will:**
1. Test motor ID 8 → You watch which motor moves
2. You enter: "Left Shoulder" (or whatever it is)
3. Test motor ID 16 → You watch and identify
4. Continue for all motors
5. Creates motor_map.txt file

**Example output:**
```
Motor ID Mapping
==================================================

ID   8 : Left Shoulder Pan
ID  16 : Left Elbow
ID  24 : Right Shoulder Pan  
ID  32 : Right Elbow
ID  64 : Head Pan
ID  72 : Head Tilt
```

### Phase 2: Reconfigure IDs

Once you know which motor is which:

**In Motor Studio:**
1. Select motor at ID 8 (Left Shoulder)
2. Change ID to 1
3. Save
4. Select motor at ID 16 (Left Elbow)
5. Change ID to 2
6. Save
7. Repeat for all motors

**Or with Python tool:**
```bash
python3 configure_motor_ids.py

# Interactive session:
Enter current motor ID: 8
Enter NEW motor ID: 1
Confirm? yes
[Attempts to change ID 8 → 1]
```

---

## ⚠️ Important Notes

### Before Reconfiguring:

1. **Document current state:**
   - Run identification tool first
   - Save motor_map.txt
   - Take photos/notes

2. **One motor at a time:**
   - Configure motors individually
   - Test after each change
   - Don't rush

3. **Power cycle after changes:**
   - Some motors need power cycle to apply new ID
   - Turn off power, wait 5 seconds, turn on

4. **Verify each change:**
   - Rescan after each motor
   - Test the new ID works
   - Make sure old IDs don't respond

### ID Assignment Strategy:

**Option A: Sequential (1, 2, 3, 4...)**
- Pros: Simple, standard
- Cons: Need to remember which is which

**Option B: Grouped by function**
- Left arm: 1-4
- Right arm: 5-8  
- Head: 9-10
- Body: 11+

**Option C: Use lowest current ID**
- Motor at 8-15 → keep as 8
- Motor at 16-23 → keep as 16
- Pros: No reconfiguration needed!
- Cons: Non-sequential IDs

---

## 🚀 Recommended Workflow

### Step 1: Install Visual C++ Redistributables
- Download from browser (I opened it for you)
- Install x64 version
- Restart computer

### Step 2: Identify Motors First
```bash
ssh -t melvin@192.168.1.119 "python3 identify_motors_interactive.py"
```
- Test each motor
- Document which is which
- Save the motor map

### Step 3: Open Motor Studio
```batch
.\launch_motor_studio.bat
```
- Select COM port
- Set baud 921600
- Connect and scan

### Step 4: Reconfigure IDs
- Change each motor to unique ID
- Test after each change
- Power cycle if needed

### Step 5: Verify on Jetson
```bash
ssh melvin@192.168.1.119
python3 scan_all_motors_wide.py /dev/ttyUSB1 921600 --start 1 --end 20
```
- Should see only 6-8 IDs now (one per motor)
- Test each motor works

---

## 📞 Next Steps

**Right Now:**
1. ✅ Visual C++ download opened (install it)
2. ⏳ Restart computer after installation
3. ⏳ Try opening Motor Studio again

**After Motor Studio Opens:**
1. Identify motors first (Python tool)
2. Connect USB-to-CAN to Windows
3. Configure motors in Motor Studio
4. Test on Jetson

**If Motor Studio Still Fails:**
1. Try Python configuration tool
2. Or use motors with current IDs (works fine!)

---

**Current Status:** Waiting for you to install Visual C++ Redistributables and restart.

Let me know when you've installed it and restarted, then we'll open Motor Studio!

