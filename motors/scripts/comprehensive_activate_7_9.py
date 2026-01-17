#!/usr/bin/env python3
"""
Comprehensive activation test for Motors 7 and 9
- Checks for responses after each command
- Tries multiple activation methods
- Uses both encoded bytes and actual CAN IDs
- Includes load params command
"""
import serial
import time

def send_and_check_response(ser, cmd, description, timeout=0.5):
    """Send command and check for response"""
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
    if resp_hex:
        print(f"    Response: {resp_hex[:60]}...")
        return True, resp_hex
    else:
        print(f"    No response")
        return False, None

def activate_motor(ser, can_id):
    """Activate motor"""
    cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    return send_and_check_response(ser, cmd, f"Activate CAN ID {can_id}")

def load_params(ser, can_id):
    """Load motor parameters"""
    cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    return send_and_check_response(ser, cmd, f"Load params CAN ID {can_id}")

port = 'COM6'
print("="*70)
print("Comprehensive Activation Test for Motors 7 and 9")
print("="*70)
print()
print("Testing multiple methods and checking ALL responses...")
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    if not ser.is_open:
        print(f"[ERROR] Serial port {port} failed to open!")
        exit(1)
    
    print(f"[OK] Serial port {port} is OPEN")
    print()
    
    # Initialize
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Test different byte encodings for Motor 7
    test_cases_motor7 = [
        (7, "Actual CAN ID 7"),
        (0x3c, "Encoded byte 0x3c (Motor 7 query)"),
    ]
    
    # Test different byte encodings for Motor 9
    test_cases_motor9 = [
        (9, "Actual CAN ID 9"),
        (0x4c, "Encoded byte 0x4c (Motor 9 query)"),
    ]
    
    print("="*70)
    print("TESTING MOTOR 7")
    print("="*70)
    
    for byte_val, desc in test_cases_motor7:
        print(f"\n{desc} (byte: 0x{byte_val:02x}):")
        
        # Try activation
        print("  Activating...")
        got_response, resp = activate_motor(ser, byte_val)
        time.sleep(0.3)
        
        # Try load params
        print("  Loading params...")
        got_response2, resp2 = load_params(ser, byte_val)
        time.sleep(0.3)
        
        if got_response or got_response2:
            print(f"    [SUCCESS] Got response with {desc}!")
        else:
            print(f"    [NO RESPONSE] {desc} didn't respond")
    
    print()
    print("="*70)
    print("TESTING MOTOR 9")
    print("="*70)
    
    for byte_val, desc in test_cases_motor9:
        print(f"\n{desc} (byte: 0x{byte_val:02x}):")
        
        # Try activation
        print("  Activating...")
        got_response, resp = activate_motor(ser, byte_val)
        time.sleep(0.3)
        
        # Try load params
        print("  Loading params...")
        got_response2, resp2 = load_params(ser, byte_val)
        time.sleep(0.3)
        
        if got_response or got_response2:
            print(f"    [SUCCESS] Got response with {desc}!")
        else:
            print(f"    [NO RESPONSE] {desc} didn't respond")
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Check which byte encodings got responses!")
    print("Then we can use those for the activation sequence.")
    print()
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

