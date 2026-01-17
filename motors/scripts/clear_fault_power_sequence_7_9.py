#!/usr/bin/env python3
"""
Clear fault and power sequence Motors 7 and 9
Theory: "Bus voltage is too low" fault prevents Motors 7/9 from responding
        when all motors connected. Need to clear fault first.
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
print("Clear Fault & Power Sequence Motors 7 and 9")
print("="*70)
print()
print("Theory: Motors 7/9 have 'Bus voltage is too low' fault")
print("        when all motors connected. Need to:")
print("  1. Clear the fault")
print("  2. Activate motors gradually (power sequencing)")
print("  3. Then query Motors 7 and 9")
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A (device read)
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Step 1: Try to clear fault (various methods)
    print("="*70)
    print("STEP 1: Clear Fault (Various Methods)")
    print("="*70)
    print()
    
    fault_clear_commands = [
        ("Reset command", bytes.fromhex("41540007e83c02000d0a")),  # Reset Motor 7
        ("Reset command", bytes.fromhex("41540007e8dc02000d0a")),  # Reset Motor 9
        ("Clear fault (0x03)", bytes.fromhex("41540007e83c03000d0a")),  # Clear fault Motor 7
        ("Clear fault (0x03)", bytes.fromhex("41540007e8dc03000d0a")),  # Clear fault Motor 9
        ("Disable then enable", bytes.fromhex("41540007e83c00000d0a")),  # Disable Motor 7
        ("Disable then enable", bytes.fromhex("41540007e8dc00000d0a")),  # Disable Motor 9
    ]
    
    for desc, cmd in fault_clear_commands:
        print(f"  {desc}...")
        resp = send_and_get_response(ser, cmd, timeout=0.5)
        if resp:
            print(f"    [RESPONSE] {resp[:60]}...")
        time.sleep(0.3)
    
    print()
    print("Waiting 1 second...")
    time.sleep(1.0)
    print()
    
    # Step 2: Power sequence - activate motors one at a time with delays
    print("="*70)
    print("STEP 2: Power Sequence (Activate Motors Gradually)")
    print("="*70)
    print()
    print("Activating motors one at a time to prevent voltage drop...")
    print()
    
    motors_sequence = [
        (0x0c, "Motor 1"),
        (0x1c, "Motor 3"),
    ]
    
    # Activate first 2 motors
    for byte_val, name in motors_sequence:
        print(f"Activating {name} (byte 0x{byte_val:02x})...")
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        if resp:
            print(f"  [RESPONSE]")
        time.sleep(0.5)  # Longer delay between activations
    
    print()
    print("Waiting 2 seconds for voltage to stabilize...")
    time.sleep(2.0)
    
    # Now try Motors 7 and 9 (with fewer motors active, voltage should be higher)
    print()
    print("Now trying Motors 7 and 9 (with only 2 motors active)...")
    print()
    
    print("Motor 7 (byte 0x3c)...")
    cmd_7 = bytes.fromhex("41540007e83c01000d0a")
    resp_7 = send_and_get_response(ser, cmd_7, timeout=1.0)
    if resp_7:
        print(f"  [RESPONSE] {resp_7[:60]}...")
        print("  -> Motor 7 responds with fewer motors active!")
    else:
        print("  [NO RESPONSE]")
    
    time.sleep(0.5)
    
    print("Motor 9 (byte 0xdc)...")
    cmd_9 = bytes.fromhex("41540007e8dc01000d0a")
    resp_9 = send_and_get_response(ser, cmd_9, timeout=1.0)
    if resp_9:
        print(f"  [RESPONSE] {resp_9[:60]}...")
        print("  -> Motor 9 responds with fewer motors active!")
    else:
        print("  [NO RESPONSE]")
    
    # Step 3: Continue power sequence
    print()
    print("Activating remaining motors...")
    print()
    
    remaining_motors = [
        (0x58, "Motor 11"),
        (0x70, "Motor 14"),
    ]
    
    for byte_val, name in remaining_motors:
        print(f"Activating {name} (byte 0x{byte_val:02x})...")
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        if resp:
            print(f"  [RESPONSE]")
        time.sleep(0.5)
    
    print()
    print("Waiting 2 seconds...")
    time.sleep(2.0)
    
    # Check Motors 7 and 9 again after all motors activated
    print()
    print("Checking Motors 7 and 9 again (all motors now active)...")
    print()
    
    resp_7_after = send_and_get_response(ser, cmd_7, timeout=1.0)
    if resp_7_after:
        print(f"  Motor 7: [RESPONSE] {resp_7_after[:60]}...")
        if not resp_7:
            print("  -> Motor 7 NOW responds after power sequence!")
    else:
        print("  Motor 7: [NO RESPONSE]")
        if resp_7:
            print("  -> Motor 7 STOPPED responding after all motors activated")
            print("     Confirms voltage/power issue!")
    
    time.sleep(0.5)
    
    resp_9_after = send_and_get_response(ser, cmd_9, timeout=1.0)
    if resp_9_after:
        print(f"  Motor 9: [RESPONSE] {resp_9_after[:60]}...")
        if not resp_9:
            print("  -> Motor 9 NOW responds after power sequence!")
    else:
        print("  Motor 9: [NO RESPONSE]")
        if resp_9:
            print("  -> Motor 9 STOPPED responding after all motors activated")
            print("     Confirms voltage/power issue!")
    
    ser.close()
    
    print()
    print("="*70)
    print("ANALYSIS")
    print("="*70)
    print()
    if resp_7 or resp_9:
        print("SUCCESS: Motors 7/9 responded during power sequence!")
        print("  - Solution: Use power sequencing (activate gradually)")
        print("  - Or: Clear fault before activation")
    elif resp_7 and not resp_7_after:
        print("CONFIRMED: Voltage drop issue!")
        print("  - Motors 7/9 respond with fewer motors")
        print("  - Stop responding when all motors active")
        print("  - Solution needed: Better power supply or distribution")
    else:
        print("Motors 7/9 still don't respond")
        print("  - May need Motor Studio's exact fault-clearing sequence")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

