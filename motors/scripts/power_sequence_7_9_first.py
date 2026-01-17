#!/usr/bin/env python3
"""
Power sequence: Initialize Motors 7 and 9 FIRST with delays
This might help with power distribution when all motors are connected
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
print("Power Sequence: Motors 7 and 9 FIRST with Delays")
print("="*70)
print()
print("Strategy:")
print("  1. Initialize Motors 7 and 9 FIRST")
print("  2. Wait longer between commands (reduce power surge)")
print("  3. Let them stabilize before activating other motors")
print("  4. This might prevent 'Bus voltage too low' fault")
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(1.0)  # Longer delay
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(1.0)  # Longer delay
    ser.read(500)
    print("  [OK]")
    print()
    
    # STEP 1: Motors 7 and 9 FIRST with extended delays
    print("="*70)
    print("STEP 1: Initialize Motors 7 and 9 FIRST (Extended Delays)")
    print("="*70)
    print()
    
    # Motor 7 - Extended format query
    print("Motor 7 - Extended format query (0x3c)...")
    cmd_7_query = bytes.fromhex("41542007e83c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_7_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(2.0)  # Long delay - let motor stabilize
    
    # Motor 9 - Extended format query
    print("Motor 9 - Extended format query (0x4c)...")
    cmd_9_query = bytes.fromhex("41542007e84c0800c40000000000000d0a")
    resp = send_and_get_response(ser, cmd_9_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
    else:
        print("  [NO RESPONSE]")
    time.sleep(2.0)  # Long delay - let motor stabilize
    
    print("\nWaiting 3 seconds for Motors 7 and 9 to stabilize...")
    time.sleep(3.0)
    print("  [Done]")
    print()
    
    # STEP 2: Activate other motors slowly
    print("="*70)
    print("STEP 2: Activate Other Motors Slowly (One at a time)")
    print("="*70)
    print()
    
    other_motors = [
        (0x0c, "Motor 1"),
        (0x1c, "Motor 3"),
        (0x58, "Motor 11"),
        (0x70, "Motor 14"),
    ]
    
    for byte_val, name in other_motors:
        print(f"Activating {name} (byte 0x{byte_val:02x})...")
        
        cmd_act = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd_act, timeout=0.5)
        time.sleep(1.0)  # Delay between activations
        
        cmd_params = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                                0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd_params, timeout=0.5)
        time.sleep(1.0)  # Delay between commands
        
        print(f"  [Done]")
    
    print()
    time.sleep(2.0)
    
    # STEP 3: Verify Motors 7 and 9 still responding
    print("="*70)
    print("STEP 3: Verify Motors 7 and 9 Still Responding")
    print("="*70)
    print()
    
    print("Querying Motor 7 again...")
    resp = send_and_get_response(ser, cmd_7_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
        print("  Motor 7 is still responding!")
    else:
        print("  [NO RESPONSE] - Motor 7 may have faulted")
    
    print("\nQuerying Motor 9 again...")
    resp = send_and_get_response(ser, cmd_9_query, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp[:60]}...")
        print("  Motor 9 is still responding!")
    else:
        print("  [NO RESPONSE] - Motor 9 may have faulted")
    
    ser.close()
    
    print()
    print("="*70)
    print("POWER SEQUENCING COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio:")
    print("  - Do Motors 7 and 9 show 'Bus voltage too low' fault?")
    print("  - Are they still in RESET mode?")
    print()
    print("If fault persists, possible solutions:")
    print("  1. Increase power supply capacity")
    print("  2. Check power connections for Motors 7 and 9")
    print("  3. Add CAN bus termination resistors")
    print("  4. Power Motors 7 and 9 from separate power rail")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

