#!/usr/bin/env python3
"""
Move Motors 7 and 9 using extended format bytes (0x3c, 0x4c)
Use extended format for activation, then try movement with same bytes
"""
import serial
import time

def send_and_get_response(ser, cmd, timeout=0.5):
    """Send command and get response"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.03)
    
    return response.hex() if len(response) > 0 else None

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
print("Move Motors 7 and 9 - Extended Format")
print("="*70)
print()
print("Motor 7: Extended format byte 0x3c")
print("Motor 9: Extended format byte 0x4c")
print()
print("WATCH MOTORS 7 AND 9 - Do they move?")
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
    
    # Motor 7 - Extended format activation, then movement
    print("="*70)
    print("MOTOR 7 - Extended Format (byte 0x3c)")
    print("="*70)
    print()
    
    # Activate with extended format query
    print("Activating Motor 7 (extended format 0x3c)...")
    cmd_7_query = bytes.fromhex("41542007e83c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_7_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    speed = 0.05
    
    # Move forward
    print(f"Moving Motor 7 FORWARD (speed={speed}) - WATCH MOTOR 7!")
    move_motor_jog(ser, 0x3c, speed, 1)
    time.sleep(3.0)
    
    # Stop
    print("Stopping...")
    stop_motor(ser, 0x3c)
    time.sleep(1.0)
    
    # Move backward
    print(f"Moving Motor 7 BACKWARD (speed={-speed}) - WATCH MOTOR 7!")
    move_motor_jog(ser, 0x3c, -speed, 1)
    time.sleep(3.0)
    
    # Final stop
    print("Final stop...")
    stop_motor(ser, 0x3c)
    time.sleep(1.0)
    
    # Motor 9 - Extended format activation, then movement
    print()
    print("="*70)
    print("MOTOR 9 - Extended Format (byte 0x4c)")
    print("="*70)
    print()
    
    # Activate with extended format query
    print("Activating Motor 9 (extended format 0x4c)...")
    cmd_9_query = bytes.fromhex("41542007e84c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_9_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Move forward
    print(f"Moving Motor 9 FORWARD (speed={speed}) - WATCH MOTOR 9!")
    move_motor_jog(ser, 0x4c, speed, 1)
    time.sleep(3.0)
    
    # Stop
    print("Stopping...")
    stop_motor(ser, 0x4c)
    time.sleep(1.0)
    
    # Move backward
    print(f"Moving Motor 9 BACKWARD (speed={-speed}) - WATCH MOTOR 9!")
    move_motor_jog(ser, 0x4c, -speed, 1)
    time.sleep(3.0)
    
    # Final stop
    print("Final stop...")
    stop_motor(ser, 0x4c)
    time.sleep(1.0)
    
    ser.close()
    
    print()
    print("="*70)
    print("MOVEMENT TEST COMPLETE")
    print("="*70)
    print()
    print("Did Motors 7 and 9 move?")
    print("  - Motor 7 with byte 0x3c?")
    print("  - Motor 9 with byte 0x4c?")
    print()
    print("If they moved, we've confirmed:")
    print("  - Extended format bytes work for movement")
    print("  - Motors 7 and 9 can be controlled!")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

