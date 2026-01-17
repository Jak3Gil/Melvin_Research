#!/usr/bin/env python3
"""
Broadcast Discovery - Maybe motors 7, 9, 11 only respond to broadcast queries
when all motors are connected together
"""
import serial
import time
import sys
from collections import defaultdict

KNOWN_MOTORS = [1, 3, 7, 9, 11, 14]

def extract_all_motor_ids_from_responses(all_responses):
    """Extract all motor IDs from all responses"""
    motors_found = set()
    
    for resp_hex in all_responses:
        msg_clean = resp_hex.replace('0d0a', '').lower()
        
        if msg_clean.startswith('41541000'):
            if len(msg_clean) >= 12:
                id_bytes = msg_clean[8:12]
                known_responses = {
                    '0fec': 1,
                    '1fec': 3,
                    '77ec': 14,
                    '3fec': 7,   # Possible patterns
                    '4fec': 9,
                    '9fec': 11,
                }
                detected_id = known_responses.get(id_bytes)
                if detected_id:
                    motors_found.add(detected_id)
    
    return motors_found

def broadcast_discovery(port='COM6', baudrate=921600):
    """
    Try broadcast queries that might trigger all motors to respond
    Motor Studio might use broadcast "WhoIs" or similar queries
    """
    
    all_responses = []
    motors_found = set()
    
    try:
        ser = serial.Serial(port, baudrate, timeout=3.0)
        print("="*70)
        print("Broadcast Discovery - Finding All 6 Motors")
        print("="*70)
        print()
        print("Theory: Motors 7, 9, 11 may only respond to broadcast queries")
        print("when all motors are connected together")
        print()
        
        # Initialize
        print("Initializing adapter...")
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        print("  [OK]")
        print()
        
        # Method 1: Device read command (this might be a broadcast query)
        print("METHOD 1: Device Read Command (AT+A) - might trigger all motors")
        print("-" * 70)
        
        ser.reset_input_buffer()
        ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A
        time.sleep(0.5)
        
        # Collect ALL responses for 5 seconds
        print("Collecting responses for 5 seconds...")
        responses_method1 = bytearray()
        start = time.time()
        while time.time() - start < 5.0:
            if ser.in_waiting > 0:
                responses_method1.extend(ser.read(ser.in_waiting))
            time.sleep(0.1)
        
        # Parse responses
        messages = []
        msg_buf = bytearray()
        for byte in responses_method1:
            msg_buf.append(byte)
            if len(msg_buf) >= 2 and msg_buf[-2] == 0x0d and msg_buf[-1] == 0x0a:
                messages.append(msg_buf.hex())
                all_responses.append(msg_buf.hex())
                msg_buf = bytearray()
        
        if len(msg_buf) > 0:
            messages.append(msg_buf.hex())
            all_responses.append(msg_buf.hex())
        
        print(f"  Captured {len(messages)} message(s) from device read")
        for i, msg in enumerate(messages[:10], 1):
            print(f"    [{i}] {msg[:60]}...")
        
        detected = extract_all_motor_ids_from_responses(messages)
        motors_found.update(detected)
        print(f"  Motors detected: {sorted(detected)}")
        print()
        
        # Method 2: CanOPEN NMT WhoIs / Node Guarding broadcast
        print("METHOD 2: CanOPEN Broadcast Queries")
        print("-" * 70)
        
        # Try different broadcast formats
        broadcast_commands = [
            # NMT WhoIs (node discovery)
            ("NMT WhoIs", bytearray([0x41, 0x54, 0x20, 0x00, 0x00, 0x01, 0x00, 0x0d, 0x0a])),
            # Device read variations
            ("Device Read 2", bytes.fromhex("41542b41010d0a")),
            ("Device Read 3", bytes.fromhex("41542b41ff0d0a")),
        ]
        
        for name, cmd in broadcast_commands:
            print(f"  Trying {name}...")
            ser.reset_input_buffer()
            ser.write(bytes(cmd) if isinstance(cmd, bytearray) else cmd)
            time.sleep(0.5)
            
            # Collect responses
            responses = bytearray()
            start = time.time()
            while time.time() - start < 3.0:
                if ser.in_waiting > 0:
                    responses.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            # Parse
            msg_buf = bytearray()
            for byte in responses:
                msg_buf.append(byte)
                if len(msg_buf) >= 2 and msg_buf[-2] == 0x0d and msg_buf[-1] == 0x0a:
                    msg_hex = msg_buf.hex()
                    all_responses.append(msg_hex)
                    msg_buf = bytearray()
            
            if len(responses) > 4:
                print(f"    Got {len(responses)} bytes: {responses.hex()[:60]}...")
                detected = extract_all_motor_ids_from_responses([responses.hex()])
                motors_found.update(detected)
                if detected:
                    print(f"    Motors detected: {sorted(detected)}")
            else:
                print(f"    No response")
        
        print()
        
        # Method 3: Send all individual queries rapidly, then listen
        print("METHOD 3: Send all queries rapidly, then passive listen")
        print("-" * 70)
        
        motor_queries = {
            1: bytes.fromhex("41542007e80c0800c40000000000000d0a"),
            3: bytes.fromhex("41542007e81c0800c40000000000000d0a"),
            7: bytes.fromhex("41542007e83c0800c40000000000000d0a"),
            9: bytes.fromhex("41542007e84c0800c40000000000000d0a"),
            11: bytes.fromhex("41540007e89c01000d0a"),
            14: bytes.fromhex("41542007e8740800c40000000000000d0a"),
        }
        
        print("Sending all queries in rapid succession...")
        ser.reset_input_buffer()
        for motor_id in sorted(motor_queries.keys()):
            ser.write(motor_queries[motor_id])
            time.sleep(0.1)  # Very short delay
        
        print("Listening for all responses (10 seconds)...")
        time.sleep(1.0)  # Initial wait
        
        responses_all = bytearray()
        start = time.time()
        while time.time() - start < 10.0:
            if ser.in_waiting > 0:
                responses_all.extend(ser.read(ser.in_waiting))
            time.sleep(0.1)
        
        # Parse all responses
        msg_buf = bytearray()
        for byte in responses_all:
            msg_buf.append(byte)
            if len(msg_buf) >= 2 and msg_buf[-2] == 0x0d and msg_buf[-1] == 0x0a:
                msg_hex = msg_buf.hex()
                all_responses.append(msg_hex)
                msg_buf = bytearray()
        
        detected = extract_all_motor_ids_from_responses(all_responses)
        motors_found.update(detected)
        
        if len(responses_all) > 0:
            print(f"  Captured {len(responses_all)} bytes total")
            print(f"  Motors detected: {sorted(detected)}")
        else:
            print(f"  No responses captured")
        
        ser.close()
        
        # Final Summary
        print()
        print("="*70)
        print("BROADCAST DISCOVERY RESULTS")
        print("="*70)
        print()
        
        found = sorted(list(motors_found))
        missing = [m for m in KNOWN_MOTORS if m not in found]
        
        print(f"Total unique motors detected: {len(found)} out of {len(KNOWN_MOTORS)}")
        print()
        
        if found:
            print("DETECTED MOTORS:")
            for motor_id in found:
                print(f"  Motor {motor_id}")
        
        if missing:
            print()
            print(f"MISSING MOTORS ({len(missing)}):")
            for motor_id in missing:
                print(f"  Motor {motor_id}")
        
        print()
        print(f"Total responses captured: {len(all_responses)}")
        print()
        print("="*70)
        
        if len(found) == len(KNOWN_MOTORS):
            print("\n[SUCCESS] Found ALL 6 motors using broadcast discovery!")
        elif len(found) > 3:
            print(f"\n[PROGRESS] Found {len(found)} motors (improvement)!")
        
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
    print("Trying broadcast discovery methods...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = broadcast_discovery(port)

