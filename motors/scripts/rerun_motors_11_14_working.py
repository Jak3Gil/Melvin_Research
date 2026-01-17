#!/usr/bin/env python3
"""
Rerun the working movement sequences for Motors 11 and 14
Capture what commands work so we can replicate for Motors 7 and 9
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
print("Rerun Working Motors 11 and 14 - Full Command Sequence")
print("="*70)
print()
print("Motor 11: Uses byte 0x58 (or 0x9c)")
print("Motor 14: Uses byte 0x70")
print()
print("Starting in 3 seconds...")
time.sleep(3)
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Motor 11 - Full sequence
    print("="*70)
    print("MOTOR 11 - Full Activation & Movement Sequence")
    print("="*70)
    print()
    
    print("Step 1: Activate Motor 11 (byte 0x58)...")
    activate_motor(ser, 0x58)
    print("  [OK]")
    
    print("Step 2: Load parameters...")
    load_params(ser, 0x58)
    print("  [OK]")
    
    time.sleep(0.5)
    
    speed = 0.05
    
    print(f"Step 3: Move FORWARD (speed={speed}) - WATCH MOTOR 11!")
    move_motor_jog(ser, 0x58, speed, 1)
    time.sleep(3.0)
    
    print("Step 4: Stop...")
    stop_motor(ser, 0x58)
    time.sleep(1.0)
    
    print(f"Step 5: Move BACKWARD (speed={-speed}) - WATCH MOTOR 11!")
    move_motor_jog(ser, 0x58, -speed, 1)
    time.sleep(3.0)
    
    print("Step 6: Final stop...")
    stop_motor(ser, 0x58)
    time.sleep(2.0)
    
    # Motor 14 - Full sequence
    print()
    print("="*70)
    print("MOTOR 14 - Full Activation & Movement Sequence")
    print("="*70)
    print()
    
    print("Step 1: Activate Motor 14 (byte 0x70)...")
    activate_motor(ser, 0x70)
    print("  [OK]")
    
    print("Step 2: Load parameters...")
    load_params(ser, 0x70)
    print("  [OK]")
    
    time.sleep(0.5)
    
    print(f"Step 3: Move FORWARD (speed={speed}) - WATCH MOTOR 14!")
    move_motor_jog(ser, 0x70, speed, 1)
    time.sleep(3.0)
    
    print("Step 4: Stop...")
    stop_motor(ser, 0x70)
    time.sleep(1.0)
    
    print(f"Step 5: Move BACKWARD (speed={-speed}) - WATCH MOTOR 14!")
    move_motor_jog(ser, 0x70, -speed, 1)
    time.sleep(3.0)
    
    print("Step 6: Final stop...")
    stop_motor(ser, 0x70)
    time.sleep(1.0)
    
    ser.close()
    
    print()
    print("="*70)
    print("SEQUENCE COMPLETE")
    print("="*70)
    print()
    print("Command sequence that works:")
    print("  1. Initialize adapter (AT+AT, AT+A)")
    print("  2. Activate motor (AT 00 07 e8 <byte> 01 00)")
    print("  3. Load parameters (AT 20 07 e8 <byte> 08 00 c4...)")
    print("  4. Movement commands (AT 90 07 e8 <byte> ...)")
    print()
    print("Motors 11 and 14 use:")
    print("  Motor 11: byte 0x58")
    print("  Motor 14: byte 0x70")
    print()
    print("Now we need to find the correct bytes for Motors 7 and 9!")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

