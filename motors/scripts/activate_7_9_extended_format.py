#!/usr/bin/env python3
"""
Activate Motors 7 and 9 using extended format (0x20 command type)
Motors 7 and 9 use extended format for queries, so they might need it for activation too
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
print("Activate Motors 7 and 9 - Using Extended Format (0x20)")
print("="*70)
print()
print("Motor Studio commands:")
print("  Motor 7 extended: 41542007e83c0800c40000000000000d0a")
print("  Motor 7 standard: 41540007e87c01000d0a")
print("  Motor 9 extended: 41542007e84c0800c40000000000000d0a")
print()
print("Testing these exact formats as activation commands...")
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
    
    # Motor 7 - Extended format (0x20 command type, byte 0x3c)
    print("="*70)
    print("MOTOR 7 - Extended Format (0x20, byte 0x3c)")
    print("="*70)
    print()
    
    cmd_7_extended = bytes.fromhex("41542007e83c0800c40000000000000d0a")
    print("Sending Motor Studio extended command for Motor 7...")
    resp1 = send_and_get_response(ser, cmd_7_extended, timeout=1.0)
    if resp1:
        print(f"  [RESPONSE] {resp1[:80]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Also try standard 0x00 activation with byte 0x3c
    print("\nTrying standard activation (0x00) with byte 0x3c...")
    cmd_7_activate = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x3c, 0x01, 0x00, 0x0d, 0x0a])
    resp2 = send_and_get_response(ser, cmd_7_activate, timeout=1.0)
    if resp2:
        print(f"  [RESPONSE] {resp2[:80]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Motor 7 - Standard format (0x00 command type, byte 0x7c)
    print()
    print("="*70)
    print("MOTOR 7 - Standard Format (0x00, byte 0x7c)")
    print("="*70)
    print()
    
    cmd_7_standard = bytes.fromhex("41540007e87c01000d0a")
    print("Sending Motor Studio standard command for Motor 7...")
    resp3 = send_and_get_response(ser, cmd_7_standard, timeout=1.0)
    if resp3:
        print(f"  [RESPONSE] {resp3[:80]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Also try standard 0x00 activation with byte 0x7c
    print("\nTrying standard activation (0x00) with byte 0x7c...")
    cmd_7_activate2 = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x7c, 0x01, 0x00, 0x0d, 0x0a])
    resp4 = send_and_get_response(ser, cmd_7_activate2, timeout=1.0)
    if resp4:
        print(f"  [RESPONSE] {resp4[:80]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Motor 9 - Extended format (0x20 command type, byte 0x4c)
    print()
    print("="*70)
    print("MOTOR 9 - Extended Format (0x20, byte 0x4c)")
    print("="*70)
    print()
    
    cmd_9_extended = bytes.fromhex("41542007e84c0800c40000000000000d0a")
    print("Sending Motor Studio extended command for Motor 9...")
    resp5 = send_and_get_response(ser, cmd_9_extended, timeout=1.0)
    if resp5:
        print(f"  [RESPONSE] {resp5[:80]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Also try standard 0x00 activation with byte 0x4c
    print("\nTrying standard activation (0x00) with byte 0x4c...")
    cmd_9_activate = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x4c, 0x01, 0x00, 0x0d, 0x0a])
    resp6 = send_and_get_response(ser, cmd_9_activate, timeout=1.0)
    if resp6:
        print(f"  [RESPONSE] {resp6[:80]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(0.5)
    
    # Try sending extended format multiple times (like Motor Studio might)
    print()
    print("="*70)
    print("Repeating Extended Format Commands (Multiple Times)")
    print("="*70)
    print()
    
    print("Sending Motor 7 extended command 3 times...")
    for i in range(3):
        resp = send_and_get_response(ser, cmd_7_extended, timeout=1.0)
        if resp:
            print(f"  Attempt {i+1}: [RESPONSE] {resp[:60]}...")
        else:
            print(f"  Attempt {i+1}: [NO RESPONSE]")
        time.sleep(0.3)
    
    print("\nSending Motor 9 extended command 3 times...")
    for i in range(3):
        resp = send_and_get_response(ser, cmd_9_extended, timeout=1.0)
        if resp:
            print(f"  Attempt {i+1}: [RESPONSE] {resp[:60]}...")
        else:
            print(f"  Attempt {i+1}: [NO RESPONSE]")
        time.sleep(0.3)
    
    ser.close()
    
    print()
    print("="*70)
    print("ACTIVATION ATTEMPTS COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio now:")
    print("  - Are Motors 7 and 9 now visible?")
    print("  - Did any of the commands get responses?")
    print()
    print("If motors became visible, the extended format worked!")
    print("If not, we may need to try other command sequences.")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

