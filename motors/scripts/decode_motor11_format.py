#!/usr/bin/env python3
"""Decode Motor 11's 4-byte format"""
import struct

# Motor 11 bytes: e8 9c 01 00
motor11_bytes = bytes.fromhex('e89c0100')
motor11_id = 11

print(f"Motor 11 (CAN ID {motor11_id}):")
print(f"4 bytes: {motor11_bytes.hex()}")
print()

# Try different decodings
val_le = struct.unpack('<I', motor11_bytes)[0]  # Little-endian
val_be = struct.unpack('>I', motor11_bytes)[0]  # Big-endian

print(f"Little-endian 32-bit: 0x{val_le:08X} = {val_le}")
print(f"Big-endian 32-bit:   0x{val_be:08X} = {val_be}")
print()

# Try to find pattern
print("Possible patterns:")
print(f"  As bytes: 0x{motor11_bytes[0]:02X} 0x{motor11_bytes[1]:02X} 0x{motor11_bytes[2]:02X} 0x{motor11_bytes[3]:02X}")

# CANopen COB-IDs
print(f"\nCANopen COB-IDs for node {motor11_id}:")
print(f"  SDO (0x600+{motor11_id}):    0x{0x600 + motor11_id:03X} = {0x600 + motor11_id}")
print(f"  RPDO (0x180+{motor11_id}):   0x{0x180 + motor11_id:03X} = {0x180 + motor11_id}")
print(f"  TPDO (0x200+{motor11_id}):   0x{0x200 + motor11_id:03X} = {0x200 + motor11_id}")
print(f"  Emergency (0x80+{motor11_id}): 0x{0x80 + motor11_id:03X} = {0x80 + motor11_id}")

# Check if it matches
sdo = 0x600 + motor11_id
rpdo = 0x180 + motor11_id
tpdo = 0x200 + motor11_id
emergency = 0x80 + motor11_id

print(f"\nComparing:")
print(f"  Value (little-endian): 0x{val_le:08X}")
print(f"  SDO (0x{0x600 + motor11_id:03X}): 0x{sdo:08X} - {'MATCH!' if val_le == sdo else 'no match'}")
print(f"  RPDO (0x{0x180 + motor11_id:03X}): 0x{rpdo:08X} - {'MATCH!' if val_le == rpdo else 'no match'}")
print(f"  TPDO (0x{0x200 + motor11_id:03X}): 0x{tpdo:08X} - {'MATCH!' if val_le == tpdo else 'no match'}")

# Try reverse - what if we encode 11 differently?
print(f"\nTesting reverse encoding:")
test_val = 0x00019ce8
print(f"  0x00019ce8 as bytes (little-endian): {struct.pack('<I', test_val).hex()}")
print(f"  Does it equal e89c0100? {struct.pack('<I', test_val).hex() == 'e89c0100'}")

