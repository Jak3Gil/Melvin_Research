#!/usr/bin/env python3
"""
Activate Motors 7 and 9 using correct bytes (0xbc, 0x8c) FIRST
Then activate other motors
Using both Motor Studio exact commands and extended format
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

port = 'COM6'
print("="*70)
print("Activate Motors 7 and 9 - Correct Bytes FIRST")
print("="*70)
print()
print("Motor 7: byte 0xbc (Motor Studio exact)")
print("Motor 9: byte 0x8c (Motor Studio exact)")
print()
print("Strategy: Send these commands FIRST, then other motors")
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
    
    # STEP 1: Motors 7 and 9 FIRST with correct bytes
    print("="*70)
    print("STEP 1: Motors 7 and 9 FIRST (Correct Bytes)")
    print("="*70)
    print()
    
    # Motor 7 - Motor Studio exact command
    print("Motor 7 - Motor Studio exact command (0xbc)...")
    cmd_7_exact = bytes.fromhex("41540007ebc401000d0a")
    resp = send_and_get_response(ser, cmd_7_exact, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.3)
    
    # Motor 7 - Extended format with byte 0xbc
    print("Motor 7 - Extended format (0x20, 0xbc)...")
    cmd_7_ext = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0xbc, 0x08, 0x00,
                           0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_7_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.3)
    
    # Motor 9 - Motor Studio exact command
    print("Motor 9 - Motor Studio exact command (0x8c)...")
    cmd_9_exact = bytes.fromhex("41540007e88c01000d0a")
    resp = send_and_get_response(ser, cmd_9_exact, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.3)
    
    # Motor 9 - Extended format with byte 0x8c
    print("Motor 9 - Extended format (0x20, 0x8c)...")
    cmd_9_ext = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0x8c, 0x08, 0x00,
                           0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_9_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Repeat a few times
    print("\nRepeating Motor 7 and 9 commands 2 more times...")
    for i in range(2):
        send_and_get_response(ser, cmd_7_exact, timeout=0.5)
        time.sleep(0.2)
        send_and_get_response(ser, cmd_9_exact, timeout=0.5)
        time.sleep(0.2)
    print("  [Done]")
    print()
    time.sleep(1.0)
    
    # STEP 2: Activate other motors
    print("="*70)
    print("STEP 2: Activate Other Motors")
    print("="*70)
    print()
    
    other_motors = [
        (0x0c, "Motor 1"),
        (0x1c, "Motor 3"),
        (0x58, "Motor 11"),
        (0x70, "Motor 14"),
    ]
    
    for byte_val, name in other_motors:
        cmd_act = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        send_and_get_response(ser, cmd_act, timeout=0.3)
        time.sleep(0.2)
        
        cmd_params = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                                0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        send_and_get_response(ser, cmd_params, timeout=0.3)
        time.sleep(0.2)
    
    print("  [Done]")
    print()
    
    ser.close()
    
    print("="*70)
    print("ACTIVATION COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio now:")
    print("  - Are Motors 7 and 9 visible?")
    print("  - Using correct bytes (0xbc, 0x8c) and sending FIRST")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

