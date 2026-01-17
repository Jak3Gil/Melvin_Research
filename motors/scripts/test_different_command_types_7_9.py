#!/usr/bin/env python3
"""
Test different COMMAND types for Motors 7 and 9
We've tested all address bytes - maybe they respond to different COMMAND bytes?
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
print("Test Different Command Types for Motors 7 and 9")
print("="*70)
print()
print("We've tested all address bytes (0x00-0xFF)")
print("Now testing different COMMAND types (bytes after AT)")
print()
print("Known command types:")
print("  0x00 = Standard activate")
print("  0x20 = Extended/Load params")
print("  0x90 = JOG/Move")
print("  etc.")
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Motor 7 and 9 individual bytes
    motor7_byte = 0x3c
    motor9_byte = 0xdc
    
    # Test different command types
    command_types = [
        (0x00, "Standard activate", [0x01, 0x00]),
        (0x10, "Command type 0x10", [0x01, 0x00]),
        (0x20, "Extended/Load params", [0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
        (0x30, "Command type 0x30", [0x01, 0x00]),
        (0x40, "Command type 0x40", [0x01, 0x00]),
        (0x50, "Command type 0x50", [0x01, 0x00]),
        (0x60, "Command type 0x60", [0x01, 0x00]),
        (0x70, "Command type 0x70", [0x01, 0x00]),
        (0x80, "Command type 0x80", [0x01, 0x00]),
        (0x90, "JOG/Move", [0x08, 0x05, 0x70, 0x00, 0x00, 0x07, 0x01, 0x80, 0x19]),  # Move command
        (0xa0, "Command type 0xa0", [0x01, 0x00]),
        (0xb0, "Command type 0xb0", [0x01, 0x00]),
        (0xc0, "Command type 0xc0", [0x01, 0x00]),
        (0xd0, "Command type 0xd0", [0x01, 0x00]),
        (0xe0, "Command type 0xe0", [0x01, 0x00]),
        (0xf0, "Command type 0xf0", [0x01, 0x00]),
    ]
    
    print("="*70)
    print("MOTOR 7 - Different Command Types (byte 0x3c)")
    print("="*70)
    print()
    
    motor7_responses = []
    
    for cmd_type, desc, data_bytes in command_types:
        cmd = bytearray([0x41, 0x54, cmd_type, 0x07, 0xe8, motor7_byte])
        cmd.extend(data_bytes)
        cmd.extend([0x0d, 0x0a])
        
        print(f"  Command 0x{cmd_type:02x} ({desc}): ", end='', flush=True)
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        
        if resp:
            print(f"[RESPONSE] {resp[:50]}...")
            motor7_responses.append({
                'cmd_type': cmd_type,
                'desc': desc,
                'response': resp
            })
        else:
            print("[NO RESPONSE]")
        
        time.sleep(0.2)
    
    print()
    
    print("="*70)
    print("MOTOR 9 - Different Command Types (byte 0xdc)")
    print("="*70)
    print()
    
    motor9_responses = []
    
    for cmd_type, desc, data_bytes in command_types:
        cmd = bytearray([0x41, 0x54, cmd_type, 0x07, 0xe8, motor9_byte])
        cmd.extend(data_bytes)
        cmd.extend([0x0d, 0x0a])
        
        print(f"  Command 0x{cmd_type:02x} ({desc}): ", end='', flush=True)
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        
        if resp:
            print(f"[RESPONSE] {resp[:50]}...")
            motor9_responses.append({
                'cmd_type': cmd_type,
                'desc': desc,
                'response': resp
            })
        else:
            print("[NO RESPONSE]")
        
        time.sleep(0.2)
    
    ser.close()
    
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    
    if motor7_responses:
        print(f"Motor 7: {len(motor7_responses)} command types got responses:")
        for item in motor7_responses:
            print(f"  - 0x{item['cmd_type']:02x} ({item['desc']})")
    else:
        print("Motor 7: No responses to any command type")
    
    if motor9_responses:
        print(f"Motor 9: {len(motor9_responses)} command types got responses:")
        for item in motor9_responses:
            print(f"  - 0x{item['cmd_type']:02x} ({item['desc']})")
    else:
        print("Motor 9: No responses to any command type")
    
    print()
    
    if motor7_responses or motor9_responses:
        print("SUCCESS! Found command types that work!")
        print("Use these command types instead of standard activate (0x00)")
    else:
        print("No command types worked.")
        print("Motors 7 and 9 truly don't respond when all motors connected.")
        print()
        print("This suggests:")
        print("  1. Hardware fault (Bus voltage too low)")
        print("  2. They're physically in a fault state")
        print("  3. Need to fix power/voltage issue first")
    
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

