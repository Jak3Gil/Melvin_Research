#!/usr/bin/env python3
"""
Try moving Motors 7 and 9 directly when all motors are connected
Even if they don't respond to activation, maybe movement commands work?
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

port = 'COM6'
print("="*70)
print("Try Moving Motors 7 and 9 Directly (All Motors Connected)")
print("="*70)
print()
print("Strategy: Try movement commands directly, even without activation response")
print("          Maybe movement commands wake them up or work differently")
print()
print("WATCH MOTORS 7 AND 9 - Do they move?")
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
    
    # Test Motor 7 - Try various bytes that worked individually
    print("="*70)
    print("MOTOR 7 - Movement Test")
    print("="*70)
    print()
    
    motor7_bytes = [0x3c, 0x7c, 0xbc]  # Known bytes from individual tests
    
    for byte_val in motor7_bytes:
        print(f"Motor 7 - Byte 0x{byte_val:02x}:")
        print(f"  Trying movement command (speed=0.05) - WATCH MOTOR 7!")
        move_motor_jog(ser, byte_val, 0.05, 1)
        time.sleep(2.0)  # Move for 2 seconds
        
        # Stop
        print("  Stopping...")
        move_motor_jog(ser, byte_val, 0.0, 0)
        time.sleep(1.0)
        print()
    
    # Test Motor 9 - Try various bytes
    print("="*70)
    print("MOTOR 9 - Movement Test")
    print("="*70)
    print()
    
    motor9_bytes = [0xdc, 0x4c, 0x8c]  # Known bytes from individual tests
    
    for byte_val in motor9_bytes:
        print(f"Motor 9 - Byte 0x{byte_val:02x}:")
        print(f"  Trying movement command (speed=0.05) - WATCH MOTOR 9!")
        move_motor_jog(ser, byte_val, 0.05, 1)
        time.sleep(2.0)  # Move for 2 seconds
        
        # Stop
        print("  Stopping...")
        move_motor_jog(ser, byte_val, 0.0, 0)
        time.sleep(1.0)
        print()
    
    ser.close()
    
    print("="*70)
    print("MOVEMENT TEST COMPLETE")
    print("="*70)
    print()
    print("Did Motors 7 or 9 move?")
    print("  - If YES: Movement commands work even without activation response!")
    print("  - If NO: Need to capture Motor Studio's exact sequence")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

