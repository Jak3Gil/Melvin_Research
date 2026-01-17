# Next Steps - CAN Bus Motor Configuration

## Current Status

✅ **Hardware is working** (power, connections confirmed)  
❌ **Only 2 motors responding** (Motor 1 and Motor 2)  
❌ **13 motors not responding**  
❌ **Software activation didn't work**  
❌ **Configuration commands didn't work**  

## This IS a Common CAN Bus Issue

Yes, this happens frequently with CAN bus systems. The problem is:

**Motors need to be configured with unique CAN IDs before they can all respond individually.**

## Why Only 2 Motors Work

The 2 working motors (Motor 1 and Motor 2) have likely been configured with CAN IDs already.  
The 13 non-responding motors are probably still at default/unconfigured state.

## What You Need

### Option 1: Motor Configuration Software (BEST)

Look for software from your motor manufacturer:
- **Robstride Motor Studio** (if Robstride motors)
- Motor configuration/management software
- CAN bus configuration tools

**How to use:**
1. Connect one motor at a time (or use software's addressing)
2. Open configuration software
3. Set unique CAN ID (1-15 or 1-31)
4. Save configuration
5. Repeat for each motor

### Option 2: Hardware Configuration

Check if your motors have:
- **DIP switches** for CAN ID selection
- **Jumpers** for ID configuration
- **Buttons/switches** for ID setting

**How to use:**
1. Set DIP switches/jumpers for desired CAN ID
2. Apply power (some motors read switches on power-up)
3. Repeat for each motor

### Option 3: Configuration Commands (If Documented)

If your motor documentation specifies CAN ID configuration commands:

1. **Disconnect all motors except one**
2. Send configuration command with new CAN ID
3. Save configuration (if required)
4. Disconnect, connect next motor
5. Repeat for all motors

### Option 4: Contact Manufacturer Support

If you can't find configuration method:
- Contact motor manufacturer
- Ask for CAN ID configuration procedure
- Request configuration software/tools

## Immediate Action Items

1. **Check Motor Documentation**
   - Look for "CAN ID Configuration" section
   - Find configuration software name
   - Check for hardware configuration options

2. **Look for Configuration Software**
   - Check manufacturer website
   - Download motor management software
   - Install and try to configure motors

3. **Check Motor Hardware**
   - Look for DIP switches
   - Check for jumpers
   - Look for configuration buttons/ports

4. **Try Configuration Script** (Experimental)
   ```powershell
   python try_configuration_commands.py
   ```
   Note: This may not work - command format is motor-specific

## Recommended Approach

1. **First**: Check motor documentation/manual
2. **Second**: Look for configuration software
3. **Third**: Check for hardware configuration (DIP switches)
4. **Fourth**: Try configuration commands (if documented)
5. **Last**: Contact manufacturer support

## Summary

Your motors are working, but they need to be configured with unique CAN IDs. This is a normal step in CAN bus setup. The 2 working motors have been configured, the other 13 need configuration.

The configuration method depends on your specific motor type - check documentation or use manufacturer's configuration software.

