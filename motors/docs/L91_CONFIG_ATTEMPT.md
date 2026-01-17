# L91 CAN ID Configuration Attempt

Since Motor Studio isn't working, we're trying to configure CAN IDs directly using L91 protocol commands.

## Known L91 Command Format

**Format**: `AT <cmd_byte> 0x07 0xe8 <can_id> <data...> 0x0d 0x0a`

**Known Command Bytes:**
- `0x00` = Activate/Deactivate motor
- `0x20` = Load parameters
- `0x90` = Move jog

## Configuration Command Attempts

The script `configure_l91_can_id.py` tries various command bytes that might be used for CAN ID configuration:

- `0x10-0x1F` - Parameter/config commands
- `0x30-0x3F` - Configuration commands
- `0x40-0x4F` - Extended configuration
- `0x50-0x5F` - Settings commands
- `0x60-0x70` - Alternative formats

## Usage

```powershell
cd F:\Melvin_Research\Melvin_Research
python configure_l91_can_id.py <source_id> <target_id>
```

**Example:**
```powershell
# Try to configure from default ID 0 to ID 1
python configure_l91_can_id.py 0 1

# Try to configure from ID 8 (currently working) to ID 9
python configure_l91_can_id.py 8 9
```

## Important Notes

1. **No Official Documentation**: L91 protocol CAN ID configuration commands are not publicly documented
2. **Experimental**: These commands are guesses based on common patterns
3. **May Not Work**: Configuration might require:
   - Hardware configuration (DIP switches/jumpers)
   - Manufacturer-specific commands
   - Configuration software (Motor Studio)
   - Motors configured one at a time (disconnect others)

## Next Steps if This Doesn't Work

1. **Check motor hardware** for DIP switches/jumpers
2. **Contact motor manufacturer** for configuration documentation
3. **Try configuring motors one at a time** (disconnect others)
4. **Check if motors have configuration mode** (buttons/switches)

