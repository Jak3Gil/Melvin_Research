#!/usr/bin/env python3
"""
Test various byte encodings for Motor 7 to find one that responds
Motor 9 responds to CAN ID 9, but Motor 7 doesn't respond to CAN ID 7 or 0x3c
"""
import serial
import time

def send_and_check_response(ser, cmd, timeout=0.5):
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
    
    return response.hex() if len(response) > 0 else None

def activate_motor(ser, byte_val):
    """Activate motor"""
    cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
    return send_and_check_response(ser, cmd)

def load_params(ser, byte_val):
    """Load motor parameters"""
    cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    return send_and_check_response(ser, cmd)

port = 'COM6'
print("="*70)
print("Testing Motor 7 - Various Byte Encodings")
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
    
    # Test various bytes around Motor 7 patterns
    # Motor 7 query uses 0x3c, try variations
    test_bytes = [
        0x07,  # Actual CAN ID 7
        0x3c,  # Motor 7 query byte
        0x7c,  # Related pattern
        0xbc,  # Related pattern
        0xfc,  # Related pattern
        0x2c,  # Related pattern
        0x6c,  # Related pattern
    ]
    
    print("Testing Motor 7 byte encodings:")
    print("-" * 70)
    
    found_responses = []
    
    for byte_val in test_bytes:
        print(f"\nByte 0x{byte_val:02x}:")
        
        # Try activation
        resp1 = activate_motor(ser, byte_val)
        time.sleep(0.3)
        
        if resp1:
            print(f"  Activation: [RESPONSE] {resp1[:60]}...")
            found_responses.append((byte_val, 'activate', resp1))
        else:
            print(f"  Activation: No response")
        
        # Try load params
        resp2 = load_params(ser, byte_val)
        time.sleep(0.3)
        
        if resp2:
            print(f"  Load params: [RESPONSE] {resp2[:60]}...")
            found_responses.append((byte_val, 'load_params', resp2))
        else:
            print(f"  Load params: No response")
    
    ser.close()
    
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    
    if found_responses:
        print("\nBytes that got responses:")
        for byte_val, cmd_type, resp in found_responses:
            print(f"  Byte 0x{byte_val:02x} ({cmd_type}): {resp[:60]}...")
    else:
        print("\nNo responses found for Motor 7 with any byte encoding.")
        print("Motor 7 may need a different activation method.")
    
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

