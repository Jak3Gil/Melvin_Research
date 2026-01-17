# RobStride Motor Configuration Guide

**Status:** Motors are moving! ✅  
**Issue:** Motors need proper configuration for single ID operation

---

## 🎯 Goal

Configure each motor to respond to a **single, unique CAN ID** instead of multiple IDs.

Currently:
- 32 IDs are responding (8-31, 72-79)
- Multiple IDs likely map to the same physical motor
- Need to assign one ID per motor

---

## 🛠️ Tools Available

### 1. RobStride Motor Studio (Windows)

**Location:** `c:\Users\Owner\Downloads\Studio (2)\Studio\`

Two versions available:
- **17nm motors:** `motor_tool.exe` (in `17nm上位机` folder)
- **120nm motors:** `z1_motor_tool.exe` (in `120nm上位机` folder)

### 2. Motor Studio Driver

**Location:** `c:\Users\Owner\Downloads\motorstudio0.0.8\motorstudio0.0.8\driver.exe`

### 3. USB-to-CAN Adapter Firmware

**Location:** `c:\RobStride_Flash\`
- CANable firmware
- candleLight firmware

### 4. Product Documentation

**Location:** `c:\RobStride_Flash\Product_Information-main\`
- Motor specifications (RS00-RS06)
- Chinese and English manuals
- STEP files for CAD

---

## 📋 Configuration Steps

### Step 1: Identify Your Motor Models

Check which RobStride motors you have:
- **RS00** - Small motor (17Nm)
- **RS01** - Medium motor (30Nm)
- **RS02** - Medium-large motor (60Nm)
- **RS03** - Large motor (90Nm)
- **RS04** - Extra large motor (120Nm)
- **RS05** - High torque motor
- **RS06** - High speed motor

**Action:** Look at the motor labels or check documentation

### Step 2: Run Motor Studio on Windows

Since Motor Studio is a Windows application, you'll need to:

1. **Connect USB-to-CAN adapter to Windows PC**
   - Unplug from Jetson temporarily
   - Plug into Windows computer

2. **Install CH341 USB Driver** (if needed)
   ```
   Location: c:\RobStride_Flash\Product_Information-main\CH341SER.exe
   ```

3. **Run appropriate Motor Studio:**
   - For 17Nm motors: Run `motor_tool.exe`
   - For 120Nm motors: Run `z1_motor_tool.exe`

### Step 3: Configure Each Motor

In Motor Studio:

1. **Scan for motors**
   - Click "Scan" or "Search Motors"
   - Should find all connected motors

2. **Select a motor**
   - Click on motor in list

3. **Change CAN ID**
   - Find "CAN ID" or "Motor ID" setting
   - Set to unique ID (e.g., 1, 2, 3, 4, etc.)
   - Save/Apply settings

4. **Verify**
   - Motor should now only respond to new ID
   - Test by scanning again

5. **Repeat for each motor**
   - Assign sequential IDs: 1, 2, 3, 4, 5, etc.

### Step 4: Document Motor Mapping

Create a map of which physical motor has which ID:

| Motor Location | Physical Description | CAN ID | Notes |
|----------------|---------------------|--------|-------|
| Left Shoulder | Large joint motor | 1 | RS03 |
| Left Elbow | Medium motor | 2 | RS02 |
| Right Shoulder | Large joint motor | 3 | RS03 |
| ... | ... | ... | ... |

---

## 🔧 Alternative: Configure via Python Script

If Motor Studio doesn't work, you can configure motors programmatically:

### Create Configuration Script

```python
#!/usr/bin/env python3
"""Configure motor to single CAN ID"""
import serial
import time

