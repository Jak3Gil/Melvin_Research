#!/usr/bin/env python3
"""
Test Motor Studio's exact command formats for Motors 7 and 9
Motor 9: 41542007e84c0800c40000000000000d0a (extended, byte 0x4c)
Motor 7: 41542007e83c0800c40000000000000d0a (extended, byte 0x3c)
        41540007e87c01000d0a (standard, byte 0x7c)
"""
import serial
import time

def send_and_get_response(ser, cmd_hex, description, timeout=0.5):
    """Send command from hex string and get response"""
    cmd = bytes.fromhex(cmd_hex.replace(' ', ''))
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.05)
    
    resp_hex = response.hex() if len(response) > 0 else None
    print(f"  {description}")
    if resp_hex:
        print(f"    Response: {resp_hex[:60]}...")
        return True, resp_hex
    else:
        print(f"    No response")
        return False, None

def move_motor_jog(ser, can_id, speed, flag=1):
    """Move motor using JOG command - try both actual ID and encoded bytes"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    # Try with actual CAN ID
    cmd1 = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    cmd1.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    cmd1.extend([0x0d, 0x0a])
    
    ser.write(cmd1)
    ser.flush()
    time.sleep(0.1)

port = 'COM6'
print("="*70)
print("Test Motor Studio Exact Formats for Motors 7 and 9")
print("="*70)
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
    
    # Test Motor 9 - Extended format (0x4c)
    print("="*70)
    print("MOTOR 9 - Extended Format (byte 0x4c)")
    print("="*70)
    print()
    
    cmd_9_extended = "41542007e84c0800c40000000000000d0a"
    got_resp, resp = send_and_get_response(ser, cmd_9_extended, "Motor 9 Extended Query", timeout=1.0)
    time.sleep(0.5)
    
    # Now try activation and movement with byte 0x4c
    print("\nActivating Motor 9 with byte 0x4c...")
    activate_cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x4c, 0x01, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(activate_cmd)
    ser.flush()
    time.sleep(0.5)
    resp = ser.read(200)
    if resp:
        print(f"  Response: {resp.hex()[:60]}...")
    else:
        print("  No response")
    
    # Try movement with byte 0x4c
    print("\nTrying movement with byte 0x4c...")
    print("  WATCH MOTOR 9 - Does it move?")
    move_motor_jog(ser, 0x4c, 0.1, 1)
    time.sleep(3.0)
    
    # Stop
    move_motor_jog(ser, 0x4c, 0.0, 0)
    time.sleep(1.0)
    
    print()
    print("="*70)
    print("MOTOR 7 - Extended Format (byte 0x3c) and Standard (byte 0x7c)")
    print("="*70)
    print()
    
    # Test Motor 7 - Extended format (0x3c)
    cmd_7_extended = "41542007e83c0800c40000000000000d0a"
    got_resp, resp = send_and_get_response(ser, cmd_7_extended, "Motor 7 Extended Query", timeout=1.0)
    time.sleep(0.5)
    
    # Test Motor 7 - Standard format (0x7c)
    cmd_7_standard = "41540007e87c01000d0a"
    got_resp, resp = send_and_get_response(ser, cmd_7_standard, "Motor 7 Standard Query", timeout=1.0)
    time.sleep(0.5)
    
    # Try activation and movement with byte 0x3c (extended)
    print("\nActivating Motor 7 with byte 0x3c (extended)...")
    activate_cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x3c, 0x01, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(activate_cmd)
    ser.flush()
    time.sleep(0.5)
    resp = ser.read(200)
    if resp:
        print(f"  Response: {resp.hex()[:60]}...")
    else:
        print("  No response")
    
    # Try movement with byte 0x3c
    print("\nTrying movement with byte 0x3c...")
    print("  WATCH MOTOR 7 - Does it move?")
    move_motor_jog(ser, 0x3c, 0.1, 1)
    time.sleep(3.0)
    move_motor_jog(ser, 0x3c, 0.0, 0)
    time.sleep(1.0)
    
    # Try activation and movement with byte 0x7c (standard)
    print("\nActivating Motor 7 with byte 0x7c (standard)...")
    activate_cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x7c, 0x01, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(activate_cmd)
    ser.flush()
    time.sleep(0.5)
    resp = ser.read(200)
    if resp:
        print(f"  Response: {resp.hex()[:60]}...")
    else:
        print("  No response")
    
    # Try movement with byte 0x7c
    print("\nTrying movement with byte 0x7c...")
    print("  WATCH MOTOR 7 - Does it move?")
    move_motor_jog(ser, 0x7c, 0.1, 1)
    time.sleep(3.0)
    move_motor_jog(ser, 0x7c, 0.0, 0)
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

