# Deep Investigation Strategies

## Running Investigation: `deep_investigation.py`

### Strategies Being Tested:

1. **Strategy 1: Selective Gap Activation**
   - Activates ONLY missing ID ranges (0-7, 40-63)
   - Tests if activating gaps first wakes up missing motors
   - Bypasses known working ranges

2. **Strategy 2: Reverse Order Activation**
   - Activates IDs 255→0 (reverse order)
   - Tests if different activation sequence reveals motors
   - May trigger different motor state

3. **Strategy 3: Powers of 2 Activation**
   - Activates powers of 2 first (1, 2, 4, 8, 16, 32, 64, 128)
   - Then fills in remaining IDs
   - Tests if strategic activation pattern works

4. **Strategy 4: Slow Individual Activation**
   - Activates each ID individually with long delays (0.2s)
   - Tests if slow, careful activation finds more motors
   - Gives motors more time to respond

5. **Strategy 5: Different Baud Rates**
   - Tests 115200, 460800, 921600, 1000000 baud
   - Tests if baud rate affects motor detection
   - May reveal motors that only respond at specific rates

6. **Strategy 6: Broadcast Commands**
   - Tests broadcast ID 0 and ID 255
   - Tests AT+AT detect command
   - Tests if broadcast wakes up all motors

7. **Strategy 7: CAN Interface Setup**
   - Sets up slcan0 from /dev/ttyUSB0
   - Tests if direct CAN interface finds motors
   - Enables RobStride SDK testing

## Additional Investigation: `test_alternative_protocols.py`

### Alternative Protocol Tests:

1. **Different Command Formats**
   - Various address bytes (0x00, 0x01, 0xFF, etc.)
   - Different command bytes (0x01, 0x02, 0x10, etc.)
   - Tests if missing motors respond to different formats

2. **Extended CAN ID Hypothesis**
   - Tests if motors use extended ID encoding
   - Tries shifted, extended formats
   - Tests 0x100+id, 0x200+id formats

3. **Missing Range Testing**
   - Focuses on ID ranges: 0-7, 40-63, 80-255
   - Tests each with multiple command formats
   - Systematic approach to missing ranges

## Current Status

### Known Working:
- **IDs 8-39** (32 IDs) - Responding after rapid activation
- **IDs 64-79** (16 IDs) - Responding after rapid activation

### Missing:
- **IDs 0-7** - Not responding
- **IDs 40-63** - Not responding  
- **IDs 80-255** - Not responding (except 64-79)

### Hypothesis:
- Missing motors may need:
  - Different activation sequence
  - Different command format
  - Different baud rate
  - Direct CAN protocol (not L91)
  - Hardware configuration

## Expected Results

Each strategy will report:
- Number of responding IDs found
- Which IDs respond
- Whether different patterns reveal more motors

## Next Steps After Investigation

1. **Analyze Results** - Compare all strategies
2. **Identify Best Strategy** - Which finds most motors
3. **Test Combined Approaches** - Merge successful strategies
4. **Physical Verification** - Check if motors are actually connected/powered
5. **Try Direct CAN** - Use RobStride SDK if slcan0 setup succeeds

