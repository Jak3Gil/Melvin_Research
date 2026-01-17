#!/usr/bin/env python3
"""
Analyze the difference between 2 motors vs 6 motors connected
Why do Motors 7 and 9 work individually but not when all motors connected?

Possible reasons:
1. CAN bus arbitration - Motors 7/9 lose when others are active
2. Power/bus voltage drop - "Bus voltage is too low" fault
3. CAN ID conflicts - Shared addresses when all motors present
4. Initialization order - Need to be first
5. Bus timing/contention - Too many simultaneous responses
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
print("Analyze 2 Motors vs 6 Motors - Why the Difference?")
print("="*70)
print()
print("Hypothesis: Motors 7 and 9 work individually because:")
print("  1. No CAN bus contention (only 2 motors)")
print("  2. No voltage drop (less power draw)")
print("  3. No address conflicts")
print("  4. Less bus traffic = no arbitration loss")
print()
print("When 6 motors connected:")
print("  - Motors 1, 3, 11, 14 respond (4 motors active)")
print("  - Motors 7, 9 don't respond (2 motors silent)")
print("  - This suggests CAN arbitration or power issue")
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
    
    # Test 1: Check if Motors 7 and 9 respond when queried FIRST (before others)
    print("="*70)
    print("TEST 1: Query Motors 7 and 9 FIRST (Before Others)")
    print("="*70)
    print()
    print("Theory: Maybe they need to be queried FIRST to avoid arbitration loss")
    print()
    
    print("Motor 7 (byte 0x3c) - Query FIRST...")
    cmd_7 = bytes.fromhex("41540007e83c01000d0a")
    resp_7 = send_and_get_response(ser, cmd_7, timeout=1.0)
    if resp_7:
        print(f"  [RESPONSE] {resp_7[:60]}...")
        print("  -> Motor 7 responds when queried FIRST!")
    else:
        print("  [NO RESPONSE]")
    
    time.sleep(0.3)
    
    print("Motor 9 (byte 0xdc) - Query FIRST...")
    cmd_9 = bytes.fromhex("41540007e8dc01000d0a")
    resp_9 = send_and_get_response(ser, cmd_9, timeout=1.0)
    if resp_9:
        print(f"  [RESPONSE] {resp_9[:60]}...")
        print("  -> Motor 9 responds when queried FIRST!")
    else:
        print("  [NO RESPONSE]")
    
    print()
    time.sleep(1.0)
    
    # Test 2: Now activate other motors and see if 7/9 still respond
    print("="*70)
    print("TEST 2: Activate Other Motors, Then Check 7 and 9 Again")
    print("="*70)
    print()
    print("If Motors 7 and 9 stop responding after others activated,")
    print("it confirms bus contention or arbitration issue")
    print()
    
    working_motors = [
        (0x0c, "Motor 1"),
        (0x1c, "Motor 3"),
        (0x58, "Motor 11"),
        (0x70, "Motor 14"),
    ]
    
    for byte_val, name in working_motors:
        print(f"Activating {name} (byte 0x{byte_val:02x})...")
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        if resp:
            print(f"  [RESPONSE]")
        time.sleep(0.2)
    
    print()
    print("Now checking Motors 7 and 9 again...")
    time.sleep(0.5)
    
    resp_7_after = send_and_get_response(ser, cmd_7, timeout=1.0)
    if resp_7_after:
        print(f"  Motor 7: [RESPONSE] {resp_7_after[:60]}...")
        print("  -> Motor 7 still responds after others activated!")
    else:
        print("  Motor 7: [NO RESPONSE]")
        if resp_7:
            print("  -> Motor 7 STOPPED responding after others activated!")
            print("     This confirms bus contention/arbitration issue!")
    
    time.sleep(0.3)
    
    resp_9_after = send_and_get_response(ser, cmd_9, timeout=1.0)
    if resp_9_after:
        print(f"  Motor 9: [RESPONSE] {resp_9_after[:60]}...")
        print("  -> Motor 9 still responds after others activated!")
    else:
        print("  Motor 9: [NO RESPONSE]")
        if resp_9:
            print("  -> Motor 9 STOPPED responding after others activated!")
            print("     This confirms bus contention/arbitration issue!")
    
    print()
    
    # Test 3: Query with longer delays (avoid bus contention)
    print("="*70)
    print("TEST 3: Query Motors 7 and 9 with Longer Delays")
    print("="*70)
    print()
    print("Theory: Maybe they need longer timeouts to respond")
    print("        (bus might be busy with other motors)")
    print()
    
    print("Waiting 2 seconds for bus to clear...")
    time.sleep(2.0)
    
    print("Motor 7 - Query with long timeout (2 seconds)...")
    resp_7_long = send_and_get_response(ser, cmd_7, timeout=2.0)
    if resp_7_long:
        print(f"  [RESPONSE] {resp_7_long[:60]}...")
        print("  -> Motor 7 responds with longer timeout!")
    else:
        print("  [NO RESPONSE]")
    
    time.sleep(2.0)  # Wait for bus to clear
    
    print("Motor 9 - Query with long timeout (2 seconds)...")
    resp_9_long = send_and_get_response(ser, cmd_9, timeout=2.0)
    if resp_9_long:
        print(f"  [RESPONSE] {resp_9_long[:60]}...")
        print("  -> Motor 9 responds with longer timeout!")
    else:
        print("  [NO RESPONSE]")
    
    ser.close()
    
    print()
    print("="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print()
    print("KEY FINDINGS:")
    print()
    if resp_7 and not resp_7_after:
        print("  ✓ Motor 7: Responds FIRST, stops after others activated")
        print("    -> CAN bus arbitration/contention issue")
    elif resp_7_long and not resp_7:
        print("  ✓ Motor 7: Needs longer timeout")
        print("    -> Bus timing/contention issue")
    else:
        print("  ✗ Motor 7: Never responds with all motors connected")
    
    if resp_9 and not resp_9_after:
        print("  ✓ Motor 9: Responds FIRST, stops after others activated")
        print("    -> CAN bus arbitration/contention issue")
    elif resp_9_long and not resp_9:
        print("  ✓ Motor 9: Needs longer timeout")
        print("    -> Bus timing/contention issue")
    else:
        print("  ✗ Motor 9: Never responds with all motors connected")
    
    print()
    print("If Motors 7/9 respond FIRST but stop after others:")
    print("  - Solution: Query them FIRST, keep them active before querying others")
    print()
    print("If they need longer timeouts:")
    print("  - Solution: Use longer delays/timeouts when querying Motors 7/9")
    print()
    print("If they never respond:")
    print("  - Possible: Power/voltage issue (Bus voltage too low fault)")
    print("  - Possible: Different CAN IDs when all motors connected")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

