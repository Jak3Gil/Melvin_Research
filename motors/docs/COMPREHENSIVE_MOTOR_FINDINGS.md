# Comprehensive Motor Investigation Results
**Date:** January 10, 2026  
**Platform:** NVIDIA Jetson (melvin@192.168.1.119)  
**Connection:** /dev/ttyUSB0 (L91 Protocol, 921600 baud)

## 🎯 Executive Summary

**Found:** 5 physical motors responding  
**Missing:** 10 motors (if you have 15 total)  
**Protocol:** L91 via USB-to-Serial adapter  
**CAN Interfaces:** can0 and can1 exist but motors NOT connected to them

---

## 📊 Complete Scan Results

### ✅ Motors Found via L91 Protocol (/dev/ttyUSB0)

**48 CAN IDs responding** across 2 ranges:

#### Range 1: IDs 8-39 (32 IDs)
- IDs 8-15 (8 IDs)
- IDs 16-20 (5 IDs)
- IDs 21-30 (10 IDs)
- IDs 31-39 (9 IDs)

#### Range 2: IDs 64-79 (16 IDs)
- IDs 64-71 (8 IDs)
- IDs 72-79 (8 IDs)

### 🎯 Physical Motor Mapping (from visual test)

Based on unique pulse patterns:

| Test | CAN ID | Pulses | Physical Motor | Status |
|------|--------|--------|----------------|--------|
| 1 | 8 | 1 | Motor 1 | ✅ Moved |
| 2 | 16 | 2 | Motor 2 | ✅ Moved |
| 3 | 21 | 3 | Motor 3 | ✅ Moved |
| 4 | 31 | 4 | ??? | ✅ Moved (same as M2 or M3?) |
| 5 | 64 | 5 | Motor 8 | ✅ Moved |
| 6 | 72 | 6 | Motor 9 | ✅ Moved |

**Result:** Only **5 unique motors** moved during tests.

### ❌ Not Found

**Scanned ranges with NO response:**
- IDs 1-7 (not responding)
- IDs 40-63 (not responding)
- IDs 80-127 (not responding)
- IDs 128-255 (not responding)

---

## 🔍 Key Findings

### 1. Multiple CAN IDs per Motor ⚠️

Each physical motor responds to **8-10 consecutive CAN IDs**:
- Motor 1: IDs 8-15 (8 IDs → 1 motor)
- Motor 2: IDs 16-20 (5 IDs → 1 motor) + possibly 31-39
- Motor 3: IDs 21-30 (10 IDs → 1 motor)
- Motor 8: IDs 64-71 (8 IDs → 1 motor)
- Motor 9: IDs 72-79 (8 IDs → 1 motor)

**This is NOT normal.** Each motor should have ONE unique CAN ID.

### 2. Protocol Analysis

**L91 Protocol (Current Setup):**
- ✅ Working via /dev/ttyUSB0
- ✅ 5 motors responding
- ✅ AT command format
- ❌ Multiple IDs per motor
- ❌ 10 motors missing

**Direct CAN Protocol (can0/can1):**
- ✅ Interfaces exist and are UP
- ✅ Configured at 500kbps
- ❌ NO motors found on can0
- ❌ NO motors found on can1
- 💡 Motors NOT connected to direct CAN

### 3. RobStride Library

**Installation:**
- ✅ Library cloned successfully
- ✅ Dependencies installed
- ❌ Requires Python 3.10+ (Jetson has 3.8)
- ❌ Cannot use official library

### 4. CAN Interface Status

```
can0: UP, 500kbps, ERROR-ACTIVE
can1: UP, 500kbps, ERROR-ACTIVE
```

Both interfaces are active but **motors are NOT connected to them**.

---

## 🤔 Why Are 10 Motors Missing?

### Theory 1: Motors Not Powered/Connected (Most Likely)
- Only 5 motors are physically powered on
- Other 10 motors are:
  - Not connected to CAN bus
  - Not powered
  - On different CAN segment

### Theory 2: Motors Not Configured (Likely)
- 5 motors have been configured to respond to L91 protocol
- 10 motors still at factory defaults
- Need individual configuration

### Theory 3: Different Connection Method
- 5 motors connected via USB-to-CAN adapter (/dev/ttyUSB0)
- 10 motors might need direct CAN connection (can0/can1)
- But direct CAN scan found nothing

### Theory 4: Hardware Issue
- CAN bus termination problem
- Wiring issue affecting some motors
- Power distribution issue

---

## 🎯 Root Cause Analysis

### The Multiple-IDs-Per-Motor Problem

**Why does Motor 1 respond to IDs 8-15?**

Possible explanations:

1. **Factory Default Behavior**
   - Motors shipped with default firmware
   - Respond to ID ranges instead of single IDs
   - Need configuration to set unique ID

2. **Broadcast Mode**
   - Motors in "unconfigured" state
   - Accepting commands from multiple IDs
   - Need to be put in configuration mode

