#!/usr/bin/env python3
"""
Fix address masking issue
Try different configuration approaches to truly separate motors
"""

import serial
import time
import struct

def send_command(ser, can_id, command_type, data):
    """Send command via RobStride adapter"""
    packet = bytearray([0x41, 0x54])
    packet.append(command_type)
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(can_id)
    packet.extend(data)
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.2)
    
    return ser.read(200)

def activate_motor(ser, can_id):
    return send_command(ser, can_id, 0x00, [0x01, 0x00])

def move_motor_test(ser, can_id):
    """Briefly move motor to test"""
    # Activate
    activate_motor(ser, can_id)
    time.sleep(0.2)
    
    # Move
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, 0x01, 0x81, 0x48])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(1.0)
    
    # Stop
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, 0x00, 0x7f, 0xff])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()

print("="*70)
print("DIAGNOSE ADDRESS MASKING ISSUE")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected\n")
    
    print("="*70)
    print("TEST 1: Which IDs control Motor 2?")
    print("="*70)
    
    print("\nTesting IDs 8-39 (one at a time)...")
    print("Watch which motor moves for each ID:\n")
    
    test_ids = [8, 12, 16, 20, 24, 28, 32, 36]
    
    for test_id in test_ids:
        input(f"\nPress ENTER to test ID {test_id}...")
        print(f"Moving motor at ID {test_id}...")
        move_motor_test(ser, test_id)
        print(f"Did Motor 2 move? (y/n): ", end='', flush=True)
    
    print("\n\n" + "="*70)
    print("TEST 2: Check if multiple physical motors exist")
    print("="*70)
    
    print("\nTesting IDs 64-79...")
    
    test_ids_2 = [64, 68, 72, 76]
    
    for test_id in test_ids_2:
        input(f"\nPress ENTER to test ID {test_id}...")
        print(f"Moving motor at ID {test_id}...")
        move_motor_test(ser, test_id)
        print(f"Which motor moved? Motor number: ", end='', flush=True)
    
    ser.close()
    
    print("\n\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)
    
    print("""
Based on your observation:

If ALL IDs moved the SAME motor:
  → Only 1-2 physical motors are connected/powered
  → The other 13-14 motors are either:
    - Not powered
    - Not on this CAN bus
    - Disconnected

If DIFFERENT IDs moved DIFFERENT motors:
  → Multiple motors ARE present
  → They have overlapping address masks
  → Need different configuration method

SOLUTION OPTIONS:

1. POWER CHECK:
   - Physically count how many motors have power LEDs ON
   - Should be 15 motors with LEDs
   - If less, some motors don't have power

2. WIRING CHECK:
   - Are all 15 motors on the SAME CAN bus cable?
   - Or are some on a different/disconnected bus?

3. FACTORY RESET:
   - Motors may need factory reset to clear address masks
   - Requires RobStride Motor Studio software or special command

4. DIFFERENT PROTOCOL:
   - May need to use MIT protocol instead of L91
   - Or use SocketCAN with proper CAN frames

Please tell me:
- How many motors have power LEDs ON?
- Did different IDs move different motors?
""")
    
except KeyboardInterrupt:
    print("\n\nTest interrupted")
    ser.close()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

