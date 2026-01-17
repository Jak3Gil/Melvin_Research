#!/usr/bin/env python3
"""
Final comprehensive test - Try COMBINATIONS of approaches
- Initialize in different orders
- Try activation after other motors stabilize
- Try broadcast + individual
- Try different byte variations after working motors active
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
print("Final Comprehensive Combination Test")
print("="*70)
print()
print("Trying COMBINATIONS of approaches:")
print("  1. Different initialization sequences")
print("  2. Broadcast + individual queries")
print("  3. Activate working motors, then try 7/9")
print("  4. Try byte variations after bus stabilizes")
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    # Initialize
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    
    print("="*70)
    print("APPROACH 1: Activate Working Motors, Then Try All Byte Variations")
    print("="*70)
    print()
    
    # Activate working motors first
    working_bytes = [0x0c, 0x1c, 0x58, 0x70]
    for byte_val in working_bytes:
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        send_and_get_response(ser, cmd, timeout=0.5)
        time.sleep(0.2)
    
    print("Working motors activated. Waiting 2 seconds...")
    time.sleep(2.0)
    print()
    
    # Now try Motor 7/9 with ALL their known byte variations
    motor7_bytes = [0x3c, 0x7c, 0xbc, 0x38, 0x40, 0x34, 0x30, 0x2c]
    motor9_bytes = [0xdc, 0x4c, 0x8c, 0xcc, 0xd0, 0xd8, 0x48, 0x44]
    
    print("Testing Motor 7 byte variations (after working motors active):")
    found_7 = False
    for byte_val in motor7_bytes:
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=1.0)
        if resp:
            resp_lower = resp.lower()
            if '3fec' in resp_lower or '3ff4' in resp_lower:
                print(f"  Byte 0x{byte_val:02x}: [MOTOR 7 RESPONSE!] {resp[:60]}...")
                found_7 = True
            else:
                print(f"  Byte 0x{byte_val:02x}: [Response but wrong pattern] {resp[:60]}...")
        time.sleep(0.3)
    
    print()
    print("Testing Motor 9 byte variations (after working motors active):")
    found_9 = False
    for byte_val in motor9_bytes:
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=1.0)
        if resp:
            resp_lower = resp.lower()
            if '4fec' in resp_lower or '4ff4' in resp_lower or 'dc' in resp_lower[:40]:
                print(f"  Byte 0x{byte_val:02x}: [MOTOR 9 RESPONSE!] {resp[:60]}...")
                found_9 = True
            else:
                print(f"  Byte 0x{byte_val:02x}: [Response but wrong pattern] {resp[:60]}...")
        time.sleep(0.3)
    
    print()
    time.sleep(2.0)
    
    # APPROACH 2: Broadcast then individual
    print("="*70)
    print("APPROACH 2: Broadcast Enable, Then Individual Queries")
    print("="*70)
    print()
    
    # Broadcast enable
    broadcast = bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x01, 0x00, 0x0d, 0x0a])
    send_and_get_response(ser, broadcast, timeout=0.5)
    time.sleep(1.0)
    
    # Try Motors 7 and 9
    print("Trying Motor 7 (0x3c) after broadcast...")
    cmd_7 = bytes.fromhex("41540007e83c01000d0a")
    resp = send_and_get_response(ser, cmd_7, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    
    print("Trying Motor 9 (0xdc) after broadcast...")
    cmd_9 = bytes.fromhex("41540007e8dc01000d0a")
    resp = send_and_get_response(ser, cmd_9, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    
    ser.close()
    
    print()
    print("="*70)
    print("FINAL RESULTS")
    print("="*70)
    print()
    
    if found_7:
        print("SUCCESS: Motor 7 responds when working motors activated first!")
    else:
        print("Motor 7: Still no response")
    
    if found_9:
        print("SUCCESS: Motor 9 responds when working motors activated first!")
    else:
        print("Motor 9: Still no response")
    
    if not found_7 and not found_9:
        print()
        print("CONCLUSION:")
        print("Motors 7 and 9 do NOT respond when all motors connected,")
        print("even with all tested combinations.")
        print()
        print("This is consistent with:")
        print("  - 'Bus voltage too low' fault")
        print("  - Hardware/power issue")
        print("  - Motor Studio also can't detect them (confirms it's not software)")
        print()
        print("Potential solutions:")
        print("  1. Improve power supply/distribution")
        print("  2. Add power sequencing (power on motors gradually)")
        print("  3. Check CAN bus termination/voltage")
        print("  4. May need hardware fix for Motors 7 and 9")
    
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

