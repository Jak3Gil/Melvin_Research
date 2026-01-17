#!/usr/bin/env python3
"""
Slow test to identify which motor moves with which byte
Longer movements and pauses so user can identify the motor
"""
import serial
import time

def activate_motor(ser, byte_val):
    """Activate motor"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)

def load_params(ser, byte_val):
    """Load motor parameters"""
    packet = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                        0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)

def move_motor_jog(ser, byte_val, speed, flag=1):
    """Move motor using JOG command"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, byte_val])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)

def stop_motor(ser, byte_val):
    """Stop motor"""
    move_motor_jog(ser, byte_val, 0.0, 0)

port = 'COM6'
print("="*70)
print("SLOW TEST - Identify Which Motor Moves")
print("="*70)
print()
print("Each test will move for 5 seconds")
print("Watch carefully which motor moves!")
print()
print("Starting in 5 seconds...")
time.sleep(5)
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Test all candidate bytes with longer movements
    test_bytes = [
        # Motor 7 candidates
        (0x38, "Motor 7 candidate 1"),
        (0x78, "Motor 7 candidate 2"),
        (0x34, "Motor 7 candidate 3"),
        (0x74, "Motor 7 candidate 4"),
        # Motor 9 candidates
        (0x08, "Motor 9 candidate 1"),
        (0x48, "Motor 9 candidate 2"),
        (0x44, "Motor 9 candidate 3"),
    ]
    
    speed = 0.1
    
    for byte_val, description in test_bytes:
        print("="*70)
        print(f"TESTING: {description} (byte 0x{byte_val:02x})")
        print("="*70)
        print()
        print(f"WATCH ALL MOTORS - Which one moves?")
        print(f"Motor will move FORWARD for 5 seconds")
        print()
        print("Starting in 3 seconds...")
        time.sleep(3)
        print()
        
        # Full activation sequence
        activate_motor(ser, byte_val)
        load_params(ser, byte_val)
        time.sleep(0.5)
        
        # Move forward for 5 seconds
        print(f"MOVING FORWARD NOW - WATCH WHICH MOTOR MOVES!")
        print(f"  (Moving for 5 seconds)")
        move_motor_jog(ser, byte_val, speed, 1)
        time.sleep(5.0)
        
        # Stop
        print("STOPPING...")
        stop_motor(ser, byte_val)
        time.sleep(2.0)
        
        print()
        print("Which motor moved? (1, 3, 7, 9, 11, 14, or none?)")
        print("Pausing for 3 seconds before next test...")
        time.sleep(3)
        print()
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Please tell me which byte made which motor move!")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

