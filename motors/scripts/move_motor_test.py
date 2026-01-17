#!/usr/bin/env python3
"""
Move motor using RobStride USB-to-CAN adapter protocol
Based on l91_motor.cpp moveJog() function
"""

import serial
import time
import struct

def send_command(ser, can_id, command_type, data):
    """Send command via RobStride adapter"""
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(command_type)
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(can_id)
    packet.extend(data)
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)
    
    return ser.read(200)

def activate_motor(ser, can_id):
    """Activate motor"""
    print(f"Activating motor {can_id}...")
    resp = send_command(ser, can_id, 0x00, [0x01, 0x00])
    if resp:
        print(f"  ✅ Activated: {resp.hex(' ')}")
    return resp

def deactivate_motor(ser, can_id):
    """Deactivate motor"""
    print(f"Deactivating motor {can_id}...")
    resp = send_command(ser, can_id, 0x00, [0x00, 0x00])
    if resp:
        print(f"  ✅ Deactivated: {resp.hex(' ')}")
    return resp

def move_motor(ser, can_id, speed, flag=1):
    """
    Move motor using JOG command
    Based on l91_motor.cpp moveJog()
    
    Args:
        can_id: Motor CAN ID
        speed: Speed value (0.0 = stop, positive = forward, negative = reverse)
        flag: 0=stop, 1=move
    """
    # Command format from l91_motor.cpp:
    # AT 90 07 e8 <can_id> 08 05 70 00 00 07 <flag> <speed_high> <speed_low> 0d 0a
    
    # Speed encoding (16-bit signed, where 0x7fff = 0.0)
    if speed == 0.0:
        speed_val = 0x7fff  # Stop
    elif speed > 0.0:
        # Positive speed: scale factor ~3283.0
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        # Negative speed
        speed_val = 0x7fff + int(speed * 3283.0)
    
    # Clamp to 16-bit range
    speed_val = max(0, min(0xFFFF, speed_val))
    
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    data = [0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low]
    
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(0x90)  # Command: MOVE_JOG
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(can_id)
    packet.extend(data)
    packet.extend([0x0d, 0x0a])
    
    print(f"Moving motor {can_id} at speed {speed:.2f} (flag={flag})...")
    print(f"  Speed value: 0x{speed_val:04X} (high=0x{speed_high:02X}, low=0x{speed_low:02X})")
    print(f"  Packet: {packet.hex(' ')}")
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)
    
    resp = ser.read(200)
    if resp:
        print(f"  ✅ Response: {resp.hex(' ')}")
    else:
        print(f"  ⚠️  No response")
    
    return resp

def stop_motor(ser, can_id):
    """Stop motor"""
    print(f"Stopping motor {can_id}...")
    return move_motor(ser, can_id, 0.0, 0)

print("="*70)
print("MOVE MOTOR TEST - RobStride Protocol")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    # Use motor at ID 20 (one of the responding IDs from Motor 1)
    motor_id = 20
    
    print("="*70)
    print(f"TEST 1: Activate Motor {motor_id}")
    print("="*70)
    
    activate_motor(ser, motor_id)
    time.sleep(0.5)
    
    # Test different speeds
    print("\n" + "="*70)
    print("TEST 2: Move Forward (Slow)")
    print("="*70)
    
    move_motor(ser, motor_id, 0.1, 1)  # Slow forward
    time.sleep(2)
    
    print("\n" + "="*70)
    print("TEST 3: Stop")
    print("="*70)
    
    stop_motor(ser, motor_id)
    time.sleep(1)
    
    print("\n" + "="*70)
    print("TEST 4: Move Backward (Slow)")
    print("="*70)
    
    move_motor(ser, motor_id, -0.1, 1)  # Slow backward
    time.sleep(2)
    
    print("\n" + "="*70)
    print("TEST 5: Stop")
    print("="*70)
    
    stop_motor(ser, motor_id)
    time.sleep(1)
    
    print("\n" + "="*70)
    print("TEST 6: Move Forward (Medium)")
    print("="*70)
    
    move_motor(ser, motor_id, 0.3, 1)  # Medium forward
    time.sleep(2)
    
    print("\n" + "="*70)
    print("TEST 7: Stop")
    print("="*70)
    
    stop_motor(ser, motor_id)
    time.sleep(1)
    
    print("\n" + "="*70)
    print("TEST 8: Deactivate Motor")
    print("="*70)
    
    deactivate_motor(ser, motor_id)
    
    ser.close()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("""
✅ Motor movement test complete!

The motor should have:
1. Activated
2. Moved forward slowly for 2 seconds
3. Stopped
4. Moved backward slowly for 2 seconds
5. Stopped
6. Moved forward at medium speed for 2 seconds
7. Stopped
8. Deactivated

If the motor moved, the RobStride protocol is working perfectly!
""")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

