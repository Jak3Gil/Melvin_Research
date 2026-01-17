# RobStride Motor Configuration Guide
## Based on Official RobStride GitHub Repositories

**Date:** January 10, 2026  
**Source:** https://github.com/RobStride

---

## 📚 Available Resources from RobStride

### Official Repositories

1. **[Product_Information](https://github.com/RobStride/Product_Information)** ⭐
   - Product specifications
   - Firmware updates
   - Detailed documentation
   - **Most important for understanding motor capabilities**

2. **[SampleProgram](https://github.com/RobStride/SampleProgram)** ⭐⭐⭐
   - STM32 (HAL) control demo
   - `RobStride.h` / `RobStride01.cpp` motor library
   - Supports Lingzu private protocol and MIT protocol
   - **Contains actual motor control code**

3. **[MotorStudio](https://github.com/RobStride/MotorStudio)**
   - Motor configuration tool
   - GUI for motor setup
   - **Likely used for CAN ID configuration**

4. **[robstride_ros_sample](https://github.com/RobStride/robstride_ros_sample)**
   - ROS package for RobStride 02 actuator
   - For ROS-based projects

5. **[robstride_actuator_bridge](https://github.com/RobStride/robstride_actuator_bridge)**
   - ROS bridge for RobStride actuators
   - Forked from MuShibo's work

6. **[CAN-USB-data-conversion](https://github.com/RobStride/CAN-USB-data-conversion)**
   - CAN-USB data conversion utilities
   - May help with USB-to-CAN adapter communication

---

## 🎯 Do You Need ROS?

### **NO - ROS is NOT required!** ✅

Based on the RobStride repositories:

**You can control motors WITHOUT ROS using:**
- Python with CAN bus libraries (`python-can`)
- Direct CAN commands via USB-to-CAN adapter
- The protocols documented in SampleProgram

**ROS is only needed if:**
- You're building a complex robotic system
- You need sensor integration, navigation, or SLAM
- You're already using ROS for other components

---

## 🔧 Recommended Approach for Your Setup

### **Option 1: Python Direct Control (RECOMMENDED)** ⭐

**Advantages:**
- No ROS overhead
- Works on Jetson directly
- Can use existing USB-to-CAN adapter
- Simpler to implement and debug

**What you need:**
1. Study the `SampleProgram` repository for command formats
2. Implement the same commands in Python
3. Use `python-can` or direct serial communication

### **Option 2: Use MotorStudio for Configuration**

**Advantages:**
- Official tool from RobStride
- GUI for easy configuration
- Can set CAN IDs, parameters, etc.

**What you need:**
1. Download MotorStudio from the repository
2. Connect to motors via USB-to-CAN
3. Configure each motor with unique ID
4. Save configuration to motor firmware

### **Option 3: ROS Integration (if needed)**

**Only if you need ROS features:**
- Use `robstride_ros_sample` package
- Requires ROS installation on Jetson
- More complex setup

---

## 📖 Key Information from SampleProgram

### Supported Protocols

1. **Lingzu Private Protocol** (L91 - what you're using!)
2. **MIT Protocol** (alternative)

### Supported Control Modes

From the SampleProgram repository:
- ✅ Enable/Disable motor
- ✅ Position control
- ✅ Speed control
- ✅ Current control
- ✅ Torque control
- ✅ Parameter setting
- ✅ Zeroing
- ✅ **Protocol switching**
- ✅ **CAN ID configuration** (likely)

### CAN Bus Requirements

- **Baud Rate:** Must match motor settings (you're using 921600 ✓)
- **CAN ID:** Each motor should have unique ID
- **Termination:** 120Ω resistors at both ends

---

## 🔍 What We Need to Extract from Repositories

### Priority 1: Command Formats

From `SampleProgram/RobStride.h` and `RobStride01.cpp`:
- Exact command format for setting CAN ID
- Parameter configuration commands
- Protocol switching commands

### Priority 2: MotorStudio Usage

From `MotorStudio` repository:
- How to use the GUI tool
- Configuration file formats
- Command-line options (if any)

### Priority 3: Product Documentation

From `Product_Information`:
- Motor specifications
- Firmware version requirements
- Configuration procedures

---

## 💡 Next Steps

### Immediate Actions

**1. Download and Study SampleProgram** 🔥
```bash
# Clone the repository
git clone https://github.com/RobStride/SampleProgram.git

# Look for these files:
# - RobStride.h (header with command definitions)
# - RobStride01.cpp (implementation)
# - main.c (usage examples)
```

**2. Check MotorStudio Repository**
```bash
git clone https://github.com/RobStride/MotorStudio.git

# Look for:
# - Executable/binary
# - Documentation
# - Configuration file examples
```

**3. Review Product_Information**
```bash
git clone https://github.com/RobStride/Product_Information.git

# Look for:
# - User manuals
# - Command protocol documentation
# - Configuration guides
```

### Implementation Plan

**Phase 1: Extract Command Formats**
- Study the C++ code in SampleProgram
- Identify the command structure for:
  - Setting CAN ID
  - Reading motor parameters
  - Saving configuration

**Phase 2: Implement in Python**
- Create Python equivalents of the C++ commands
- Test on your existing 6 motors
- Verify configuration changes persist

**Phase 3: Configure All Motors**
- Use Python script or MotorStudio
- Assign unique IDs (1-6 or 1-15)
- Test each motor individually

---

## 🚀 Quick Start - What to Do NOW

### Step 1: Clone the Repositories

```bash
# On your Windows machine or Jetson
cd ~/robstride_research
git clone https://github.com/RobStride/SampleProgram.git
git clone https://github.com/RobStride/MotorStudio.git
git clone https://github.com/RobStride/Product_Information.git
```

### Step 2: Extract Key Files

Look for these critical files:
- `SampleProgram/RobStride.h` - Command definitions
- `SampleProgram/RobStride01.cpp` - Implementation
- `MotorStudio/` - Configuration tool
- `Product_Information/` - Documentation

### Step 3: Analyze Command Structure

Study how the C++ code sends commands:
```cpp
// Example from SampleProgram (hypothetical)
void setMotorID(uint8_t old_id, uint8_t new_id) {
    // Command format to change motor ID
    // This is what we need to find!
}
```

### Step 4: Create Python Implementation

Based on the C++ code, create Python equivalents:
```python
#!/usr/bin/env python3
"""
RobStride Motor Configuration - Python Implementation
Based on official SampleProgram repository
"""

import serial
import struct
import time

class RobStrideMotor:
    def __init__(self, port, baud=921600):
        self.ser = serial.Serial(port, baud, timeout=0.5)
        time.sleep(0.5)
    
    def set_motor_id(self, old_id, new_id):
        """
        Set motor CAN ID
        Command format to be extracted from SampleProgram
        """
        # TODO: Implement based on SampleProgram code
        pass
    
    def save_config(self, motor_id):
        """
        Save configuration to motor flash
        """
        # TODO: Implement based on SampleProgram code
        pass
```

---

## 📋 Summary

### What You DON'T Need:
- ❌ ROS (unless you want it for other reasons)
- ❌ Complex setup
- ❌ Additional hardware

### What You DO Need:
- ✅ Study the SampleProgram repository (command formats)
- ✅ Possibly use MotorStudio (configuration tool)
- ✅ Implement commands in Python (or use existing tools)
- ✅ Fix CAN bus hardware issues (termination, power)

### Critical Resources:
1. **SampleProgram** - Contains all command formats ⭐⭐⭐
2. **MotorStudio** - GUI tool for configuration ⭐⭐
3. **Product_Information** - Documentation ⭐

---

## 🎯 Expected Outcome

After studying these repositories, you should be able to:

1. **Configure motor CAN IDs** programmatically
2. **Set motor parameters** (limits, gains, etc.)
3. **Switch protocols** (L91 ↔ MIT)
4. **Save configurations** to motor flash
5. **Control motors reliably** with unique IDs

---

**Next Action:** Clone the repositories and analyze the command formats!

```bash
# Start here:
git clone https://github.com/RobStride/SampleProgram.git
cd SampleProgram
# Look for RobStride.h and RobStride01.cpp
```

