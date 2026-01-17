#!/usr/bin/env python3
"""Quick hardware diagnostic - no user input required"""

import serial
import struct
import time

def test_motor_response(port, baud, motor_id):
    """Test if a specific motor responds"""
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
        
        # Build enable packet
        packet = bytearray([0xAA, 0x55, 0x01, 0x08])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        ser.write(packet)
        ser.flush()
        time.sleep(0.2)
        
        response = ser.read(100)
        ser.close()
        
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

print("="*70)
print("QUICK MOTOR DIAGNOSTIC")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

print(f"\nPort: {port}")
print(f"Baud: {baud}")

# Test known motor IDs
test_ids = [8, 9, 10, 20, 31, 32, 64, 72]

print(f"\nTesting {len(test_ids)} known motor IDs...")
print("-"*70)

found = []

for motor_id in test_ids:
    print(f"Motor {motor_id:3d}...", end=" ")
    response = test_motor_response(port, baud, motor_id)
    
    if response and len(response) > 4:
        print(f"✓ RESPONDS ({len(response)} bytes)")
        print(f"         Response: {response.hex(' ')}")
        found.append(motor_id)
    else:
        print("✗")

print("\n" + "="*70)
print("RESULTS")
print("="*70)

if found:
    print(f"\n✅ Found {len(found)} responding motor(s)!")
    print(f"   IDs: {found}")
    print(f"\n   Motors are working at {baud} baud")
    print(f"   You can now run configuration script")
else:
    print(f"\n❌ No motors responding")
    print(f"\n   Possible issues:")
    print(f"   1. Motors not powered on")
    print(f"   2. CAN bus not connected (check CAN-H, CAN-L, GND)")
    print(f"   3. Missing termination (need 120Ω at both ends)")
    print(f"   4. Wrong baud rate")
    print(f"\n   Actions:")
    print(f"   1. Check motor power LEDs")
    print(f"   2. Verify CAN bus wiring")
    print(f"   3. Add 120Ω termination resistors")
    print(f"   4. Power cycle motors")

print()

