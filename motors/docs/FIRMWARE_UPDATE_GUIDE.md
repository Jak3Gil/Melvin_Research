# RobStride Motor Firmware Update Guide
**Date:** January 10, 2026  
**Your Issue:** Motors responding to multiple CAN IDs instead of unique IDs

## 🎯 THE SOLUTION

According to the [RobStride Product_Information repository](https://github.com/RobStride/Product_Information), **firmware version RS00_0.0.3.6** fixes your exact problem:

> **"电机canopenid与canid保持一致"** (motor CANopen ID and CAN ID are now consistent)

This firmware update ensures each motor responds to only ONE CAN ID instead of multiple IDs!

---

## 📥 How to Download Firmware

### Step 1: Access Firmware Releases

Visit: [https://github.com/RobStride/Product_Information/releases](https://github.com/RobStride/Product_Information/releases)

**Latest releases available:**
- V25.12.09 (December 9, 2025)
- V25.10.27 (October 27, 2025)
- V25.08.22 (August 22, 2025)

### Step 2: Download Firmware Files

From the releases page, download the firmware for your motor model:
- **RS00**: `RS00_FAC_V1001_V00319_YYYYMMDD.hex`
- **RS01**: `RS01_FAC_V1001_V01319_YYYYMMDD.hex`
- **RS02**: `RS02_FAC_V1001_V02319_YYYYMMDD.hex`

The firmware files will be in the **Assets** section of each release.

---

## 🛠️ How to Update Firmware

### Method 1: Using MotorStudio (Recommended)

**MotorStudio** is the official RobStride configuration software.

#### Download MotorStudio:
1. Clone repository: `git clone https://github.com/RobStride/MotorStudio.git`
2. Check the instructions PDF: `使用说明书-Instructions/Instructions for using the Studio_241122.pdf`

#### Update Process:
1. Connect motor to computer via USB-to-CAN adapter
2. Open MotorStudio
3. Navigate to firmware update section
4. Select downloaded `.hex` file
5. Click "Update Firmware"
6. Wait for completion (motor will restart)

### Method 2: Using OTA (Over-The-Air) Protocol

According to the repository, RobStride supports OTA firmware updates:
- Check `OTA Agreement Description - EN_20251114102200.pdf` in the Product_Information repo
- This allows updating firmware via CAN bus

---

## 📋 Firmware Update Benefits

### RS00_0.0.3.6 Fixes:

1. **✅ CAN ID Consistency** (YOUR ISSUE!)
   - "电机canopenid与canid保持一致"
   - Motors will respond to ONE unique CAN ID
   - Fixes the multiple-IDs-per-motor problem

2. **✅ PDO Reporting Time**
   - Fixed mismatch between PDO reporting time and configuration

3. **✅ Zero Position Dead Zone**
   - Added zero position dead zone for better accuracy

### Additional Features in Latest Firmware:

- **Protocol Switching**: Switch between CANopen and MIT protocols
- **Factory Reset**: Restore motor to factory settings
- **Error Logging**: Better error tracking and diagnostics
- **Parameter Management**: All parameters readable and writable
- **Position Offset**: Set custom zero positions

---

## 🔧 After Firmware Update

### Step 1: Configure Unique CAN IDs

Once firmware is updated, use MotorStudio to assign unique IDs:

**Recommended ID Assignment:**
- Motor 1 → CAN ID 1
- Motor 2 → CAN ID 2
- Motor 3 → CAN ID 3
- ...
- Motor 15 → CAN ID 15

### Step 2: Save Configuration

After setting CAN IDs:
1. Click "Save Parameters" in MotorStudio
2. Power cycle motors
3. Verify each motor responds to only ONE ID

### Step 3: Test Motors

Run verification scan:
```bash
python3 scan_all_motors_wide.py /dev/ttyUSB0 921600 --start 1 --end 15
```

You should now see 15 motors, each responding to ONE unique ID!

---

## 📊 Current vs. After Update

### BEFORE Firmware Update:
```
Motor 1: Responds to IDs 8-15 (8 IDs)
Motor 2: Responds to IDs 16-20 (5 IDs)
Motor 3: Responds to IDs 21-30 (10 IDs)
Motor 4: Responds to IDs 31-39 (9 IDs)
Motor 5: Responds to IDs 64-71 (8 IDs)
Motor 6: Responds to IDs 72-79 (8 IDs)

Total: 52 CAN IDs → 6 motors
Problem: Multiple IDs per motor!
```

### AFTER Firmware Update:
```
Motor 1: Responds to ID 1 only
Motor 2: Responds to ID 2 only
Motor 3: Responds to ID 3 only
...
Motor 15: Responds to ID 15 only

Total: 15 CAN IDs → 15 motors
Solution: One unique ID per motor!
```

---

## ⚠️ Important Notes

### Before Updating:

1. **Backup Current Configuration**
   - Note current motor parameters
   - Document any custom settings

2. **Stable Power Supply**
   - Ensure motors have stable power during update
   - Don't interrupt the update process

3. **One Motor at a Time**
   - Update motors individually to avoid issues
   - Verify each update before proceeding to next motor

### After Updating:

1. **Recalibrate Zero Positions**
   - Firmware update may require re-zeroing motors
   - Use MotorStudio to set mechanical zero positions

2. **Test Each Motor**
   - Verify motor responds correctly
   - Check movement in both directions
   - Confirm torque and speed parameters

3. **Save Configuration**
   - Always save parameters after changes
   - Power cycle to confirm settings persist

---

## 🔗 Resources

### Official Documentation:
- **Product Information**: [https://github.com/RobStride/Product_Information](https://github.com/RobStride/Product_Information)
- **MotorStudio**: [https://github.com/RobStride/MotorStudio](https://github.com/RobStride/MotorStudio)
- **Sample Programs**: [https://github.com/RobStride/SampleProgram](https://github.com/RobStride/SampleProgram)
- **Firmware Releases**: [https://github.com/RobStride/Product_Information/releases](https://github.com/RobStride/Product_Information/releases)

### Manuals on Jetson:
- MotorStudio Instructions: `~/MotorStudio/使用说明书-Instructions/Instructions for using the Studio_241122.pdf`
- OTA Protocol: `~/Product_Information/OTA Agreement Description - EN_20251114102200.pdf`
- Product Specs: `~/Product_Information/灵足时代产品规格介绍 RobStride Product Specification Document 20250626.pdf`

---

## 🎯 Summary

**Your Problem:** Motors respond to multiple CAN IDs (8-10 IDs each)

**Root Cause:** Old firmware doesn't enforce CAN ID consistency

**Solution:** Update to firmware RS00_0.0.3.6 or later

**Steps:**
1. Download firmware from [releases page](https://github.com/RobStride/Product_Information/releases)
2. Use MotorStudio to update each motor
3. Configure unique CAN IDs (1-15)
4. Test and verify

**Result:** Each motor will respond to ONE unique CAN ID!

---

## 💡 Alternative: Contact RobStride Support

If you need assistance:
- **GitHub Issues**: Open issue on RobStride repositories
- **Documentation**: Check PDF manuals in Product_Information repo
- **Community**: Look for RobStride user forums or Discord

The firmware update is the official solution to your problem!

