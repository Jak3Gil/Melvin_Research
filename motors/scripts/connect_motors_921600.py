#!/usr/bin/env python3
"""Connect to motors via USB-to-CAN at 921600 baud"""
import serial
import struct
import time

# Configuration
PORT = '/dev/ttyUSB1'
BAUD = 921600

print(f'Connecting to motors via {PORT} at {BAUD} baud...')
print()

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.5)
    print(f'✅ Connected to {PORT}')
    print(f'   Baud rate: {BAUD}')
    print()
    
    # Send detection command
    print('Sending detection command (AT+AT)...')
    ser.write(b'AT+AT\r\n')
    time.sleep(0.2)
    response = ser.read(100)
    
    if response:
        print(f'✅ Adapter responded: {response.decode(errors="ignore")}')
    else:
        print('⚠️  No response to AT command (may be normal for some adapters)')
    print()
    
    # Test known motor IDs from previous scans
    known_motors = [8, 16, 21, 31, 64, 72]
    print('Testing known motor IDs from previous scans:')
    print(f'IDs to test: {known_motors}')
    print()
    
    found_motors = []
    for motor_id in known_motors:
        print(f'Testing ID {motor_id}...', end=' ')
        
        # Build enable packet (L91 protocol)
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(0.15)
        response = ser.read(100)
        
        if response and len(response) > 5:
            print(f'✅ FOUND! ({len(response)} bytes)')
            found_motors.append(motor_id)
        else:
            print('No response')
        
        time.sleep(0.05)
    
    print()
    print('=' * 60)
    print(f'CONNECTED MOTORS: {len(found_motors)} found')
    print('=' * 60)
    if found_motors:
        print(f'Motor IDs: {found_motors}')
        print()
        print('You can now control these motors using the L91 protocol')
        print(f'Port: {PORT}')
        print(f'Baud: {BAUD}')
    else:
        print('⚠️  No motors responded. They may be powered off or at different IDs.')
    print()
    
    ser.close()
    print('✅ Connection test complete')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

