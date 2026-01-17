#!/usr/bin/env python3
"""
Test which motor actually moves when we send commands to CAN ID 9
We're getting responses but need to see which physical motor moves
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
print("Test: Which Motor Moves with CAN ID 9?")
print("="*70)
print()
print("WATCH ALL MOTORS - Which one moves?")
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
    
    # Activate and prepare
    print("Activating CAN ID 9...")
    activate_motor(ser, 9)
    load_params(ser, 9)
    time.sleep(0.5)
    print("  [OK]")
    print()
    
    speed = 0.1  # Slightly faster to make movement obvious
    
    # Move forward
    print("MOVING FORWARD - WATCH ALL MOTORS!")
    print("  Which motor is moving? (1, 3, 7, 9, 11, 14, or none?)")
    move_motor_jog(ser, 9, speed, 1)
    time.sleep(3.0)  # Move for 3 seconds
    
    # Stop
    print("STOPPING...")
    stop_motor(ser, 9)
    time.sleep(1.5)
    
    # Move backward
    print("MOVING BACKWARD - WATCH ALL MOTORS!")
    print("  Which motor is moving? (1, 3, 7, 9, 11, 14, or none?)")
    move_motor_jog(ser, 9, -speed, 1)
    time.sleep(3.0)  # Move for 3 seconds
    
    # Final stop
    print("FINAL STOP...")
    stop_motor(ser, 9)
    time.sleep(0.5)
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Which motor moved?")
    print("  - If Motor 1 moved: CAN ID 9 might be mapped to Motor 1")
    print("  - If Motor 9 moved: CAN ID 9 correctly controls Motor 9")
    print("  - If a different motor moved: There's address mapping happening")
    print("  - If nothing moved: Motor needs different activation/enable")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

