#!/usr/bin/env python3
"""
Move Motor 8 slowly using byte 0x44 (extended format)
Motor 8: 41542007e8440800c40000000000000d0a (extended format, byte 0x44)
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

def move_motor_jog_extended(ser, byte_val, speed, flag=1):
    """Move motor using JOG command (extended format)"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    # Extended format JOG command
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, byte_val])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)

def stop_motor(ser, byte_val):
    """Stop motor"""
    move_motor_jog_extended(ser, byte_val, 0.0, 0)

port = 'COM6'
print("="*70)
print("Move Motor 8 Slowly - Byte 0x44 (Extended Format)")
print("="*70)
print()
print("Motor 8: Extended format 41542007e8440800c40000000000000d0a (byte 0x44)")
print()
print("WATCH MOTOR 8 - Does it move?")
print()
print("Starting in 3 seconds...")
time.sleep(3)
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing USB-CAN adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Motor 8 - Activate with extended format
    print("Activating Motor 8 (extended format, byte 0x44)...")
    cmd_8_act = bytes.fromhex("41542007e8440800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_8_act, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    speed = 0.05  # Slow speed
    
    # Move forward
    print(f"\nMoving Motor 8 FORWARD slowly (speed={speed}) - WATCH MOTOR 8!")
    move_motor_jog_extended(ser, 0x44, speed, 1)
    time.sleep(3.0)
    
    # Stop
    print("Stopping...")
    stop_motor(ser, 0x44)
    time.sleep(1.0)
    
    # Move backward
    print(f"Moving Motor 8 BACKWARD slowly (speed={-speed}) - WATCH MOTOR 8!")
    move_motor_jog_extended(ser, 0x44, -speed, 1)
    time.sleep(3.0)
    
    # Final stop
    print("Final stop...")
    stop_motor(ser, 0x44)
    time.sleep(1.0)
    
    ser.close()
    
    print()
    print("="*70)
    print("MOVEMENT TEST COMPLETE")
    print("="*70)
    print()
    print("Did Motor 8 move?")
    print("  - If YES: Byte 0x44 extended format works for movement commands!")
    print("  - If NO: May need different byte or command format")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

