# Motor Investigation Checklist

## Current Status
- **Expected**: 15 motors
- **Responding**: 2 motors (Motor 1 and Motor 2)
- **Missing**: 13 motors

## Physical Checks (Do First!)

### 1. Power Check
- [ ] Are all 15 motors receiving power?
- [ ] Check power LEDs on motor controllers (if present)
- [ ] Verify power supply is connected to all motors
- [ ] Check power supply voltage levels
- [ ] Verify power supply can handle all 15 motors

### 2. CAN Bus Connections
- [ ] Are all motors connected to CAN-H (CAN High)?
- [ ] Are all motors connected to CAN-L (CAN Low)?
- [ ] Are all motors connected to GND (Ground)?
- [ ] Check for loose or disconnected wires
- [ ] Verify CAN bus wiring is continuous (daisy-chained correctly)

### 3. Termination Resistors
- [ ] Is there a 120Ω termination resistor at ONE end of CAN bus?
- [ ] Is there a 120Ω termination resistor at OTHER end of CAN bus?
- [ ] Are there termination resistors in the MIDDLE? (should not be)
- [ ] Verify resistor values (should be 120Ω)

### 4. Motor Status
- [ ] Do motors have status LEDs? What do they show?
- [ ] Are motors in enabled/active state?
- [ ] Do motors need activation commands?
- [ ] Check motor documentation for enable/disable states

## Software Checks

### 5. Run Investigation Script
```powershell
cd F:\Melvin_Research\Melvin_Research
python investigate_motors.py
```

Or double-click: `run_investigation.bat`

### 6. Test Results to Look For
- Which ID ranges produce movement?
- How many motors move when testing different IDs?
- Do multiple IDs produce movement from the same motor?
- Are there any IDs that produce NO movement?

## Common Issues and Solutions

### Issue: Motors Not Powered
**Symptoms**: No movement, no status LEDs
**Solution**: Check power connections, verify power supply

### Issue: Motors Not on CAN Bus
**Symptoms**: Motors don't respond to any IDs
**Solution**: Check CAN-H, CAN-L, GND connections

### Issue: Missing Termination
**Symptoms**: Intermittent communication, only some motors respond
**Solution**: Add 120Ω resistors at both ends of CAN bus

### Issue: Motors Need Activation
**Symptoms**: Motors have power but don't respond
**Solution**: Check if motors need enable/activation commands
- Some motors require specific activation sequence
- Motors might be in sleep/standby mode
- Check motor documentation for initialization

### Issue: CAN Bus Segments
**Symptoms**: Some motors respond, others don't, but all are connected
**Solution**: Check for CAN bus routers/switches
- Motors might be on different bus segments
- May need to configure router/switch

### Issue: Wrong Bitrate
**Symptoms**: Intermittent communication
**Solution**: Verify CAN bus bitrate matches motor requirements
- L91 adapter might need bitrate configuration
- Motors might require specific bitrate (500kbps, 1Mbps, etc.)

## Testing Strategy

1. **Start with physical checks** (power, connections)
2. **Run investigation script** to see response patterns
3. **Test individual motors** (disconnect others, test one at a time)
4. **Check motor documentation** for activation/enable procedures
5. **Verify CAN bus configuration** (bitrate, termination)

## What to Report

When running investigation, note:
- Which CAN IDs produce movement
- Which physical motors move for each ID
- How many motors move when testing multiple IDs
- Any error messages or unusual behavior

