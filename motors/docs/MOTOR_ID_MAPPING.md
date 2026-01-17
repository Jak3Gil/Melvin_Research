# Robstride Motor ID Mapping

Based on wide scan results, here's the discovered motor ID mapping:

## Discovered Motors

**Total Found: 24+ motors responding** (at base address 0x07e8)

### Likely Physical Motor Mapping

Based on the scan results, it appears that:

- **Physical Motors 1-7** → **CAN IDs 16-22** (0x10-0x16)
- **Physical Motors 8-15** → **CAN IDs 8-15** (0x08-0x0F)

### Complete List of Responding CAN IDs

**CAN IDs 8-31** (0x08-0x1F) all respond to commands at base address 0x07e8:

- IDs 8-15: Likely physical motors 8-15
- IDs 16-22: Likely physical motors 1-7  
- IDs 23-31: Additional motors? (may be more than 15 total, or different devices)

## Usage

To control motors, use the CAN IDs shown above:

```powershell
# Test physical motor 1 (CAN ID 16)
python scan_robstride_motors.py COM3 921600 --test 16

# Test physical motor 8 (CAN ID 8)
python scan_robstride_motors.py COM3 921600 --test 8
```

## Notes

1. The first 7 motors (physical) use CAN IDs 16-22 instead of 1-7
2. Motors 8-15 use CAN IDs 8-15 (matches physical numbering)
3. All motors respond at base address 0x07e8
4. The wide scan found responses up to ID 31, suggesting more devices may be connected

## Verification

To verify the mapping, you can:
1. Test motor at CAN ID 16 and see which physical motor moves (should be motor 1)
2. Test motor at CAN ID 8 and see which physical motor moves (should be motor 8)
3. Create a mapping table based on visual observation

