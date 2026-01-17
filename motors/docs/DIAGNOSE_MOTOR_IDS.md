# Diagnosing Motor ID Issue

If all motor IDs move the same motor, this suggests the motors might all be configured to the same CAN ID, or they're responding to all commands.

## Test Individual Motor IDs

Test one motor ID at a time to see which physical motor responds:

```powershell
cd F:\Melvin_Research\Melvin_Research
python test_single_motor.py 8
```

Try different IDs:
- `python test_single_motor.py 8`
- `python test_single_motor.py 9`
- `python test_single_motor.py 16`
- etc.

## What to Look For

1. **If ALL motors move when testing ANY ID:**
   - All motors might be configured to the same CAN ID
   - Motors might not be filtering by CAN ID
   - CAN bus configuration issue

2. **If NO motors move for a specific ID:**
   - That CAN ID doesn't have a motor assigned
   - Motor is not responding

3. **If ONE motor moves (correct behavior):**
   - That motor is correctly configured to that CAN ID

## Possible Issues

### All Motors Respond to All IDs
- Motors might not have unique CAN IDs configured
- They might all be set to ID 0 (broadcast)
- CAN bus hardware issue

### Solution
- Check motor configuration (might need to configure CAN IDs using motor setup software)
- Verify CAN bus wiring
- Check if motors need to be individually configured with unique IDs

