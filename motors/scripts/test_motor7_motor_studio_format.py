#!/usr/bin/env python3
"""
Test Motor 7 using Motor Studio format (similar to Motor 9)
Motor 9: 41540007e8dc01000d0a (byte 0xdc, CAN ID 19)
Motor 7: Try 41540007e83c01000d0a (byte 0x3c, might be a different CAN ID)
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
print("Test Motor 7 - Motor Studio Format (Similar to Motor 9)")
print("="*70)
print()
print("Motor 9: 41540007e8dc01000d0a (byte 0xdc, CAN ID 19)")
print("Motor 7: Try bytes 0x3c (extended query), 0xbc (activation), and variations")
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
    
    # Test Motor 7 candidates in Motor Studio format
    motor_7_candidates = [
        0x3c,  # Extended query byte (we know this works for query)
        0xbc,  # Motor Studio activation byte
        0x38,  # Lower range (got responses in 0x38-0x3f)
        0x3f,  # Upper range
    ]
    
    print("Testing Motor 7 candidates in Motor Studio format:")
    print("-" * 70)
    print()
    
    for byte_val in motor_7_candidates:
        # Motor Studio format: 41540007e8[BYTE]01000d0a
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        cmd_hex = cmd.hex()
        print(f"Byte 0x{byte_val:02x}: {cmd_hex}")
        print(f"  Sending: ", end='', flush=True)
        
        resp = send_and_get_response(ser, cmd, timeout=1.0)
        
        if resp:
            print(f"[RESPONSE] {resp}")
            
            # Check for Motor 7 patterns
            resp_clean = resp.replace('0d0a', '').replace('0d', '').lower()
            if '3fec' in resp_clean or '3ff4' in resp_clean:
                print(f"    -> Motor 7 pattern detected!")
        else:
            print("[NO RESPONSE]")
        
        print()
        time.sleep(0.3)
    
    ser.close()
    
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio:")
    print("  - Does Motor 7 appear with any of these bytes?")
    print("  - What CAN ID is Motor 7 showing as?")
    print()
    print("If found, Motor 7's CAN ID might have been changed similar to Motor 9")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

