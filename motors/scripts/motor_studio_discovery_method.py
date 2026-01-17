#!/usr/bin/env python3
"""
Motor Studio Discovery Method - Replicate how Motor Studio finds all motors
Based on Motor Studio behavior and CanOPEN discovery protocols
"""
import serial
import time
import sys
from collections import defaultdict

KNOWN_MOTORS = [1, 3, 7, 9, 11, 14]

def extract_motor_id(msg_hex):
    """Extract motor ID from response"""
    msg_clean = msg_hex.replace('0d0a', '').lower()
    
    if not msg_clean.startswith('4154'):
        return None
    
    # Response format: 41541000XXec...
    if msg_clean.startswith('41541000'):
        if len(msg_clean) >= 12:
            id_bytes = msg_clean[8:12]
            known_responses = {
                '0fec': 1,
                '1fec': 3,
                '77ec': 14,
                # Try to find patterns for 7, 9, 11
                '3fec': 7,
                '4fec': 9,
                '9fec': 11,
            }
            if id_bytes in known_responses:
                return known_responses[id_bytes]
    
    return None

def motor_studio_discovery(port='COM6', baudrate=921600):
    """
    Replicate Motor Studio's discovery process
    Motor Studio likely:
    1. Initializes adapter
    2. Sends device read
    3. Sends CanOPEN NMT commands to put all nodes in operational state
    4. Queries each motor individually with delays
    5. May use broadcast queries first
    """
    
    motors_found = defaultdict(list)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Motor Studio Discovery Method - Finding All 6 Motors")
        print("="*70)
        print()
        
        # Step 1: Initialize adapter
        print("Step 1: Initializing adapter...")
        ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
        time.sleep(0.5)
        ser.read(500)
        print("  [OK]")
        print()
        
        # Step 2: Device read (like Motor Studio does)
        print("Step 2: Sending device read (AT+A)...")
        ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A
        time.sleep(0.5)
        ser.read(500)
        print("  [OK]")
        print()
        
        # Step 3: CanOPEN NMT Start All (broadcast) - CRITICAL for CanOPEN
        print("Step 3: Sending CanOPEN NMT Start All (broadcast)...")
        print("  This puts all CanOPEN nodes into Operational state")
        
        # NMT Start All: CAN ID 0x000, Data [0x01, 0x00]
        # Format: AT + command + CAN ID + data
        nmt_commands = [
            # Format 1: AT 20 00 00 02 00 01 00 ...
            bytearray([0x41, 0x54, 0x20, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x0d, 0x0a]),
            # Format 2: Try with different structure
            bytearray([0x41, 0x54, 0x00, 0x00, 0x00, 0x01, 0x00, 0x0d, 0x0a]),
        ]
        
        for i, nmt_cmd in enumerate(nmt_commands, 1):
            print(f"  Trying NMT format {i}...")
            ser.reset_input_buffer()
            ser.write(bytes(nmt_cmd))
            time.sleep(1.0)
            
            # Listen for boot messages (CanOPEN nodes send boot-up after NMT Start)
            boot_responses = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    boot_responses.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(boot_responses) > 4:
                print(f"    Got responses: {boot_responses.hex()[:60]}...")
        
        print("  [OK] Waiting 2 seconds for nodes to enter Operational state...")
        time.sleep(2.0)
        print()
        
        # Step 4: Query each motor with Motor Studio's exact command format
        print("Step 4: Querying each motor (Motor Studio format)...")
        print("-" * 70)
        
        motor_queries = {
            1: bytes.fromhex("41542007e80c0800c40000000000000d0a"),
            3: bytes.fromhex("41542007e81c0800c40000000000000d0a"),
            7: bytes.fromhex("41542007e83c0800c40000000000000d0a"),
            9: bytes.fromhex("41542007e84c0800c40000000000000d0a"),
            11: bytes.fromhex("41540007e89c01000d0a"),
            14: bytes.fromhex("41542007e8740800c40000000000000d0a"),
        }
        
        # Query in specific order - Motor Studio might query in batches
        query_order = [1, 3, 7, 9, 11, 14]
        
        for motor_id in query_order:
            query_cmd = motor_queries[motor_id]
            
            print(f"\nQuerying Motor {motor_id}...")
            ser.reset_input_buffer()
            ser.write(query_cmd)
            
            # Wait longer for response (some motors may respond slower)
            time.sleep(1.5)
            
            # Collect all responses
            responses = bytearray()
            start = time.time()
            while time.time() - start < 2.5:
                if ser.in_waiting > 0:
                    responses.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            # Parse responses
            message_buffer = responses
            messages = []
            msg_buf = bytearray()
            
            for byte in message_buffer:
                msg_buf.append(byte)
                if len(msg_buf) >= 2 and msg_buf[-2] == 0x0d and msg_buf[-1] == 0x0a:
                    messages.append(msg_buf.hex())
                    msg_buf = bytearray()
            
            if len(msg_buf) > 0:
                messages.append(msg_buf.hex())
            
            # Check for motor responses
            found_motor = False
            for msg in messages:
                if len(msg) > 10:
                    detected_id = extract_motor_id(msg)
                    if detected_id == motor_id:
                        motors_found[motor_id].append(msg)
                        print(f"  [OK] Motor {motor_id} detected!")
                        found_motor = True
                    elif detected_id:
                        print(f"  [?] Got Motor {detected_id} instead (querying {motor_id})")
                    elif len(msg) > 20:
                        print(f"  [?] Unparsed response: {msg[:60]}...")
            
            if not found_motor and len(messages) == 0:
                print(f"  [X] No response from Motor {motor_id}")
            
            # Small delay between queries (Motor Studio might do this)
            time.sleep(0.3)
        
        ser.close()
        
        # Final Summary
        print()
        print("="*70)
        print("DISCOVERY RESULTS")
        print("="*70)
        print()
        
        found = sorted([m for m in motors_found.keys()])
        missing = [m for m in KNOWN_MOTORS if m not in found]
        
        print(f"Found: {len(found)} out of {len(KNOWN_MOTORS)} motors")
        print()
        
        if found:
            print("DETECTED MOTORS:")
            for motor_id in found:
                count = len(motors_found[motor_id])
                print(f"  Motor {motor_id}: {count} response(s)")
        
        if missing:
            print()
            print(f"MISSING MOTORS ({len(missing)}):")
            for motor_id in missing:
                print(f"  Motor {motor_id}")
        
        print()
        print("="*70)
        
        if len(found) == 4:
            print("\n[SUCCESS] Found 4 out of 6 - matches Motor Studio behavior!")
            print(f"Missing: {missing}")
            print("\nThis suggests Motors {missing} may need:")
            print("  - Different initialization sequence")
            print("  - Individual activation before query")
            print("  - Different query timing/delays")
            print("  - Or may have different CanOPEN node configuration")
        elif len(found) < 4:
            print(f"\nFound {len(found)} motors (Motor Studio finds 4)")
            print("Possible issues:")
            print("  - CanOPEN NMT commands not working correctly")
            print("  - Motors not in correct state")
            print("  - Timing/delay issues")
        elif len(found) == len(KNOWN_MOTORS):
            print("\n[SUCCESS] Found ALL 6 motors!")
        
        return motors_found
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print()
    print("Replicating Motor Studio discovery method...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = motor_studio_discovery(port)

