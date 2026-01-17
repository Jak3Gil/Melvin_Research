# Finding All 15 Motors - Troubleshooting Guide

## Current Situation

**Expected:** 15 physical motors  
**Found:** 6 motor groups (48 IDs total)  
**At baud rate:** 921600

### Motor Groups Found:
1. IDs 8-15 (8 IDs) → Motor 1
2. IDs 16-23 (8 IDs) → Motor 2
3. IDs 24-31 (8 IDs) → Motor 3
4. IDs 32-39 (8 IDs) → Motor 4
5. IDs 64-71 (8 IDs) → Motor 5
6. IDs 72-79 (8 IDs) → Motor 6

**Missing: 9 motors**

---

## 🔍 Most Likely Causes

### 1. **Not All Motors Powered On** ⭐⭐⭐ MOST LIKELY

**Check right now:**
- Go to your robot
- Count motors with LED lights ON
- If only 6 have LEDs on → that's your answer!
- The other 9 need power

**Solution:** Turn on power to all 15 motors

### 2. **Motors in Standby/Sleep Mode** ⭐⭐

Some motors might be in low-power mode and not responding to scans.

**Solution:** Send a "wake up" broadcast command

### 3. **Different CAN Network** ⭐

The 9 missing motors might be:
- On a completely separate CAN network
- Not connected to the USB-to-CAN adapter
- Connected to a different controller

**Check:** Are all 15 motors wired to the same CAN bus?

### 4. **Motors Not Configured Yet**

The 9 motors might be brand new and need initial configuration before they respond.

**Solution:** Use Motor Studio to initialize them

---

## 🚀 Action Plan

### Step 1: Physical Inspection (DO THIS FIRST!)

**Count powered motors:**
```
Go to robot → Count motors with LED ON → Write down the number
```

**If you see 6 LEDs ON:**
- That matches our scan results!
- Turn on power to the other 9 motors
- Rescan

**If you see 15 LEDs ON:**
- All motors have power
- Problem is communication/configuration
- Continue to Step 2

### Step 2: Wake Up All Motors

Some motors might be in standby. Let's wake them up:

```bash
ssh melvin@192.168.1.119
python3 wake_up_motors.py
```

This sends broadcast wake-up commands.

### Step 3: Test Individual IDs

Maybe the motors ARE there but at different IDs:

```bash
# Test IDs 40-63 (gap between our groups)
python3 quick_motor_test.py /dev/ttyUSB1 921600 40
python3 quick_motor_test.py /dev/ttyUSB1 921600 50
python3 quick_motor_test.py /dev/ttyUSB1 921600 60

# Test IDs 80-127
python3 quick_motor_test.py /dev/ttyUSB1 921600 80
python3 quick_motor_test.py /dev/ttyUSB1 921600 100
python3 quick_motor_test.py /dev/ttyUSB1 921600 120
```

### Step 4: Check CAN Wiring

**Questions to answer:**
1. Are all 15 motors connected to the SAME CAN bus?
2. Or are they split across multiple buses?
3. Does your robot have multiple CAN networks?

**Common robot configurations:**
- **Single bus:** All motors on one CAN-H/CAN-L pair
- **Dual bus:** Arms on one bus, legs on another
- **Multiple buses:** Different body parts on different buses

### Step 5: Use Motor Studio

Motor Studio can:
- Scan multiple interfaces simultaneously
- Find motors in configuration mode
- Initialize brand new motors
- Show motors that don't respond to Python scans

**Once you fix the Qt5 issue:**
1. Install Visual C++ Redistributables
2. Restart computer
3. Open Motor Studio
4. Scan all interfaces
5. Should find all 15 motors

---

## 💡 Quick Tests You Can Do Right Now

### Test 1: Count LEDs
```
Physical inspection: How many motors have LED lights ON?
Answer: _____ motors
```

### Test 2: Test Gap IDs
```bash
ssh melvin@192.168.1.119

# Test the gap between our groups (40-63)
for id in 40 45 50 55 60; do
  echo "Testing ID $id..."
  python3 quick_motor_test.py /dev/ttyUSB1 921600 $id
  sleep 1
done
```

### Test 3: Test High IDs
```bash
# Test higher IDs (80-127)
for id in 80 90 100 110 120; do
  echo "Testing ID $id..."
  python3 quick_motor_test.py /dev/ttyUSB1 921600 $id
  sleep 1
done
```

### Test 4: Broadcast Wake-Up
```bash
python3 wake_up_motors.py
# Then rescan
python3 scan_all_motors_wide.py /dev/ttyUSB1 921600 --start 1 --end 127
```

---

## 🎯 My Best Guess

Based on typical robotics setups:

**Scenario A: Power Issue (90% probability)**
- Only 6 motors are powered on right now
- The other 9 need power turned on
- Check your power distribution board
- Verify all power connections

**Scenario B: Multiple CAN Buses (8% probability)**
- 6 motors on USB-to-CAN bus
- 9 motors on a different CAN network
- Need to connect to the other bus

**Scenario C: Configuration Issue (2% probability)**
- 9 motors are new/unconfigured
- Need Motor Studio to initialize them
- They won't respond until configured

---

## 📋 Checklist

- [ ] **Count motors with LED ON** (most important!)
- [ ] Test IDs in gap range (40-63)
- [ ] Test high IDs (80-127)
- [ ] Run wake_up_motors.py
- [ ] Check CAN bus wiring diagram
- [ ] Verify power to all 15 motors
- [ ] Check if motors split across multiple buses
- [ ] Try Motor Studio (after fixing Qt5)

---

## 🔧 If You Find the Missing Motors

Once you locate all 15 motors:

1. **Document their IDs:**
   ```bash
   python3 identify_motors_interactive.py
   ```

2. **Reconfigure to single IDs:**
   - Use Motor Studio (recommended)
   - Or use configure_motor_ids.py

3. **Test all 15 motors:**
   ```bash
   python3 jetson_motor_interface.py
   ```

---

## 📞 Next Step

**RIGHT NOW: Count the motors with LED lights ON**

This single check will tell us if it's:
- Power issue (6 LEDs = only 6 powered)
- Communication issue (15 LEDs = all powered but not responding)

**How many motors have LED lights ON right now?**

