#!/usr/bin/env python3
"""
Activate working motors first (1, 3, 11, 14), then try Motors 7 and 9
Maybe Motors 7 and 9 need other motors to be activated first
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

def activate_motor(ser, byte_val):
    """Activate motor using standard format"""
    cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
    return send_and_get_response(ser, cmd)

def load_params(ser, byte_val):
    """Load params using extended format"""
    cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    return send_and_get_response(ser, cmd)

port = 'COM6'
print("="*70)
print("Activate Working Motors First, Then Motors 7 and 9")
print("="*70)
print()
print("Strategy: Activate Motors 1, 3, 11, 14 first,")
print("then try to activate Motors 7 and 9")
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
    
    # Activate working motors first
    working_motors = [
        (0x0c, "Motor 1"),
        (0x1c, "Motor 3"),
        (0x58, "Motor 11"),
        (0x70, "Motor 14"),
    ]
    
    print("="*70)
    print("STEP 1: Activate Working Motors")
    print("="*70)
    print()
    
    for byte_val, name in working_motors:
        print(f"Activating {name} (byte 0x{byte_val:02x})...")
        resp1 = activate_motor(ser, byte_val)
        if resp1:
            print(f"  [RESPONSE] {resp1[:60]}...")
        else:
            print(f"  [NO RESPONSE]")
        
        time.sleep(0.3)
        
        resp2 = load_params(ser, byte_val)
        if resp2:
            print(f"  Load Params: [RESPONSE] {resp2[:60]}...")
        
        time.sleep(0.3)
        print()
    
    print("All working motors activated.")
    print()
    time.sleep(1.0)
    
    # Now try Motors 7 and 9 with different methods
    print("="*70)
    print("STEP 2: Try Motors 7 and 9 (After Working Motors Activated)")
    print("="*70)
    print()
    
    # Motor 7 - Try all formats
    print("Motor 7 - Testing different formats...")
    print()
    
    motor_7_formats = [
        (bytes.fromhex("41542007e83c0800c40000000000000d0a"), "Extended format (0x20, 0x3c)"),
        (bytes.fromhex("41540007e87c01000d0a"), "Standard format (0x00, 0x7c)"),
        (bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x3c, 0x01, 0x00, 0x0d, 0x0a]), "Activate (0x00, 0x3c)"),
        (bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x7c, 0x01, 0x00, 0x0d, 0x0a]), "Activate (0x00, 0x7c)"),
    ]
    
    for cmd, desc in motor_7_formats:
        print(f"  {desc}...")
        resp = send_and_get_response(ser, cmd, timeout=1.0)
        if resp:
            print(f"    [RESPONSE] {resp[:60]}...")
        else:
            print(f"    [NO RESPONSE]")
        time.sleep(0.3)
    
    print()
    
    # Motor 9 - Try all formats
    print("Motor 9 - Testing different formats...")
    print()
    
    motor_9_formats = [
        (bytes.fromhex("41542007e84c0800c40000000000000d0a"), "Extended format (0x20, 0x4c)"),
        (bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x4c, 0x01, 0x00, 0x0d, 0x0a]), "Activate (0x00, 0x4c)"),
    ]
    
    for cmd, desc in motor_9_formats:
        print(f"  {desc}...")
        resp = send_and_get_response(ser, cmd, timeout=1.0)
        if resp:
            print(f"    [RESPONSE] {resp[:60]}...")
        else:
            print(f"    [NO RESPONSE]")
        time.sleep(0.3)
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio now:")
    print("  - Are Motors 7 and 9 now visible?")
    print("  - Did activating working motors first help?")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

