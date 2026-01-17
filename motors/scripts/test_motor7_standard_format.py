#!/usr/bin/env python3
"""
Test Motor 7 using standard format (like Motor 9)
Motor 7 when alone: Extended format 41542007e83c0800c40000000000000d0a (0x20, 0x3c)
Motor 9 when alone: Standard format 41540007e8dc01000d0a (0x00, 0xdc)

Try Motor 7 with standard format: 41540007e83c01000d0a (0x00, 0x3c)
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
print("Test Motor 7 - Standard Format (Like Motor 9)")
print("="*70)
print()
print("Motor 7 (alone): Extended format 41542007e83c0800c40000000000000d0a")
print("Motor 9 (alone): Standard format 41540007e8dc01000d0a")
print()
print("Trying Motor 7 with standard format: 41540007e83c01000d0a")
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
    
    # Motor 7 - Standard format (like Motor 9)
    print("Motor 7 - Standard format (0x00, 0x3c)...")
    cmd_7_std = bytes.fromhex("41540007e83c01000d0a")
    print(f"Command: {cmd_7_std.hex()}")
    print(f"  Format: AT 00 07 e8 3c 01 00 0d 0a")
    print()
    
    resp = send_and_get_response(ser, cmd_7_std, timeout=1.0)
    if resp:
        print(f"[RESPONSE] {resp}")
        resp_clean = resp.replace('0d0a', '').replace('0d', '').lower()
        if '3fec' in resp_clean or '3ff4' in resp_clean:
            print("  -> Motor 7 pattern detected!")
    else:
        print("[NO RESPONSE]")
    
    print()
    
    # Also try with byte variations around 0x3c
    print("Testing byte variations around 0x3c:")
    print("-" * 70)
    
    test_bytes = [0x3c, 0x38, 0x3f, 0xbc]  # Known candidates
    
    for byte_val in test_bytes:
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        print(f"Byte 0x{byte_val:02x}: ", end='', flush=True)
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        if resp:
            print(f"[RESPONSE] {resp[:60]}...")
        else:
            print("[NO RESPONSE]")
        time.sleep(0.2)
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Key Finding:")
    print("  Motor 7 (alone): Uses extended format (0x20)")
    print("  Motor 9 (alone): Uses standard format (0x00)")
    print()
    print("When all motors connected, they might need:")
    print("  Motor 7: Standard format (0x00, 0x3c) - like Motor 9")
    print("  Motor 9: Standard format (0x00, 0xdc)")
    print()
    print("Check Motor Studio - Does Motor 7 appear with standard format?")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

