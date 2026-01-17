# 🚀 Quick Start: Configure Your Motors (NO ROS NEEDED!)

## ✅ What You Have Now

- ✅ Python script uploaded to Jetson: `~/robstride_motor_config.py`
- ✅ Based on official RobStride source code
- ✅ NO ROS required!
- ✅ Ready to run

---

## 🎯 Three Simple Steps

### Step 1: Connect to Jetson

```bash
ssh melvin@192.168.1.119
```

### Step 2: Run Auto-Configuration

```bash
python3 robstride_motor_config.py --configure-all
```

This will:
- Scan for all motors
- Assign unique IDs (1, 2, 3, 4, 5, 6)
- Save to flash memory
- Verify configuration

### Step 3: Power-Cycle Motors

**Turn off motor power → Wait 5 seconds → Turn on motor power**

---

## 🎉 Done!

Your motors now have unique IDs:
- Motor 1: ID 1
- Motor 2: ID 2
- Motor 3: ID 3
- Motor 4: ID 4
- Motor 5: ID 5
- Motor 6: ID 6

---

## 🧪 Test Your Motors

```bash
ssh melvin@192.168.1.119
python3
```

```python
from robstride_motor_config import RobStrideMotor

motor = RobStrideMotor('/dev/ttyUSB0', 921600)

# Test each motor
for i in range(1, 7):
    print(f"Testing motor {i}...")
    motor.enable_motor(i)
    motor.disable_motor(i)

motor.close()
```

---

## 📖 Key Commands

### Scan for Motors
```bash
python3 -c "from robstride_motor_config import RobStrideMotor; m = RobStrideMotor(); m.scan_motors(1, 127); m.close()"
```

### Change Single Motor ID
```python
from robstride_motor_config import RobStrideMotor

motor = RobStrideMotor()
motor.set_motor_id(old_id=8, new_id=1)  # Change motor 8 to ID 1
motor.close()
```

### Set Zero Position
```python
motor = RobStrideMotor()
motor.set_zero_position(motor_id=1)
motor.close()
```

---

## ⚠️ If Something Goes Wrong

### Motors don't respond after configuration?
→ **Power-cycle the motors** (turn off, wait, turn on)

### Configuration doesn't save?
→ Check that `save_motor_data()` was called (it's automatic in the script)

### Still having issues?
1. Check CAN bus termination (120Ω resistors)
2. Verify power supply is stable
3. Check all wiring connections
4. Try configuring one motor at a time

---

## 📚 Full Documentation

- `SOLUTION_MOTOR_CONFIGURATION.md` - Complete guide
- `ROBSTRIDE_CONFIGURATION_GUIDE.md` - Detailed reference
- `robstride_motor_config.py` - Source code with comments

---

## 🎯 What This Solves

### Before:
- ❌ Motors respond to multiple IDs
- ❌ Can't control motors individually
- ❌ Inconsistent behavior

### After:
- ✅ Each motor has ONE unique ID
- ✅ Individual motor control
- ✅ Consistent, reliable operation

---

**Ready? Let's configure those motors!**

```bash
ssh melvin@192.168.1.119
python3 robstride_motor_config.py --configure-all
```

🚀

