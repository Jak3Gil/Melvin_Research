# How to Configure Motor CAN IDs

Since all motors are currently responding to the same commands, they need to be configured with unique CAN IDs.

## The Problem

All motors are responding to all CAN IDs, which means:
- They're all configured to the same CAN ID (likely ID 0 or broadcast)
- They can't be controlled individually
- They need to be configured with unique IDs (1-15 or 8-22)

## Step 1: Identify Motors Physically

Use the identification script to identify which physical motor is which:

```powershell
cd F:\Melvin_Research\Melvin_Research
python identify_motors.py
```

This will:
- Move each motor with a unique pattern (number of movements)
- Help you identify which physical motor is Motor 1, Motor 2, etc.
- Record which CAN ID each motor should have

## Step 2: Configure CAN IDs

**Method 1: Motor Configuration Software (RECOMMENDED)**

Most motor controllers come with configuration software:
- **Robstride**: Motor Studio or similar software
- Connect one motor at a time
- Use software to set unique CAN ID (1-15)
- Repeat for each motor

**Method 2: Hardware Configuration**

Some motors use:
- **DIP switches** - set CAN ID using binary switches
- **Jumpers** - configure ID using jumper settings
- Check motor documentation for pin/switch settings

**Method 3: Configuration Commands (if supported)**

Some motors support CAN ID configuration via commands:
- Check motor documentation for configuration protocol
- May require entering "configuration mode"
- Send configuration commands with new CAN ID

**Method 4: Try Configuration Script (Experimental)**

```powershell
python configure_motor_id.py <old_id> <new_id>
```

**WARNING**: This is a template - actual command format varies by motor type.
Check your motor documentation for the correct configuration method.

## Step 3: Verify Configuration

After configuring:

```powershell
# Scan for motors
python scan_robstride_motors.py COM3 921600 --scan-all

# Test individual motors
python test_single_motor.py 8
python test_single_motor.py 9
# etc.
```

Each motor should only respond to its configured CAN ID.

## Recommended CAN ID Assignment

Based on your setup, suggested mapping:
- **Physical Motors 1-7** → **CAN IDs 16-22** (0x10-0x16)
- **Physical Motors 8-15** → **CAN IDs 8-15** (0x08-0x0F)

## What You Need

1. **Motor documentation** - to find the correct configuration method
2. **Motor configuration software** (if available)
3. **Physical access** - to see motors move during identification
4. **Patience** - configure one motor at a time

## Quick Reference

**Identify motors:**
```powershell
python identify_motors.py
```

**Test a specific motor:**
```powershell
python test_single_motor.py <CAN_ID>
```

**Scan all motors:**
```powershell
python scan_robstride_motors.py COM3 921600 --scan-all
```

## Next Steps

1. Check your motor documentation/manual for CAN ID configuration
2. Identify motors using the identification script
3. Configure each motor with a unique CAN ID using the recommended method
4. Verify each motor responds only to its assigned CAN ID

