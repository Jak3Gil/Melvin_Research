#!/usr/bin/env python3
"""
Test all 8 working motors (IDs 8-15)
Small back-and-forth movements to identify each motor
"""

import serial
import time

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
    time.sleep(0.1)
    
    return ser.read(200)

def activate_motor(ser, can_id):
    """Activate motor"""
    return send_command(ser, can_id, 0x00, [0x01, 0x00])

def deactivate_motor(ser, can_id):
    """Deactivate motor"""
    return send_command(ser, can_id, 0x00, [0x00, 0x00])

def move_motor(ser, can_id, speed):
    """
    Move motor at specified speed
    speed: 0.0 = stop, positive = forward, negative = backward
    """
    # Speed encoding
    if speed == 0.0:
        speed_val = 0x7fff
        flag = 0
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
        flag = 1
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
        flag = 1
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    data = [0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low]
    
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    packet.extend(data)
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.05)
    ser.read(200)

def stop_motor(ser, can_id):
    """Stop motor"""
    move_motor(ser, can_id, 0.0)

def test_motor_movement(ser, motor_id):
    """Test one motor with small back-and-forth movements"""
    print(f"\n{'='*70}")
    print(f"TESTING MOTOR {motor_id}")
    print(f"{'='*70}")
    
    # Activate
    print(f"Activating motor {motor_id}...")
    resp = activate_motor(ser, motor_id)
    if not resp or len(resp) == 0:
        print(f"  ❌ Motor {motor_id} not responding!")
        return False
    
    print(f"  ✅ Motor {motor_id} activated")
    time.sleep(0.5)
    
    # Small movements back and forth
    movements = [
        (0.08, "Forward slow", 1.5),
        (0.0, "Stop", 0.5),
        (-0.08, "Backward slow", 1.5),
        (0.0, "Stop", 0.5),
        (0.08, "Forward slow", 1.0),
        (0.0, "Stop", 0.5),
        (-0.08, "Backward slow", 1.0),
        (0.0, "Stop", 0.5),
    ]
    
    for speed, description, duration in movements:
        print(f"  {description}...", end='', flush=True)
        move_motor(ser, motor_id, speed)
        time.sleep(duration)
        print(" ✓")
    
    # Final stop
    print(f"  Final stop...")
    stop_motor(ser, motor_id)
    time.sleep(0.3)
    
    # Deactivate
    print(f"  Deactivating motor {motor_id}...")
    deactivate_motor(ser, motor_id)
    
    print(f"✅ Motor {motor_id} test complete")
    
    return True

print("="*70)
print("TEST ALL WORKING MOTORS (IDs 8-15)")
print("="*70)
print("\nEach motor will make small back-and-forth movements")
print("Watch to identify which physical motor is which ID")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    # Test motors 8-15
    working_motors = [8, 9, 10, 11, 12, 13, 14, 15]
    
    print("Testing motors in sequence...")
    print("Watch carefully to identify each motor!\n")
    
    time.sleep(2)  # Give time to get ready
    
    tested = []
    failed = []
    
    for motor_id in working_motors:
        success = test_motor_movement(ser, motor_id)
        
        if success:
            tested.append(motor_id)
        else:
            failed.append(motor_id)
        
        # Pause between motors
        print(f"\nPause before next motor...")
        time.sleep(2)
    
    ser.close()
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"✅ Successfully tested: {len(tested)} motors")
    for motor_id in tested:
        print(f"   Motor {motor_id} ✓")
    
    if failed:
        print(f"\n❌ Failed to test: {len(failed)} motors")
        for motor_id in failed:
            print(f"   Motor {motor_id} ✗")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Note which physical motor corresponds to each ID")
    print(f"   2. Power cycle motors to configure IDs 1-7")
    print(f"   3. Test all 15 motors once configured")
    
    print()
    
except KeyboardInterrupt:
    print(f"\n\n⚠️  Test interrupted by user")
    print(f"   Stopping all motors...")
    try:
        for motor_id in range(8, 16):
            stop_motor(ser, motor_id)
            deactivate_motor(ser, motor_id)
        ser.close()
    except:
        pass
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
