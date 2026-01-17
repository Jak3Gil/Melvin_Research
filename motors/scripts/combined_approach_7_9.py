#!/usr/bin/env python3
"""
Combined approach for Motors 7 and 9:
1. Extended format query (0x3c for Motor 7, 0x4c for Motor 9) - we know this works
2. Motor Studio exact activation (0xbc for Motor 7, 0x8c for Motor 9)
3. Send FIRST before other motors
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
print("Combined Approach for Motors 7 and 9")
print("="*70)
print()
print("Strategy:")
print("  1. Extended format query (0x3c, 0x4c) - we know this works")
print("  2. Motor Studio exact activation (0xbc, 0x8c)")
print("  3. Send FIRST before other motors")
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
    
    # STEP 1: Motors 7 and 9 - Combined approach
    print("="*70)
    print("STEP 1: Motors 7 and 9 - Combined Approach")
    print("="*70)
    print()
    
    # Motor 7 - Extended format query (we know this works)
    print("Motor 7 - Extended format query (0x3c)...")
    cmd_7_query = bytes.fromhex("41542007e83c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_7_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.3)
    
    # Motor 7 - Motor Studio exact activation
    print("Motor 7 - Motor Studio activation (0xbc)...")
    cmd_7_act = bytes.fromhex("41540007ebc401000d0a")
    resp = send_and_get_response(ser, cmd_7_act, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.3)
    
    # Motor 9 - Extended format query (we know this works)
    print("Motor 9 - Extended format query (0x4c)...")
    cmd_9_query = bytes.fromhex("41542007e84c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_9_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.3)
    
    # Motor 9 - Motor Studio exact activation
    print("Motor 9 - Motor Studio activation (0x8c)...")
    cmd_9_act = bytes.fromhex("41540007e88c01000d0a")
    resp = send_and_get_response(ser, cmd_9_act, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Repeat the sequence
    print("\nRepeating sequence 2 more times...")
    for i in range(2):
        send_and_get_response(ser, cmd_7_query, timeout=0.5)
        time.sleep(0.2)
        send_and_get_response(ser, cmd_7_act, timeout=0.5)
        time.sleep(0.2)
        send_and_get_response(ser, cmd_9_query, timeout=0.5)
        time.sleep(0.2)
        send_and_get_response(ser, cmd_9_act, timeout=0.5)
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
    print()
    print("Sequence used:")
    print("  1. Extended query (0x3c, 0x4c) - known to work")
    print("  2. Motor Studio activation (0xbc, 0x8c) - exact format")
    print("  3. Other motors activated after")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

