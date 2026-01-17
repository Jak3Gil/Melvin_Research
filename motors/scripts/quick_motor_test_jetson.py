#!/usr/bin/env python3
"""Quick test if motors respond on /dev/ttyUSB0 at 921600 baud"""

import serial
import struct
import time

print("="*60)
print("  Quick Motor Test - /dev/ttyUSB0 @ 921600 baud")
print("="*60)

try:
    ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0.5)
    print("\n✓ Serial port opened")
    
    # Send enable command to motor 8
    print("  Sending enable to motor 8...")
    
    packet = bytearray([0xAA, 0x55, 0x01, 0x08])
    packet.extend(struct.pack('<I', 8))  # CAN ID 8
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # Enable
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    time.sleep(0.2)
    
    response = ser.read(100)
    
    if response and len(response) > 0:
        print(f"  ✅ MOTOR RESPONDED! ({len(response)} bytes)")
        print(f"  Response: {response.hex()}")
        print(f"\n✅ Motors are working at 921600 baud!")
        print(f"  DIP switches are back to original position\n")
    else:
        print(f"  ✗ No response")
        print(f"\n  Motors still not responding.")
        print(f"  Try:")
        print(f"  1. Power cycle the motors")
        print(f"  2. Unplug/replug USB cable")
        print(f"  3. Check DIP switch position\n")
    
    ser.close()
    
except Exception as e:
    print(f"\n✗ Error: {e}\n")

