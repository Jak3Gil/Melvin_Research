#!/usr/bin/env python3
"""
Test Motor 1 movement to verify our command format works
Motor 1 is known to work, so if it moves, our commands are correct
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
print("Test Motor 1 Movement - Verify Command Format")
print("="*70)
print()
print("Motor 1 uses CAN ID 1 (actual ID)")
print("Testing if our movement commands work with a known motor")
print()
print("WATCH MOTOR 1 - Does it move?")
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
    
    # Activate Motor 1 using actual CAN ID 1
    print("Activating Motor 1 (CAN ID 1)...")
    activate_motor(ser, 1)
    load_params(ser, 1)
    time.sleep(0.5)
    print("  [OK]")
    print()
    
    speed = 0.1
    
    # Move forward
    print("MOVING FORWARD - WATCH MOTOR 1!")
    move_motor_jog(ser, 1, speed, 1)
    time.sleep(3.0)
    
    # Stop
    print("STOPPING...")
    stop_motor(ser, 1)
    time.sleep(1.5)
    
    # Move backward
    print("MOVING BACKWARD - WATCH MOTOR 1!")
    move_motor_jog(ser, 1, -speed, 1)
    time.sleep(3.0)
    
    # Final stop
    print("FINAL STOP...")
    stop_motor(ser, 1)
    time.sleep(0.5)
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Did Motor 1 move?")
    print("  - If YES: Our command format works, Motor 1 needs CAN ID 1")
    print("  - If NO: Motor 1 might need different CAN ID or command format")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

