#!/usr/bin/env python3
"""
Apply the exact working sequence from Motors 11/14 to Motors 7 and 9
Using Motor Studio byte encodings: 0x4c (Motor 9), 0x3c and 0x7c (Motor 7)
"""
import serial
import time

def activate_motor(ser, can_id):
    """Activate motor"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)

def load_params(ser, can_id):
    """Load motor parameters"""
    packet = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                        0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)

def move_motor_jog(ser, can_id, speed, flag=1):
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
    
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)

def stop_motor(ser, can_id):
    """Stop motor"""
    move_motor_jog(ser, can_id, 0.0, 0)

port = 'COM6'
print("="*70)
print("Apply Working Sequence to Motors 7 and 9")
print("="*70)
print()
print("Using Motor Studio byte encodings:")
print("  Motor 9: byte 0x4c (extended)")
print("  Motor 7: byte 0x3c (extended) and 0x7c (standard)")
print()
print("Starting in 3 seconds...")
time.sleep(3)
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Step 1: Initialize adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Motor 9 - byte 0x4c
    print("="*70)
    print("MOTOR 9 - Using byte 0x4c (Extended format)")
    print("="*70)
    print()
    
    print("Step 2: Activate Motor 9 (byte 0x4c)...")
    activate_motor(ser, 0x4c)
    print("  [OK]")
    
    print("Step 3: Load parameters...")
    load_params(ser, 0x4c)
    print("  [OK]")
    
    time.sleep(0.5)
    
    speed = 0.05
    
    print(f"Step 4: Move FORWARD - WATCH MOTOR 9!")
    move_motor_jog(ser, 0x4c, speed, 1)
    time.sleep(3.0)
    
    print("Step 5: Stop...")
    stop_motor(ser, 0x4c)
    time.sleep(1.0)
    
    print(f"Step 6: Move BACKWARD - WATCH MOTOR 9!")
    move_motor_jog(ser, 0x4c, -speed, 1)
    time.sleep(3.0)
    
    print("Step 7: Final stop...")
    stop_motor(ser, 0x4c)
    time.sleep(2.0)
    
    # Motor 7 - Try byte 0x3c (extended)
    print()
    print("="*70)
    print("MOTOR 7 - Using byte 0x3c (Extended format)")
    print("="*70)
    print()
    
    print("Step 2: Activate Motor 7 (byte 0x3c)...")
    activate_motor(ser, 0x3c)
    print("  [OK]")
    
    print("Step 3: Load parameters...")
    load_params(ser, 0x3c)
    print("  [OK]")
    
    time.sleep(0.5)
    
    print(f"Step 4: Move FORWARD - WATCH MOTOR 7!")
    move_motor_jog(ser, 0x3c, speed, 1)
    time.sleep(3.0)
    
    print("Step 5: Stop...")
    stop_motor(ser, 0x3c)
    time.sleep(1.0)
    
    print(f"Step 6: Move BACKWARD - WATCH MOTOR 7!")
    move_motor_jog(ser, 0x3c, -speed, 1)
    time.sleep(3.0)
    
    print("Step 7: Final stop...")
    stop_motor(ser, 0x3c)
    time.sleep(2.0)
    
    # Motor 7 - Try byte 0x7c (standard)
    print()
    print("="*70)
    print("MOTOR 7 - Using byte 0x7c (Standard format)")
    print("="*70)
    print()
    
    print("Step 2: Activate Motor 7 (byte 0x7c)...")
    activate_motor(ser, 0x7c)
    print("  [OK]")
    
    print("Step 3: Load parameters...")
    load_params(ser, 0x7c)
    print("  [OK]")
    
    time.sleep(0.5)
    
    print(f"Step 4: Move FORWARD - WATCH MOTOR 7!")
    move_motor_jog(ser, 0x7c, speed, 1)
    time.sleep(3.0)
    
    print("Step 5: Stop...")
    stop_motor(ser, 0x7c)
    time.sleep(1.0)
    
    print(f"Step 6: Move BACKWARD - WATCH MOTOR 7!")
    move_motor_jog(ser, 0x7c, -speed, 1)
    time.sleep(3.0)
    
    print("Step 7: Final stop...")
    stop_motor(ser, 0x7c)
    time.sleep(1.0)
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Which motors moved?")
    print("  - Motor 9 with byte 0x4c?")
    print("  - Motor 7 with byte 0x3c?")
    print("  - Motor 7 with byte 0x7c?")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

