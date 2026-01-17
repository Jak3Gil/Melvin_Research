#!/usr/bin/env python3
"""
Move Motor 9 slowly using CAN ID 9 (confirmed working)
"""
import serial
import time

def activate_motor(ser, can_id):
    """Activate motor"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
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
print("Moving Motor 9 Slowly - CAN ID 9")
print("="*70)
print()
print("WATCH MOTOR 9 - It should move slowly back and forth")
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
    
    # Activate Motor 9
    print("Activating Motor 9 (CAN ID 9)...")
    activate_motor(ser, 9)
    time.sleep(0.5)
    print("  [OK]")
    print()
    
    speed = 0.05  # Slow speed
    
    # Move forward slowly
    print(f"Moving Motor 9 FORWARD slowly (speed={speed})...")
    move_motor_jog(ser, 9, speed, 1)
    time.sleep(2.0)  # Move for 2 seconds
    
    # Stop
    print("Stopping...")
    stop_motor(ser, 9)
    time.sleep(1.0)
    
    # Move backward slowly
    print(f"Moving Motor 9 BACKWARD slowly (speed={-speed})...")
    move_motor_jog(ser, 9, -speed, 1)
    time.sleep(2.0)  # Move for 2 seconds
    
    # Stop
    print("Stopping...")
    stop_motor(ser, 9)
    time.sleep(1.0)
    
    # Move forward again
    print(f"Moving Motor 9 FORWARD again...")
    move_motor_jog(ser, 9, speed, 1)
    time.sleep(2.0)
    
    # Final stop
    print("Final stop...")
    stop_motor(ser, 9)
    time.sleep(0.5)
    
    ser.close()
    
    print()
    print("="*70)
    print("MOVEMENT COMPLETE")
    print("="*70)
    print()
    print("Did Motor 9 move? (Forward -> Backward -> Forward)")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

