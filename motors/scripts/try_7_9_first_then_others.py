#!/usr/bin/env python3
"""
Try querying/activating Motors 7 and 9 FIRST, before other motors
Maybe they need to be initialized before the other motors are activated
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
print("Try Motors 7 and 9 FIRST, Then Other Motors")
print("="*70)
print()
print("Strategy: Initialize Motors 7 and 9 BEFORE activating other motors")
print("Maybe the order matters when all motors are connected!")
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
    
    # STEP 1: Try Motors 7 and 9 FIRST with all their command formats
    print("="*70)
    print("STEP 1: Initialize Motors 7 and 9 FIRST")
    print("="*70)
    print()
    
    # Motor 7 - Extended format (Motor Studio's exact command)
    print("Motor 7 - Sending extended format command...")
    cmd_7_ext = bytes.fromhex("41542007e83c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_7_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Motor 7 - Standard format
    print("Motor 7 - Sending standard format command...")
    cmd_7_std = bytes.fromhex("41540007e87c01000d0a")
    resp = send_and_get_response(ser, cmd_7_std, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Motor 9 - Extended format (Motor Studio's exact command)
    print("Motor 9 - Sending extended format command...")
    cmd_9_ext = bytes.fromhex("41542007e84c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_9_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Repeat the commands multiple times (like Motor Studio might)
    print("\nRepeating Motor 7 and 9 commands 3 times each...")
    for i in range(3):
        send_and_get_response(ser, cmd_7_ext, timeout=0.5)
        time.sleep(0.2)
        send_and_get_response(ser, cmd_9_ext, timeout=0.5)
        time.sleep(0.2)
    
    print("  [Done]")
    print()
    time.sleep(1.0)
    
    # STEP 2: Now activate other motors
    print("="*70)
    print("STEP 2: Activate Other Motors (1, 3, 11, 14)")
    print("="*70)
    print()
    
    other_motors = [
        (0x0c, "Motor 1"),
        (0x1c, "Motor 3"),
        (0x58, "Motor 11"),
        (0x70, "Motor 14"),
    ]
    
    for byte_val, name in other_motors:
        # Activate
        cmd_act = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd_act, timeout=0.5)
        time.sleep(0.2)
        
        # Load params
        cmd_params = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                                0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd_params, timeout=0.5)
        time.sleep(0.2)
    
    print("  [Done]")
    print()
    
    # STEP 3: Try Motors 7 and 9 again
    print("="*70)
    print("STEP 3: Query Motors 7 and 9 Again (After Other Motors)")
    print("="*70)
    print()
    
    print("Motor 7 - Extended format again...")
    resp = send_and_get_response(ser, cmd_7_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    
    print("Motor 9 - Extended format again...")
    resp = send_and_get_response(ser, cmd_9_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio now:")
    print("  - Are Motors 7 and 9 visible?")
    print("  - Did querying them FIRST make a difference?")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

