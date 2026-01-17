#!/usr/bin/env python3
"""
Activate working motors first, then test Motors 7 and 9 with various bytes
Maybe Motors 7 and 9 use different bytes when all motors are connected
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
print("Activate Working Motors First, Then Test Motors 7 and 9")
print("="*70)
print()
print("Strategy:")
print("  1. Activate working motors (1, 3, 11, 14) first")
print("  2. Then try Motors 7 and 9 with various byte values")
print("  3. Maybe they use different bytes when all motors connected")
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
    
    # Step 1: Activate working motors
    print("="*70)
    print("STEP 1: Activate Working Motors")
    print("="*70)
    print()
    
    working_motors = [
        (0x0c, "Motor 1"),
        (0x1c, "Motor 3"),
        (0x58, "Motor 11"),
        (0x70, "Motor 14"),
    ]
    
    for byte_val, name in working_motors:
        print(f"Activating {name} (byte 0x{byte_val:02x})...")
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        if resp:
            print(f"  [RESPONSE] {resp[:60]}...")
        else:
            print(f"  [NO RESPONSE]")
        time.sleep(0.3)
    
    print()
    print("Waiting 1 second for bus to stabilize...")
    time.sleep(1.0)
    print()
    
    # Step 2: Test Motors 7 and 9 with various bytes
    print("="*70)
    print("STEP 2: Test Motors 7 and 9 - Various Bytes")
    print("="*70)
    print()
    
    # Motor 7 candidate bytes (from various tests)
    motor7_bytes = [
        (0x3c, "Motor 7 individual (standard)"),
        (0x7c, "Motor 7 individual (alternative)"),
        (0xbc, "Motor 7 Motor Studio"),
        (0x38, "Motor 7 variation"),
        (0x40, "Motor 7 variation"),
        (0x5c, "Motor 7 variation"),
    ]
    
    print("Motor 7 byte candidates:")
    print("-" * 70)
    for byte_val, desc in motor7_bytes:
        print(f"  Testing 0x{byte_val:02x} ({desc})...")
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        if resp:
            print(f"    [RESPONSE] {resp[:60]}...")
            if '3fec' in resp.lower() or '3ff4' in resp.lower():
                print(f"    -> Motor 7 PATTERN!")
        else:
            print(f"    [NO RESPONSE]")
        time.sleep(0.3)
    
    print()
    
    # Motor 9 candidate bytes
    motor9_bytes = [
        (0xdc, "Motor 9 individual (CAN ID 19)"),
        (0x4c, "Motor 9 extended format"),
        (0x8c, "Motor 9 Motor Studio"),
        (0x58, "Motor 9 variation (note: 0x58 is Motor 11)"),
        (0x48, "Motor 9 variation"),
        (0xcc, "Motor 9 variation"),
    ]
    
    print("Motor 9 byte candidates:")
    print("-" * 70)
    for byte_val, desc in motor9_bytes:
        print(f"  Testing 0x{byte_val:02x} ({desc})...")
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        if resp:
            print(f"    [RESPONSE] {resp[:60]}...")
            resp_lower = resp.lower()
            if '4fec' in resp_lower or '4ff4' in resp_lower or 'dc' in resp_lower[:40]:
                print(f"    -> Motor 9 PATTERN!")
            elif '5fec' in resp_lower or '5ff4' in resp_lower:
                print(f"    -> Motor 11 pattern (not Motor 9)")
        else:
            print(f"    [NO RESPONSE]")
        time.sleep(0.3)
    
    print()
    
    # Step 3: Try extended format after working motors activated
    print("="*70)
    print("STEP 3: Test Extended Format (After Working Motors)")
    print("="*70)
    print()
    
    print("Motor 7 - Extended format (0x20, 0x3c)...")
    cmd_ext_7 = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0x3c, 0x08, 0x00,
                          0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_ext_7, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print(f"  [NO RESPONSE]")
    time.sleep(0.5)
    
    print("Motor 9 - Extended format (0x20, 0x4c)...")
    cmd_ext_9 = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0x4c, 0x08, 0x00,
                          0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_ext_9, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print(f"  [NO RESPONSE]")
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("If any byte/format made Motors 7 or 9 respond, that's the answer!")
    print("Otherwise, Motors 7 and 9 may need Motor Studio's exact sequence")
    print("which we need to capture from serial traffic.")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

