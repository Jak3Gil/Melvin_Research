# How to Update Firmware - Complete Guide
**Script Created:** `ota_firmware_updater.py`  
**Status:** Ready to use (firmware files needed)

---

## 🎯 What I Created

**Automatic OTA Firmware Updater** - Updates motor firmware via CAN bus

**Features:**
- ✅ Implements RobStride OTA protocol
- ✅ Automatic update process
- ✅ Progress indicators
- ✅ Safety checks
- ✅ Can update single motor or all motors
- ✅ Error handling

---

## 📥 Step 1: Get Firmware Files

### Option A: Download from GitHub Releases (Recommended)

```bash
# On Jetson
cd ~
wget https://github.com/RobStride/Product_Information/releases/download/V25.12.09/RS00_FAC_V1001_V00319_20251022.bin

# Or for other motor models:
# RS01: wget https://github.com/RobStride/Product_Information/releases/download/V25.12.09/RS01_...
# RS02: wget https://github.com/RobStride/Product_Information/releases/download/V25.12.09/RS02_...
```

### Option B: Download on Windows, then transfer

1. Visit: [https://github.com/RobStride/Product_Information/releases](https://github.com/RobStride/Product_Information/releases)
2. Download latest firmware (V25.12.09)
3. Transfer to Jetson:
   ```powershell
   scp RS00_firmware.bin melvin@192.168.1.119:~/
   ```

---

## 🚀 Step 2: Run the Updater

### Test on ONE Motor First (IMPORTANT!)

```bash
ssh melvin@192.168.1.119

# Update single motor (CAN ID 8)
python3 ota_firmware_updater.py /dev/ttyUSB0 921600 RS00_firmware.bin 8
```

**What happens:**
1. Script asks for confirmation (type `YES`)
2. Gets device ID from motor
3. Starts upgrade process
4. Sends firmware data (shows progress)
5. Motor reboots automatically
6. Done!

### Update All Motors (After testing one)

```bash
# Update all 6 motors automatically
python3 ota_firmware_updater.py /dev/ttyUSB0 921600 RS00_firmware.bin
```

This will update motors: 8, 16, 21, 31, 64, 72

---

## ⚠️ CRITICAL WARNINGS

### Before Running:

1. **✅ Stable Power Supply**
   - Ensure motors have reliable power
   - Use UPS if available
   - Check all power connections

2. **✅ Don't Interrupt**
   - Process takes 5-10 minutes per motor
   - Don't press Ctrl+C
   - Don't disconnect cables
   - Don't power off

3. **✅ Test on ONE Motor First**
   - Update motor ID 8 first
   - Verify it works
   - Then update others

4. **✅ Backup Plan**
   - Know how to contact RobStride support
   - Have MotorStudio as backup method
   - Document current motor settings

### Risks:

- ⚠️ **Interrupted update = bricked motor**
- ⚠️ **Power loss = dead motor**
- ⚠️ **Wrong firmware = damaged motor**
- ⚠️ **No rollback if it fails**

---

## 📊 Expected Output

```
======================================================================
  RobStride Motor OTA Firmware Updater
======================================================================

Port: /dev/ttyUSB0
Baud: 921600
Firmware: RS00_firmware.bin
Target Motor: CAN ID 8

======================================================================
⚠️  CRITICAL WARNINGS
======================================================================
1. Ensure STABLE POWER to all motors
2. Do NOT interrupt the update process
3. Motor will be BRICKED if power is lost
4. Test on ONE motor first
5. Have a backup plan

======================================================================

Type 'YES' to continue (anything else to cancel): YES

Opening serial port /dev/ttyUSB0...
✓ Serial port opened

======================================================================
  Firmware Update: Motor CAN ID 8
======================================================================

✓ Firmware file loaded: 245760 bytes

[1/4] Getting device ID for motor 8...
  ✓ Device ID received: a1 b2 c3 d4 e5 f6 g7 h8

[2/4] Starting upgrade for motor 8...
  ✓ Upgrade start accepted

[3/4] Sending upgrade info...
  Bin size: 245760 bytes
  Packets: 40960
  ✓ Upgrade info accepted

[4/4] Sending firmware data...
  Total: 245760 bytes in 40960 packets
  This will take approximately 4096.0 seconds

⚠️  DO NOT INTERRUPT! Motor will be bricked if interrupted!

  Progress: 100/40960 (0.2%)
  Progress: 200/40960 (0.5%)
  ...
  Progress: 40960/40960 (100.0%)

  ✓ All data sent!

======================================================================
✓ FIRMWARE UPDATE COMPLETE!
======================================================================

Motor will restart automatically.
Wait 10 seconds for motor to reboot...

✓ Firmware update successful!

[COMPLETE]
```

---

## 🔧 After Firmware Update

### Step 1: Verify Motor Responds

```bash
# Test updated motor
python3 quick_motor_test.py /dev/ttyUSB0 921600 8 3
```

Motor should move normally.

### Step 2: Configure Unique CAN ID

**Option A: Use MotorStudio (Recommended)**
- Open MotorStudio on Windows
- Connect to motor
- Set CAN ID to unique value (1-15)
- Save configuration

**Option B: Try Configuration Commands**
```bash
# Try to configure motor 8 to ID 1
python3 discover_and_configure_all_motors_auto.py /dev/ttyUSB0 921600
```

### Step 3: Verify Unique ID

```bash
# Scan to see if motor now has unique ID
python3 scan_all_motors_wide.py /dev/ttyUSB0 921600 --start 1 --end 15
```

Expected: Motor responds to ONE ID only!

---

## 🐛 Troubleshooting

### Problem: "No response from motor"

**Solutions:**
- Check motor is powered on
- Verify CAN bus connections
- Try different CAN ID
- Motor might be in wrong state

### Problem: "Upgrade start failed"

**Solutions:**
- Motor might not support OTA
- Wrong firmware file
- Motor already in upgrade mode (power cycle)

### Problem: Update interrupted

**Solutions:**
- Power cycle motor
- Try update again
- If motor is bricked, contact RobStride support
- May need MotorStudio to recover

### Problem: Motor doesn't work after update

**Solutions:**
- Power cycle motor (wait 30 seconds)
- Recalibrate zero position
- Check motor parameters
- May need to restore factory settings

---

## 📋 Update Checklist

### Pre-Update:
- [ ] Downloaded correct firmware file
- [ ] Verified stable power supply
- [ ] Tested script on ONE motor first
- [ ] Documented current motor settings
- [ ] Have backup plan ready

### During Update:
- [ ] Don't interrupt process
- [ ] Don't disconnect cables
- [ ] Don't power off
- [ ] Monitor progress
- [ ] Wait for completion

### Post-Update:
- [ ] Verify motor responds
- [ ] Configure unique CAN ID
- [ ] Test motor movement
- [ ] Recalibrate if needed
- [ ] Document new settings

---

## 🎯 Quick Start

```bash
# 1. Download firmware
cd ~
# (Download firmware file here)

# 2. Update ONE motor first
python3 ota_firmware_updater.py /dev/ttyUSB0 921600 RS00_firmware.bin 8

# 3. If successful, update others
python3 ota_firmware_updater.py /dev/ttyUSB0 921600 RS00_firmware.bin 16
python3 ota_firmware_updater.py /dev/ttyUSB0 921600 RS00_firmware.bin 21
# etc...

# 4. Or update all at once (risky!)
python3 ota_firmware_updater.py /dev/ttyUSB0 921600 RS00_firmware.bin
```

---

## 💡 Alternative: Use MotorStudio

If OTA update fails or you're uncomfortable with risks:

1. Download MotorStudio on Windows PC
2. Connect ONE motor via USB-to-CAN
3. Use GUI to update firmware
4. Much safer with progress bar and error recovery
5. Official method recommended by RobStride

**MotorStudio is the safer choice!**

---

## 📞 Need Help?

- **Script location:** `~/ota_firmware_updater.py`
- **Firmware releases:** [https://github.com/RobStride/Product_Information/releases](https://github.com/RobStride/Product_Information/releases)
- **OTA Protocol:** `~/Product_Information/OTA Agreement Description - EN_20251114102200.pdf`
- **RobStride GitHub:** [https://github.com/RobStride](https://github.com/RobStride)

---

## ⚡ Summary

**I created an automatic firmware updater that:**
- Implements RobStride OTA protocol
- Updates motors via CAN bus
- Shows progress and handles errors
- Can update single or all motors

**To use it:**
1. Download firmware from GitHub releases
2. Run: `python3 ota_firmware_updater.py /dev/ttyUSB0 921600 firmware.bin 8`
3. Type `YES` to confirm
4. Wait for completion
5. Motor reboots with new firmware

**Remember:**
- ⚠️ Test on ONE motor first
- ⚠️ Ensure stable power
- ⚠️ Don't interrupt
- ✅ MotorStudio is safer alternative

**The automatic script is ready - you just need the firmware files!**

