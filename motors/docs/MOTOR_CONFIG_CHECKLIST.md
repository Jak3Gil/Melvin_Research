# Motor Reconfiguration Checklist

## ✅ Completed
- [x] Connected to Jetson
- [x] Found motors (48 IDs responding)
- [x] Motors are moving
- [x] Created Python tools for motor control
- [x] Opened Visual C++ Redistributables download

---

## ⏳ To Do Now

### 1. Install Visual C++ Redistributables
- [ ] Download vc_redist.x64.exe (should be downloading now)
- [ ] Run the installer
- [ ] Click "Install"
- [ ] **Restart your computer** (important!)

### 2. Test Motor Studio
- [ ] After restart, run: `.\launch_motor_studio.bat`
- [ ] Or double-click motor_tool.exe in File Explorer
- [ ] Verify it opens without Qt5Core.dll error

### 3. Identify Motors (Before Reconfiguring!)
- [ ] SSH to Jetson: `ssh -t melvin@192.168.1.119`
- [ ] Run: `python3 identify_motors_interactive.py`
- [ ] Test each motor and note which physical motor it is
- [ ] Save the motor_map.txt file

### 4. Prepare for Reconfiguration
- [ ] Unplug USB-to-CAN from Jetson
- [ ] Plug USB-to-CAN into Windows PC
- [ ] Check Device Manager for COM port number
- [ ] Keep motors powered on

### 5. Reconfigure in Motor Studio
- [ ] Open Motor Studio
- [ ] Select COM port
- [ ] Set baud rate: 921600
- [ ] Click "Connect"
- [ ] Click "Scan" to find motors
- [ ] For each motor:
  - [ ] Select motor
  - [ ] Change CAN ID to new unique ID (1, 2, 3, etc.)
  - [ ] Click "Save" or "Write"
  - [ ] Verify change

### 6. Verify Configuration
- [ ] Plug USB-to-CAN back into Jetson
- [ ] SSH to Jetson
- [ ] Run: `python3 scan_all_motors_wide.py /dev/ttyUSB1 921600 --start 1 --end 20`
- [ ] Should see only 6-8 IDs (one per motor)
- [ ] Test each motor: `python3 quick_motor_test.py /dev/ttyUSB1 921600 1`

---

## 📋 Motor ID Assignment Plan

Fill this out during identification:

| Current ID(s) | Physical Motor Location | New ID |
|---------------|------------------------|--------|
| 8-15          | _________________      | 1      |
| 16-23         | _________________      | 2      |
| 24-31         | _________________      | 3      |
| 32-39         | _________________      | 4      |
| 64-71         | _________________      | 5      |
| 72-79         | _________________      | 6      |

---

## 🚨 Troubleshooting

### Motor Studio still won't open after installing Visual C++
- Try x86 version: https://aka.ms/vs/17/release/vc_redist.x86.exe
- Use Python tool: `python3 configure_motor_ids.py`
- Or keep current IDs (they work fine!)

### Can't identify which motor is which
- Test with stronger movement
- Watch carefully during pulse
- Try one motor at a time
- Mark motors with tape as you identify them

### ID change doesn't work in Motor Studio
- Try power cycling motor
- Check if motor is in configuration mode
- Some motors may need firmware update
- Use Python tool as backup

### Motors don't respond after reconfiguration
- Power cycle all motors
- Check CAN bus connections
- Verify new IDs were saved
- Rescan with wider range

---

## 📞 Current Step

**YOU ARE HERE:** 
→ Installing Visual C++ Redistributables

**NEXT:**
→ Restart computer
→ Try opening Motor Studio
→ If it opens: Identify motors, then reconfigure
→ If it doesn't: Use Python configuration tool

---

## 💡 Quick Commands Reference

```bash
# SSH to Jetson
ssh melvin@192.168.1.119

# Scan for motors
python3 scan_all_motors_wide.py /dev/ttyUSB1 921600 --start 1 --end 127

# Identify motors
python3 identify_motors_interactive.py

# Test specific motor
python3 quick_motor_test.py /dev/ttyUSB1 921600 8

# Configure motor IDs (if Motor Studio fails)
python3 configure_motor_ids.py

# Run motor interface demo
python3 jetson_motor_interface.py
```

---

**Status:** Waiting for Visual C++ installation and computer restart.

