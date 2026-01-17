#!/usr/bin/env python3
"""
Test different byte patterns for Motors 7 and 9 movement
Motor 11: query uses 0x9c, movement uses 0x58 (different!)
Motor 14: query uses 0x74, movement uses 0x70 (similar)

Motor 7: query uses 0x3c or 0x7c
Motor 9: query uses 0x4c

Try variations and patterns based on Motor 11/14 relationships
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
print("Test Movement Byte Patterns for Motors 7 and 9")
print("="*70)
print()
print("Patterns observed:")
print("  Motor 11: query 0x9c -> movement 0x58 (0x9c - 0x44 = 0x58)")
print("  Motor 14: query 0x74 -> movement 0x70 (0x74 - 0x04 = 0x70)")
print()
print("Testing variations for Motors 7 and 9...")
print()
print("Starting in 3 seconds...")
time.sleep(3)
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
    
    # Motor 7 candidates
    # Query uses 0x3c or 0x7c
    # Try: 0x3c-0x44=0x-8 (invalid), 0x3c-0x04=0x38, 0x7c-0x44=0x38, 0x7c-0x04=0x78
    motor_7_candidates = [
        0x38,  # 0x3c - 0x04 or 0x7c - 0x44
        0x78,  # 0x7c - 0x04
        0x3c,  # Original query byte (already tested)
        0x7c,  # Original query byte (already tested)
        0x34,  # Other variations
        0x74,  # Similar to Motor 14
    ]
    
    # Motor 9 candidates
    # Query uses 0x4c
    # Try: 0x4c-0x44=0x08, 0x4c-0x04=0x48
    motor_9_candidates = [
        0x08,  # 0x4c - 0x44
        0x48,  # 0x4c - 0x04
        0x4c,  # Original query byte (already tested)
        0x44,  # Other variations
    ]
    
    speed = 0.1
    
    print("="*70)
    print("MOTOR 7 - Testing movement bytes")
    print("="*70)
    print()
    
    for byte_val in motor_7_candidates:
        print(f"Testing byte 0x{byte_val:02x} - WATCH MOTOR 7!")
        
        # Full sequence
        activate_motor(ser, byte_val)
        load_params(ser, byte_val)
        time.sleep(0.3)
        
        # Move forward
        move_motor_jog(ser, byte_val, speed, 1)
        time.sleep(2.0)
        
        # Stop
        stop_motor(ser, byte_val)
        time.sleep(1.5)
        
        print(f"  Did Motor 7 move with byte 0x{byte_val:02x}?")
        print()
    
    print()
    print("="*70)
    print("MOTOR 9 - Testing movement bytes")
    print("="*70)
    print()
    
    for byte_val in motor_9_candidates:
        print(f"Testing byte 0x{byte_val:02x} - WATCH MOTOR 9!")
        
        # Full sequence
        activate_motor(ser, byte_val)
        load_params(ser, byte_val)
        time.sleep(0.3)
        
        # Move forward
        move_motor_jog(ser, byte_val, speed, 1)
        time.sleep(2.0)
        
        # Stop
        stop_motor(ser, byte_val)
        time.sleep(1.5)
        
        print(f"  Did Motor 9 move with byte 0x{byte_val:02x}?")
        print()
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Which bytes made which motors move?")
    print("  Please report which byte values worked!")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

