# Current Motor Status

## Latest Scan Results (Jetson - January 6, 2025)

**USB-to-CAN Adapter Found:**
- Device: `/dev/ttyUSB0` (QinHeng Electronics HL-340 / CH340)
- Baud Rate: 921600 (working)

**CAN IDs Responding:**
- CAN IDs 8-15 (0x08-0x0F): **8 IDs** - All control **Motor 1**
- CAN IDs 16-31 (0x10-0x1F): **16 IDs** - All control **Motor 2**
- IDs 1-7 (0x01-0x07): Do NOT respond

**Physical Motor Status (CONFIRMED):**
- **Only 2 physical motors are responding**
- **Physical Motor 1**: Controlled by CAN IDs 8-15 (all 8 IDs control the same motor)
- **Physical Motor 2**: Controlled by CAN IDs 16-31 (all 16 IDs control the same motor)
- Motors are not properly configured with unique CAN IDs (multiple IDs per motor)

**Missing:** 13 motors (should have 15 total)

## Implications

1. **Configuration didn't work** - The remapping script's configuration commands didn't change motor IDs
2. **Only 2 motors active** - 13 motors are not responding at all
3. **Motor grouping pattern** - Motors respond in groups (8 IDs → Motor 1, 16 IDs → Motor 2)

## What This Means

Since configuration commands didn't work, the motors likely:
- Don't support software CAN ID configuration via L91 protocol
- Need hardware configuration (DIP switches, jumpers)
- Need configuration software (motor manufacturer's tool)
- Need to be configured one at a time (disconnect others)

## Current Working Setup

You can currently control:
- **Motor 1** using any CAN ID from 8-15 (all 8 IDs control Motor 1)
- **Motor 2** using any CAN ID from 16-31 (all 16 IDs control Motor 2)

## Questions to Answer

1. **Where are the other 13 motors?**
   - Are they powered on?
   - Are they connected to CAN bus?
   - Do they need to be enabled/activated?

2. **How to configure CAN IDs?**
   - Check motor documentation for CAN ID configuration method
   - Look for DIP switches or jumpers on motor controllers
   - Check if you have motor configuration software

## Next Steps

1. **Check all motors are powered/connected**
   - Verify all 15 motors have power
   - Check CAN bus connections (CAN-H, CAN-L, GND)
   - Verify termination resistors (120Ω at both ends)

2. **Find configuration method**
   - Check motor documentation/manual
   - Look for configuration software
   - Check for hardware configuration options

3. **For now, use what works:**
   - Control Motor 1: Use any CAN ID from 8-15 (e.g., CAN ID 8)
   - Control Motor 2: Use any CAN ID from 16-31 (e.g., CAN ID 16)
   - This gives you 2 motors you can control individually

