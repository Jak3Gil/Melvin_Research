# Motor Configuration Approach

## Current Situation

- **Motor 1** responds to CAN IDs 8-15 (all control the same motor)
- **Motor 2** responds to CAN IDs 16-22 (all control the same motor)
- **13 other motors** exist but don't respond to action commands
- **No DIP switches** - need software configuration
- **Action commands aren't reaching** the other motors

## Configuration Strategy

Since action commands (activate, move) aren't reaching the other motors, we'll try:

1. **Configuration commands** - Try to set CAN IDs using various command formats
2. **Multiple source IDs** - Try configuring from:
   - ID 0 (default/unconfigured state)
   - ID 8 (currently Motor 1)
   - ID 16 (currently Motor 2)
3. **Target IDs** - Configure to IDs 1-7 and 23-31 (avoiding 8-22 which are in use)

## The Script

`configure_all_motors.py` will:
1. Try various configuration command formats (command bytes 0x10-0x51)
2. Try multiple data formats for each command
3. Attempt to configure motors from source IDs to target IDs
4. Test all IDs after configuration to see which motors respond
5. Report which physical motors respond to which CAN IDs

## Running the Script

```powershell
cd F:\Melvin_Research\Melvin_Research
python configure_all_motors.py
```

Or double-click: `run_configure_all.bat`

## What to Expect

The script will:
- Try many configuration command formats
- Take some time (testing many command combinations)
- Ask you to identify which physical motors move for each CAN ID
- Report results showing which motors respond to which IDs

## If Configuration Works

- More than 2 motors should respond to different IDs
- Each motor should respond to a unique CAN ID
- You'll have a mapping of CAN IDs to physical motors

## If Configuration Doesn't Work

If still only 2 motors respond:
- Configuration commands may not be supported via software
- Motors may need hardware configuration (but you said no DIP switches)
- Motors may need manufacturer-specific configuration tool
- Motors may need to be configured one at a time (disconnect others)

## Alternative: Configure One at a Time

If the script doesn't work, you could try:
1. Disconnect all motors except one
2. Run configuration commands for that one motor
3. Set it to a unique CAN ID
4. Disconnect it, connect next motor
5. Repeat for all motors

