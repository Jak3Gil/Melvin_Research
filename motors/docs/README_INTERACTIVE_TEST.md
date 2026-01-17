# Interactive Motor Tester

Interactive script to test and identify motors one at a time with keyboard controls.

## Usage

```powershell
python test_motors_interactive.py [COM_PORT] [BAUD_RATE]
```

**Default:**
```powershell
python test_motors_interactive.py COM3 921600
```

## Controls

- **W / w** - Move motor forward (small jog ~5 degrees)
- **S / s** - Move motor backward (small jog ~5 degrees)
- **SPACE** - Next motor
- **Q / q** - Quit and stop all motors

## How It Works

1. The script cycles through motors in this order:
   - CAN IDs 16-22 (likely physical motors 1-7)
   - CAN IDs 8-15 (likely physical motors 8-15)

2. For each motor:
   - Activates and initializes the motor
   - Shows the current motor number and CAN ID
   - Waits for keyboard input
   - Moves the motor when you press W or S
   - Moves to next motor when you press SPACE

3. Movement:
   - Very small speed (0.02) for precise testing
   - Short duration (0.3 seconds) per keypress
   - Motor stops automatically after movement

## Identifying Motors

1. Run the script
2. Watch the physical motor when you press W or S
3. Note which physical motor number moves
4. Press SPACE to move to the next CAN ID
5. Repeat for all motors
6. Create a mapping: Physical Motor X → CAN ID Y

## Adjusting Movement

If movements are too large or too small, edit the script:

```python
move_speed = 0.02  # Smaller = less movement (try 0.01 for smaller, 0.05 for larger)
move_duration = 0.3  # How long to move (seconds)
```

## Safety

- Motors are deactivated when moving to next motor
- Motors are stopped when quitting
- Very small movements to prevent damage
- All motors are stopped on exit

## Example Session

```
============================================================
INTERACTIVE MOTOR TESTER
============================================================

Testing Motor 1 of 15
CAN ID: 16 (0x10)
Physical Motor Number: 1

------------------------------------------------------------
CONTROLS:
  W / w - Move forward (small jog)
  S / s - Move backward (small jog)
  SPACE - Next motor
  Q / q - Quit
------------------------------------------------------------

Waiting for input...
```

Press W → Motor moves forward
Press S → Motor moves backward  
Press SPACE → Moves to next motor (CAN ID 17)

## Notes

- Works on Windows (uses msvcrt for keyboard input)
- Make sure no other program is using COM3
- Motors must be powered and connected
- Watch the motors carefully to identify them!