def configure_motor_id(ser, old_id, new_id):
    """
    Configure a motor to respond to a new CAN ID
    
    Args:
        ser: Serial port object
        old_id: Current CAN ID motor responds to
        new_id: New CAN ID to assign
    """
    print(f"Configuring motor from ID {old_id} to ID {new_id}...")
    
    # Enable motor
    cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, old_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(cmd)
    time.sleep(0.2)
    
    # Send ID change command (this is a guess - may need Motor Studio)
    # Command format: AT + 0x30 + old_id + new_id
    cmd = bytes([0x41, 0x54, 0x30, 0x07, 0xe8, old_id, 0x08, 0x00,
                 new_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    ser.write(cmd)
    time.sleep(0.5)
    
    # Verify new ID
    cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, new_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.2)
    response = ser.read(100)
    
    if len(response) > 0:
        print(f"✓ Motor now responds to ID {new_id}")
        return True
    else:
        print(f"✗ Failed to configure motor")
        return False

# Usage
ser = serial.Serial('/dev/ttyUSB1', 921600, timeout=0.5)

# Example: Configure motor currently at ID 21 to ID 3
configure_motor_id(ser, old_id=21, new_id=3)

ser.close()
```

**Note:** The exact command for changing motor ID may vary. Motor Studio is the recommended method.

---

## 📊 Current Motor Status

From our scan, we found:

### Range 1: IDs 8-31 (24 IDs responding)
These likely represent 3-6 physical motors responding to multiple IDs each.

### Range 2: IDs 72-79 (8 IDs responding)
These likely represent 1-2 physical motors.

### Estimated Physical Motors: 4-8 motors total

---

## 🎯 Recommended ID Assignment

After configuration, use this ID scheme:

| Motor Function | Recommended ID | Notes |
|----------------|----------------|-------|
| Left Shoulder Pan | 1 | |
| Left Shoulder Pitch | 2 | |
| Left Elbow | 3 | |
| Left Wrist | 4 | |
| Right Shoulder Pan | 5 | |
| Right Shoulder Pitch | 6 | |
| Right Elbow | 7 | |
| Right Wrist | 8 | |
| Head Pan | 9 | |
| Head Tilt | 10 | |
| Waist | 11 | |
| Additional motors | 12+ | |

---

## 📝 Configuration Checklist

- [ ] Identify motor models (RS00-RS06)
- [ ] Install CH341 USB driver on Windows
- [ ] Connect USB-to-CAN to Windows PC
- [ ] Run appropriate Motor Studio (17nm or 120nm)
- [ ] Scan for motors in Motor Studio
- [ ] Configure each motor to unique ID
- [ ] Test each motor individually
- [ ] Document motor ID mapping
- [ ] Reconnect to Jetson
- [ ] Verify configuration with scan script

---

## 🚀 Quick Test After Configuration

Once motors are configured:

```bash
# On Jetson
ssh melvin@192.168.1.119

# Scan for motors (should see fewer IDs now)
python3 scan_all_motors_wide.py /dev/ttyUSB1 921600 --start 1 --end 20

# Test specific motor
python3 quick_motor_test.py /dev/ttyUSB1 921600 1

# Use Python interface
python3 jetson_motor_interface.py
```

---

## 📚 Resources

### Documentation
- Motor manuals: `c:\RobStride_Flash\Product_Information-main\Product Literature\`
- Chinese manuals: `c:\RobStride_Flash\Product_Information-main\产品资料\`

### Tools
- Motor Studio (17nm): `c:\Users\Owner\Downloads\Studio (2)\Studio\...\motor_tool.exe`
- Motor Studio (120nm): `c:\Users\Owner\Downloads\Studio (2)\Studio\...\z1_motor_tool.exe`
- Driver: `c:\Users\Owner\Downloads\motorstudio0.0.8\motorstudio0.0.8\driver.exe`
- USB Driver: `c:\RobStride_Flash\Product_Information-main\CH341SER.exe`

---

## ⚠️ Important Notes

1. **Backup Current Configuration**
   - Document current IDs before changing
   - Take photos of Motor Studio settings

2. **One Motor at a Time**
   - Configure motors individually
   - Test after each configuration

3. **Power Cycle**
   - May need to power cycle motors after ID change
   - Unplug power, wait 5 seconds, plug back in

4. **Windows Required**
   - Motor Studio only runs on Windows
   - Need to temporarily move USB adapter to Windows PC

5. **CAN Termination**
   - Ensure CAN bus has proper termination resistors
   - Usually 120Ω at each end of bus

---

## 🔍 Troubleshooting

### Motor Studio Won't Connect
- Install CH341SER.exe driver
- Check COM port in Device Manager
- Try different USB port
- Restart Motor Studio

### Can't Change Motor ID
- Ensure motor is enabled first
- Check if motor is in configuration mode
- Try power cycling motor
- Consult motor manual for specific model

### Multiple Motors Same ID
- This shouldn't happen after proper configuration
- If it does, reconfigure one motor at a time
- Disconnect other motors while configuring

---

## 📞 Next Steps

1. **Run Motor Studio on Windows**
   - Connect USB-to-CAN to Windows
   - Launch appropriate motor_tool.exe
   - Scan and identify motors

2. **Configure IDs**
   - Assign unique ID to each motor
   - Test each motor after configuration

3. **Return to Jetson**
   - Reconnect USB-to-CAN to Jetson
   - Run scan to verify new IDs
   - Update your motor control code with new IDs

4. **Create Motor Map**
   - Document which ID controls which physical motor
   - Use pulse_motor() to identify each one
   - Create reference diagram

---

**Status:** Ready to configure motors with Motor Studio! 🎉

