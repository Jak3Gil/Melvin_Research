#!/usr/bin/env python3
"""
Clear fault and properly initialize Motors 7 and 9
Motor 7 is showing "Bus voltage too low" fault and stuck in RESET mode
Try different initialization sequences to clear the fault
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
print("Clear Fault and Initialize Motors 7 and 9")
print("="*70)
print()
print("Motor 7 is in RESET mode with 'Bus voltage too low' fault")
print("Try different initialization sequences to clear the fault")
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
    
    # Try multiple sequences for Motor 7
    print("="*70)
    print("MOTOR 7 - Multiple Initialization Attempts")
    print("="*70)
    print()
    
    # Sequence 1: Extended format query (we know this works)
    print("Attempt 1: Extended format query (0x3c)...")
    cmd_7_query = bytes.fromhex("41542007e83c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_7_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    time.sleep(0.5)
    
    # Sequence 2: Motor Studio exact activation
    print("Attempt 2: Motor Studio activation (0xbc)...")
    cmd_7_act = bytes.fromhex("41540007ebc401000d0a")
    resp = send_and_get_response(ser, cmd_7_act, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    time.sleep(0.5)
    
    # Sequence 3: Standard activation
    print("Attempt 3: Standard activation (0xbc)...")
    cmd_7_std = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0xbc, 0x01, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_7_std, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    time.sleep(0.5)
    
    # Sequence 4: Load params
    print("Attempt 4: Load params (0xbc)...")
    cmd_7_params = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0xbc, 0x08, 0x00,
                               0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_7_params, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    time.sleep(1.0)
    
    # Try Motor 9 similarly
    print()
    print("="*70)
    print("MOTOR 9 - Multiple Initialization Attempts")
    print("="*70)
    print()
    
    print("Attempt 1: Extended format query (0x4c)...")
    cmd_9_query = bytes.fromhex("41542007e84c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_9_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    time.sleep(0.5)
    
    print("Attempt 2: Motor Studio activation (0x8c)...")
    cmd_9_act = bytes.fromhex("41540007e88c01000d0a")
    resp = send_and_get_response(ser, cmd_9_act, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    time.sleep(0.5)
    
    print("Attempt 3: Load params (0x8c)...")
    cmd_9_params = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0x8c, 0x08, 0x00,
                               0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd_9_params, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    time.sleep(1.0)
    
    ser.close()
    
    print()
    print("="*70)
    print("INITIALIZATION COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio:")
    print("  - Is Motor 7 still showing 'Bus voltage too low' fault?")
    print("  - Is Motor 7 still in RESET mode?")
    print("  - Can you set Motor mode now?")
    print()
    print("If fault persists, it might be:")
    print("  1. Hardware issue specific to Motors 7 and 9")
    print("  2. CAN bus termination issue")
    print("  3. Motor configuration/calibration needed")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

