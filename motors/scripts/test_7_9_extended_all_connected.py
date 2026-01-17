#!/usr/bin/env python3
"""
Test Motors 7 and 9 with extended format when all motors are connected
Maybe they only respond to extended format (0x20) when all motors are active
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
print("Test Motors 7 and 9 - Extended Format (All Motors Connected)")
print("="*70)
print()
print("Testing extended format (0x20) for Motors 7 and 9")
print("Maybe they only respond to extended format when all motors are active")
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
    
    # Test Motor 7 - Extended format with various bytes
    print("="*70)
    print("MOTOR 7 - Extended Format Tests")
    print("="*70)
    print()
    
    motor7_bytes = [0x3c, 0x38, 0x40, 0x34, 0x30, 0x2c]  # Various potential bytes
    
    for byte_val in motor7_bytes:
        print(f"Motor 7 - Extended format (0x20, byte 0x{byte_val:02x}):")
        cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                         0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=1.0)
        if resp:
            print(f"  [RESPONSE] {resp[:60]}...")
            print(f"  -> Motor 7 responds to extended format with byte 0x{byte_val:02x}!")
        else:
            print(f"  [NO RESPONSE]")
        time.sleep(0.5)
        print()
    
    # Test Motor 9 - Extended format with various bytes
    print("="*70)
    print("MOTOR 9 - Extended Format Tests")
    print("="*70)
    print()
    
    motor9_bytes = [0x4c, 0xdc, 0x48, 0x44, 0x40, 0xcc, 0xd0]  # Various potential bytes
    
    for byte_val in motor9_bytes:
        print(f"Motor 9 - Extended format (0x20, byte 0x{byte_val:02x}):")
        cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                         0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=1.0)
        if resp:
            print(f"  [RESPONSE] {resp[:60]}...")
            print(f"  -> Motor 9 responds to extended format with byte 0x{byte_val:02x}!")
        else:
            print(f"  [NO RESPONSE]")
        time.sleep(0.5)
        print()
    
    ser.close()
    
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("If Motors 7 and 9 responded, they need extended format (0x20)")
    print("when all motors are connected!")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