3. **Firmware Grouping**
   - Motors grouped by position/function
   - Each group responds to ID range
   - Intentional design (unlikely)

4. **L91 Adapter Behavior**
   - USB-to-CAN adapter translating IDs
   - Adapter firmware causing ID multiplication
   - Check adapter documentation

---

## ✅ What We Know For Sure

1. **5 physical motors are working** via /dev/ttyUSB0
2. **48 CAN IDs respond** but control only 5 motors
3. **L91 protocol is working** for these 5 motors
4. **Direct CAN (can0/can1) has no motors** connected
5. **No motors found** in IDs 40-63, 80-255
6. **Motors are NOT individually configured** with unique IDs

---

## 🛠️ Solutions & Next Steps

### Solution 1: Find the Missing 10 Motors

**Physical Check:**
```bash
# Check if all 15 motors are:
1. Powered on (LED indicators?)
2. Connected to CAN bus (CAN-H, CAN-L wiring)
3. Properly terminated (120Ω resistors at bus ends)
```

**Wiring Verification:**
- Trace CAN bus from adapter to each motor
- Check for loose connections
- Verify daisy-chain continuity

### Solution 2: Configure Motors with Unique IDs

**Option A: Use Manufacturer Software**
- RobStride Motor Studio (if available)
- Connect motors one at a time
- Assign unique IDs (1-15)

**Option B: Configuration Commands**
Your `remap_motor_ids.py` attempts this, but commands may not be correct.

**Option C: Hardware Configuration**
- Check for DIP switches on motor controllers
- Check for jumpers for ID selection

### Solution 3: Reconfigure CAN Bus

**Try different bitrate:**
```bash
# Stop current CAN
sudo ip link set can0 down

# Try 1Mbps (RobStride standard)
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up

# Rescan
python3 scan_can_direct.py
```

### Solution 4: Use Hybrid Approach

**For the 5 working motors:**
- Continue using L91 protocol via /dev/ttyUSB0
- Use current scripts (scan_robstride_motors.py, etc.)
- Control via CAN IDs: 8, 16, 21, 64, 72

**For the 10 missing motors:**
- Find them first (physical check)
- Determine if they need different connection
- Configure with unique IDs

---

## 📝 Recommended Action Plan

### Immediate Actions (Do First)

1. **Physical Inspection**
   - Count how many motors are actually powered on
   - Check LED indicators on each motor
   - Verify all motors are connected to CAN bus

2. **Verify Motor Count**
   - Do you actually have 15 motors?
   - Or only 5 motors with multiple ID responses?

3. **Check CAN Bus Wiring**
   - Verify daisy-chain connections
   - Check termination resistors (120Ω at each end)
   - Test continuity of CAN-H and CAN-L

### Short-term Actions

4. **Test ID 31 Again**
   - Determine which motor moved during Test 4
   - This tells us about ID range overlaps

5. **Try Configuration Commands**
   - Attempt to configure Motor 1 to respond only to ID 1
   - See if `remap_motor_ids.py` works

6. **Contact Manufacturer**
   - Ask RobStride about:
     - Why motors respond to multiple IDs
     - How to configure unique IDs
     - L91 protocol documentation

### Long-term Solution

7. **Reconfigure All Motors**
   - Set each motor to unique ID (1-15)
   - One ID per motor
   - Test each motor individually

8. **Consider Direct CAN**
   - If L91 is causing issues
   - Connect motors to can0/can1 directly
   - Upgrade Python to 3.10+ for RobStride library

---

## 🎓 Technical Details

### L91 Protocol Command Format

```
AT <cmd> <addr_high> <addr_low> <can_id> <data> \r\n
```

**Example - Activate Motor 8:**
```
41 54 00 07 e8 08 01 00 0d 0a
AT    00 07 e8 08 01 00 \r \n
```

### Variables in Motor Communication

1. **CAN ID** (0x08-0xFF)
   - Target motor identifier
   - Currently: multiple IDs per motor

2. **Base Address** (0x07e8)
   - For USB-to-CAN adapter
   - Not used by motors directly

3. **Command Byte** (0x00, 0x20, 0x90)
   - 0x00 = Activate
   - 0x20 = Load parameters
   - 0x90 = Move/jog

4. **Protocol Type**
   - L91 (serial AT commands)
   - Direct CAN (SocketCAN)

---

## 📚 Resources

- RobStride Control: https://github.com/Seeed-Projects/RobStride_Control
- RobStride Wiki: https://wiki.seeedstudio.com/robstride_control/
- Your scripts: `scan_all_motors_wide.py`, `test_all_ranges_auto.py`

---

## 🎯 Bottom Line

**You have 5 motors working, but they're not properly configured.**

Each motor responds to 8-10 CAN IDs instead of 1 unique ID. The other 10 motors are either:
- Not powered/connected
- Need different configuration
- On different CAN segment

**Next step:** Physical inspection to verify how many motors are actually powered and connected.

