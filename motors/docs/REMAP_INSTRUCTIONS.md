# Remapping Motor CAN IDs

## The Challenge

All motors are currently responding to all CAN IDs, which means they're all configured to the same ID (or not filtering). To control them individually, each motor needs a unique CAN ID.

## The Problem with Remapping

Since all motors respond to all commands, we can't easily configure them one at a time via software commands - any configuration command would affect all motors the same way.

## Solutions (in order of recommendation):

### Solution 1: Disconnect Motors One at a Time (Most Reliable)

1. **Disconnect all motors except one** from the CAN bus
2. Connect only Motor 1 to CAN bus
3. Run configuration software/commands to set it to CAN ID 16
4. Disconnect Motor 1, connect only Motor 2
5. Configure Motor 2 to CAN ID 17
6. Repeat for all motors

### Solution 2: Motor Configuration Software (Recommended)

1. Use motor manufacturer's configuration software (e.g., Robstride Motor Studio)
2. Connect motors one at a time (or use software's individual addressing)
3. Configure each motor with unique CAN ID via software
4. Software typically handles individual motor identification

### Solution 3: Hardware Configuration (If Available)

1. Check if motors have **DIP switches** or **jumpers** for CAN ID
2. Set switches/jumpers on each motor to desired ID
3. No software needed - hardware configuration

### Solution 4: Try Configuration Commands (Experimental)

Run the remapping script:

```powershell
cd F:\Melvin_Research\Melvin_Research
python remap_motor_ids.py
```

**WARNING**: This may not work if:
- Motors don't support software CAN ID configuration
- Configuration command format is different
- All motors receive the same configuration command

## Verification

After configuring, verify each motor responds only to its assigned ID:

```powershell
# Test each ID individually
python test_single_motor.py 16  # Should move only one motor
python test_single_motor.py 17  # Should move a different motor
python test_single_motor.py 8   # Should move a different motor
```

If all IDs still move the same motor(s), configuration didn't work and you need to use Solution 1, 2, or 3.

## Recommended CAN ID Assignment

- **Physical Motors 1-7** → **CAN IDs 16-22** (0x10-0x16)
- **Physical Motors 8-15** → **CAN IDs 8-15** (0x08-0x0F)

This gives you 15 unique IDs for 15 motors.

