#!/usr/bin/env python3
"""
Test Motor Studio's EXACT command formats for Motors 7 and 9
Motor 7: 41540007ebc401000d0a (byte 0xbc)
Motor 9: 41540007e88c01000d0a (byte 0x8c)
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
print("Test Motor Studio EXACT Commands for Motors 7 and 9")
print("="*70)
print()
print("Motor 7: 41540007ebc401000d0a (byte 0xbc)")
print("Motor 9: 41540007e88c01000d0a (byte 0x8c)")
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
    
    # Motor 7 - Exact Motor Studio command
    print("="*70)
    print("MOTOR 7 - Motor Studio Exact Command")
    print("="*70)
    print()
    
    cmd_7 = bytes.fromhex("41540007ebc401000d0a")
    print(f"Sending: {cmd_7.hex()}")
    print("  (AT 00 07 e8 bc 01 00 0d 0a)")
    resp = send_and_get_response(ser, cmd_7, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp}")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Also try activation and load params with byte 0xbc
    print("\nTrying activation with byte 0xbc...")
    cmd_7_act = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0xbc, 0x01, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_7_act, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    
    print("\nTrying load params with byte 0xbc...")
    cmd_7_params = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0xbc, 0x08, 0x00,
                               0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_7_params, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    
    time.sleep(0.5)
    
    # Motor 9 - Exact Motor Studio command
    print()
    print("="*70)
    print("MOTOR 9 - Motor Studio Exact Command")
    print("="*70)
    print()
    
    cmd_9 = bytes.fromhex("41540007e88c01000d0a")
    print(f"Sending: {cmd_9.hex()}")
    print("  (AT 00 07 e8 8c 01 00 0d 0a)")
    resp = send_and_get_response(ser, cmd_9, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp}")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Also try activation and load params with byte 0x8c
    print("\nTrying activation with byte 0x8c...")
    cmd_9_act = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x8c, 0x01, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_9_act, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    
    print("\nTrying load params with byte 0x8c...")
    cmd_9_params = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0x8c, 0x08, 0x00,
                               0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_9_params, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Key Discovery:")
    print("  Motor 7 uses byte 0xbc (NOT 0x3c or 0x7c)")
    print("  Motor 9 uses byte 0x8c (NOT 0x4c)")
    print()
    print("Check Motor Studio - Are Motors 7 and 9 now visible?")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

