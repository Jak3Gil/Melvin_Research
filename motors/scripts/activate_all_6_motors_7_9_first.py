#!/usr/bin/env python3
"""
Activate all 6 motors - Motors 7 and 9 FIRST with extended format
Then activate other motors
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

def load_params(ser, byte_val):
    """Load motor parameters"""
    cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    return send_and_get_response(ser, cmd)

port = 'COM6'
print("="*70)
print("Activate All 6 Motors - Motors 7 and 9 FIRST")
print("="*70)
print()
print("Strategy: Query Motors 7 and 9 FIRST with extended format")
print("         Then activate all motors")
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
    
    # STEP 1: Motors 7 and 9 FIRST with extended format
    print("="*70)
    print("STEP 1: Motors 7 and 9 FIRST (Extended Format)")
    print("="*70)
    print()
    
    # Motor 7 - Extended format (we know this works)
    print("Motor 7 - Extended format query (0x3c)...")
    cmd_7_ext = bytes.fromhex("41542007e83c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_7_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Motor 7 - Standard format activation
    print("Motor 7 - Standard format activation (0x3c)...")
    cmd_7_std = bytes.fromhex("41540007e83c01000d0a")
    resp = send_and_get_response(ser, cmd_7_std, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Motor 9 - Extended format query (0x4c)
    print("Motor 9 - Extended format query (0x4c)...")
    cmd_9_ext = bytes.fromhex("41542007e84c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_9_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Motor 9 - Standard format activation (0xdc)
    print("Motor 9 - Standard format activation (0xdc)...")
    cmd_9_std = bytes.fromhex("41540007e8dc01000d0a")
    resp = send_and_get_response(ser, cmd_9_std, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    print("\nWaiting 1 second for Motors 7 and 9 to stabilize...")
    time.sleep(1.0)
    print()
    
    # STEP 2: Activate other motors
    print("="*70)
    print("STEP 2: Activate Other Motors (1, 3, 11, 14)")
    print("="*70)
    print()
    
    other_motors = [
        (1, 0x0c, "Motor 1"),
        (3, 0x1c, "Motor 3"),
        (11, 0x58, "Motor 11"),
        (14, 0x70, "Motor 14"),
    ]
    
    for motor_num, byte_val, name in other_motors:
        print(f"{name} (byte 0x{byte_val:02x}):")
        
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        if resp:
            print(f"  Activation: [RESPONSE] {resp[:60]}...")
        else:
            print(f"  Activation: [NO RESPONSE]")
        
        resp2 = load_params(ser, byte_val)
        if resp2:
            print(f"  Load Params: [RESPONSE] {resp2[:60]}...")
        
        time.sleep(0.3)
        print()
    
    # STEP 3: Verify Motors 7 and 9 again
    print("="*70)
    print("STEP 3: Verify Motors 7 and 9 Again")
    print("="*70)
    print()
    
    print("Motor 7 - Query again...")
    resp = send_and_get_response(ser, cmd_7_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
        print("  Motor 7 is responding!")
    else:
        print("  [NO RESPONSE]")
    
    print("Motor 9 - Query again...")
    resp = send_and_get_response(ser, cmd_9_ext, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
        print("  Motor 9 is responding!")
    else:
        print("  [NO RESPONSE]")
    
    ser.close()
    
    print()
    print("="*70)
    print("ACTIVATION COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio:")
    print("  - Are all 6 motors visible?")
    print("  - Motors 1, 3, 7, 9/19, 11, 14")
    print()
    print("Sequence used:")
    print("  1. Motors 7 and 9: Extended format query FIRST")
    print("  2. Motors 7 and 9: Standard format activation")
    print("  3. Other motors: Standard format activation")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

