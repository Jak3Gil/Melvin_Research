# CAN Bus Addressing Issue - Common Problem

## Your Situation
- **15 motors connected to CAN bus**
- **Only 2 motors respond to commands**
- **All IDs (8-15) control Motor 1**
- **All IDs (16-22) control Motor 2**
- **Other 13 motors don't respond at all**

## This IS a Common CAN Bus Issue

Yes, this happens frequently with CAN bus systems, especially when:
1. Motors are shipped with default/same CAN IDs
2. Motors need to be individually configured with unique IDs
3. CAN bus addressing isn't set up properly

## Why This Happens

### Common Causes:

1. **Default CAN IDs**
   - Motors often ship with ID 0 (broadcast) or all set to the same ID
   - Only motors that have been configured respond to their specific IDs
   - Unconfigured motors either:
     - Don't respond (most common)
     - Respond to broadcast/default ID only
     - Respond to a default ID range

2. **CAN Bus Filtering**
   - Motors filter CAN messages by ID
   - If motor ID doesn't match message ID, motor ignores the message
   - Motors with default/unconfigured IDs ignore most messages

3. **Initialization Required**
   - Some motors need initialization to accept CAN IDs
   - Motors may need to be in "configuration mode"
   - Motors may need enable/activation before accepting IDs

## Your Specific Case

Based on your results:
- **Motor 1** responds to IDs 8-15 (likely configured to ID 8, but responding to range)
- **Motor 2** responds to IDs 16-22 (likely configured to ID 16, but responding to range)
- **Other 13 motors** don't respond (likely still at default/unconfigured state)

## What This Means

The 13 non-responding motors are probably:
1. **At default/unconfigured state** - Need to be configured with unique IDs
2. **Not filtering properly** - Need configuration to set their CAN ID
3. **In a sleep/disabled state** - Need activation/enable first

## Solutions

### Solution 1: Configure Motors with Unique IDs (Most Likely)

Motors need to be configured with unique CAN IDs. Common methods:

1. **Configuration Software** (Best option)
   - Motor manufacturer's software (Robstride Motor Studio, etc.)
   - Connect one motor at a time
   - Set unique CAN ID (1-15 or 1-31)
   - Repeat for each motor

2. **Hardware Configuration**
   - DIP switches on motor controllers
   - Jumpers for ID selection
   - Check motor documentation

3. **CAN ID Configuration Commands** (If supported)
   - Some motors support software ID configuration
   - Usually requires specific command format
   - May need to disconnect other motors first

### Solution 2: Disconnect Motors One at a Time

If configuration software isn't available:

1. Disconnect all motors except one
2. Connect motor to CAN bus
3. Send configuration commands
4. Set motor to unique CAN ID (1-15)
5. Disconnect, connect next motor
6. Repeat for all 15 motors

### Solution 3: Check Motor Documentation

Your motor documentation should specify:
- How to configure CAN IDs
- Default CAN ID values
- Configuration procedure
- Required software/tools

## Why Software Activation Didn't Work

Software activation commands (activate, load params) won't help if:
- Motors don't have unique CAN IDs configured
- Motors are filtering messages by ID (ignoring commands)
- Motors need configuration mode first

## Next Steps

1. **Check motor documentation** for CAN ID configuration method
2. **Look for configuration software** from motor manufacturer
3. **Try configuration commands** (if documented)
4. **Use hardware configuration** (DIP switches/jumpers) if available
5. **Configure motors one at a time** (disconnect others)

## Summary

Yes, this is a common CAN bus issue. Your motors likely need to be configured with unique CAN IDs before they can all respond individually. The fact that 2 motors are working suggests those 2 have been configured, while the other 13 are still at default/unconfigured state.

