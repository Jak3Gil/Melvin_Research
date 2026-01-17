#!/usr/bin/env python3
"""
Test different baud rates on /dev/ttyUSB0
DIP switches might change the baud rate, not the protocol
"""

import serial
import struct
import time

BAUDRATES = [
    9600,
    19200,
    38400,
    57600,
    115200,
    230400,
    460800,
    921600,
    1000000,
    2000000,
]

def send_l91(ser, can_id, data):
    """Send L91 protocol command"""
    packet = bytearray([0xAA, 0x55, 0x01, 0x08])
    packet.extend(struct.pack('<I', can_id))
    packet.extend(data)
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    ser.write(packet)
    time.sleep(0.2)
    return ser.read(100)

print("="*60)
print("  Testing All Baud Rates on /dev/ttyUSB0")
print("="*60)
print("\nDIP switches might have changed the baud rate...\n")

enable_cmd = bytes([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

for baudrate in BAUDRATES:
    print(f"Testing {baudrate:>7} baud... ", end='', flush=True)
    
    try:
        ser = serial.Serial('/dev/ttyUSB0', baudrate, timeout=0.3)
        response = send_l91(ser, 8, enable_cmd)
        ser.close()
        
        if response and len(response) > 0:
            print(f"✓ RESPONSE! ({len(response)} bytes)")
            print(f"  Data: {response.hex()}")
            print(f"\n✅ Motors respond at {baudrate} baud!")
            print(f"   Update your scripts to use this baud rate.\n")
            break
        else:
            print("✗ No response")
            
    except Exception as e:
        print(f"✗ Error: {e}")

else:
    print("\n❌ No baud rate worked")
    print("\nThis means:")
    print("1. DIP switches changed to a mode we haven't tested")
    print("2. Motors need power cycle")
    print("3. Different protocol entirely")
    print("\nPlease check the RobStride controller documentation")
    print("for DIP switch settings.\n")

