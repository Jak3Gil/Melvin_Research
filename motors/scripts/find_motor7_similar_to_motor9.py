#!/usr/bin/env python3
"""
Find Motor 7 using similar approach to Motor 9
Motor 9: CAN ID 19, found with byte 0xdc (41540007e8dc01000d0a)
Motor 7: Might have similar byte encoding pattern

Try byte variations around 0xdc and other patterns
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
print("Find Motor 7 - Similar to Motor 9 Pattern")
print("="*70)
print()
print("Motor 9: CAN ID 19, byte 0xdc (41540007e8dc01000d0a)")
print("Motor 7: Try similar byte patterns around 0xdc")
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
    
    # Motor 9 is 0xdc, Motor 7 might be related
    # Try variations: 0xdc - 0x20 = 0xbc, 0xdc - 0x30 = 0xac, etc.
    # Or try 0xdc - 0x40 = 0x9c, or patterns like 0xcc, 0xec, 0xfc
    
    test_bytes = [
        0xbc,  # 0xdc - 0x20 (Motor 7 was 0xbc in Motor Studio)
        0xac,  # 0xdc - 0x30
        0xcc,  # 0xdc - 0x10
        0xec,  # 0xdc + 0x10
        0xfc,  # 0xdc + 0x20
        0xdc,  # Same as Motor 9 (to verify)
        0x9c,  # Motor 11 query byte
        0x7c,  # Motor 7 standard format
    ]
    
    print("Testing byte encodings for Motor 7:")
    print("-" * 70)
    print()
    
    found_responses = []
    
    for byte_val in test_bytes:
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        print(f"Byte 0x{byte_val:02x}: ", end='', flush=True)
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        
        if resp:
            print(f"[RESPONSE] {resp[:60]}...")
            found_responses.append((byte_val, resp))
        else:
            print("[NO RESPONSE]")
        
        time.sleep(0.2)
    
    ser.close()
    
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    
    if found_responses:
        print("Bytes that got responses:")
        for byte_val, resp in found_responses:
            print(f"  Byte 0x{byte_val:02x}: {resp[:60]}...")
            
            # Check response pattern
            resp_clean = resp.replace('0d0a', '').replace('0d', '').lower()
            if '3fec' in resp_clean or '3c' in resp_clean[:20]:
                print(f"    -> Pattern suggests Motor 7!")
            elif '4fec' in resp_clean or '4c' in resp_clean[:20]:
                print(f"    -> Pattern suggests Motor 9!")
            elif '5fec' in resp_clean or '5c' in resp_clean[:20]:
                print(f"    -> Pattern suggests Motor 11!")
    else:
        print("No responses found. Motor 7 might need a different approach.")
    
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

