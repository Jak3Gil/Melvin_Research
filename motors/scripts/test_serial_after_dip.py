#!/usr/bin/env python3
"""
Test if /dev/ttyUSB0 still works after DIP switch change
"""

import serial
import struct
import time

def send_l91(ser, can_id, data):
    """Send L91 protocol command"""
    packet = bytearray([0xAA, 0x55, 0x01, 0x08])
    packet.extend(struct.pack('<I', can_id))
    packet.extend(data)
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    ser.write(packet)
    time.sleep(0.1)
    return ser.read(100)

print("="*60)
print("  Testing Serial Port After DIP Switch Change")
print("="*60)

try:
    ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0.5)
    print("\n✓ /dev/ttyUSB0 opened\n")
    
    print("Sending enable command to motor 8...")
    response = send_l91(ser, 8, bytes([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
    
    if response:
        print(f"✓ Motor responded: {len(response)} bytes")
        print(f"  Response: {response.hex()}")
        print(f"\n✓ Still in Serial Mode (L91 protocol)")
        print(f"  DIP switches may control other features")
    else:
        print("✗ No response via /dev/ttyUSB0")
        print("\n  Possible meanings:")
        print("  1. DIP switches changed to CAN mode (motors now on can0/can1)")
        print("  2. Motors need power cycle")
        print("  3. Different baud rate needed")
    
    ser.close()
    
except Exception as e:
    print(f"✗ Error: {e}")

print()

