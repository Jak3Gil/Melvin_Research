# Melvin_november Repository Findings

## Repository Location
**GitHub**: https://github.com/Jak3Gil/Melvin_november

## Documentation Structure

Based on the repository structure:
- **docs/** folder exists - Contains documentation files (reorganized Dec 6, 2025)
- Documentation was moved to `docs/` directory in recent commit

## Motor-Related Files Found

From the repository (based on MOTOR_COMMANDS_REFERENCE.md):

### Key Files:
1. **`test_motors_12_14.c`** - Complete test program for motors 12 & 14
2. **`test_robstride_motors.c`** - Robstride-specific motor tests
3. **`melvin_motor_runtime.c`** - Runtime system that bridges brain EXEC nodes to motors
4. **`setup_usb_can_motors.sh`** - Complete setup script for USB-to-CAN
5. **`map_can_ids_to_physical_motors.c`** - Motor discovery and mapping
6. **`tools/map_can_motors.c`** - CAN motor discovery tool

## Motor Command Protocol

The repository uses **direct CAN bus commands** (not L91 protocol):
- Uses `slcan0` or `can0` interface
- CAN bitrate: 500kbps
- Motor IDs: 1-14 (0x01-0x0E)
- Commands: 0xA0 (disable), 0xA1 (enable), 0xA2 (velocity), 0xA3 (torque)

## Important Note

**The Melvin_november repository uses direct CAN bus protocol, NOT L91 protocol!**

Your setup uses:
- **L91 protocol** over USB-to-Serial (921600 baud)
- **AT commands** format (e.g., `AT 00 07 e8 <id> 01 00 0d 0a`)

The Melvin_november repository uses:
- **Direct CAN bus** via `slcan0` interface
- **Raw CAN frames** (struct can_frame)
- **Linux CAN utilities** (can-utils, slcand)

## CAN ID Configuration

**The repository does NOT appear to contain CAN ID configuration commands.**

The files show:
- Motor control commands (enable, disable, position, velocity, torque)
- Motor discovery/mapping tools
- Test programs

But **no CAN ID configuration/address setting commands** are documented.

## What This Means

1. **Different Protocol**: Melvin_november uses direct CAN, you're using L91
2. **No ID Config Found**: The repository doesn't show how to configure CAN IDs
3. **Motors Assumed Configured**: The code assumes motors already have unique CAN IDs

## Next Steps

Since the Melvin_november repository doesn't have CAN ID configuration:
1. **Check motor hardware** for DIP switches/jumpers
2. **Look for motor manufacturer documentation** (Robstride)
3. **Try Motor Studio** (if you can get it working)
4. **Contact Robstride support** for CAN ID configuration method

## References

- Repository: https://github.com/Jak3Gil/Melvin_november
- Motor Commands Reference: See `MOTOR_COMMANDS_REFERENCE.md` in this project

