#!/usr/bin/env python3
"""
Debug why we can't find all 6 motors at once
Tests different sequences, timing, and response patterns
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
                # Need to find patterns for 7, 9, 11
                '3fec': 7,  # Guess based on pattern
                '4fec': 9,  # Guess based on pattern
                '9fec': 11, # Guess based on pattern
            }
            if id_bytes in known_responses:
                return known_responses[id_bytes]
    
    return None

def query_motor(ser, motor_id, wait_time=1.0):
    """Query a motor and return all responses"""
    motor_queries = {
        1: bytes.fromhex("41542007e80c0800c40000000000000d0a"),
        3: bytes.fromhex("41542007e81c0800c40000000000000d0a"),
        7: bytes.fromhex("41542007e83c0800c40000000000000d0a"),
        9: bytes.fromhex("41542007e84c0800c40000000000000d0a"),
        11: bytes.fromhex("41540007e89c01000d0a"),
        14: bytes.fromhex("41542007e8740800c40000000000000d0a"),
    }
    
    query_cmd = motor_queries.get(motor_id)
    if query_cmd is None:
        return []
    
    ser.reset_input_buffer()
    ser.write(query_cmd)
    time.sleep(wait_time)
    
    # Collect all responses
    all_responses = []
    message_buffer = bytearray()
    
    start = time.time()
    while time.time() - start < 2.0:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            message_buffer.extend(data)
        
        # Parse complete messages
        while True:
            crlf_pos = -1
            for i in range(len(message_buffer) - 1):
                if message_buffer[i] == 0x0d and message_buffer[i+1] == 0x0a:
                    crlf_pos = i
                    break
            
            if crlf_pos >= 0:
                msg_bytes = message_buffer[:crlf_pos+2]
                msg_hex = msg_bytes.hex()
                all_responses.append(msg_hex)
                message_buffer = message_buffer[crlf_pos+2:]
            else:
                break
        
        time.sleep(0.05)
    
    # Check for any remaining data
    if len(message_buffer) > 0:
        all_responses.append(message_buffer.hex())
    
    return all_responses

def debug_all_motors(port='COM6', baudrate=921600):
    """Comprehensive debugging of why we can't find all 6 at once"""
    
    all_responses_log = []
    motors_found_sequences = []
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Debug: Why Can't We Find All 6 Motors At Once?")
        print("="*70)
        print()
        
        # Initialize
        print("Initializing...")
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(200)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(200)
        print("  [OK]")
        print()
        
        # Test 1: Query all motors in sequence with default timing
        print("="*70)
        print("TEST 1: Query all motors sequentially (default timing)")
        print("="*70)
        
        motors_found_test1 = set()
        for motor_id in KNOWN_MOTORS:
            print(f"\nQuerying Motor {motor_id}...")
            responses = query_motor(ser, motor_id, wait_time=0.5)
            
            for resp in responses:
                all_responses_log.append({
                    'test': 'Test1',
                    'motor': motor_id,
                    'response': resp
                })
                detected_id = extract_motor_id(resp)
                if detected_id:
                    motors_found_test1.add(detected_id)
                    print(f"  -> Detected Motor {detected_id} (expected {motor_id})")
                elif len(resp) > 10:
                    print(f"  -> Unparsed response: {resp[:60]}...")
        
        print(f"\nTest 1 Results: Found {len(motors_found_test1)} motors: {sorted(motors_found_test1)}")
        motors_found_sequences.append(('Sequential (0.5s)', motors_found_test1))
        time.sleep(1.0)
        
        # Test 2: Query all motors with longer delays
        print("\n" + "="*70)
        print("TEST 2: Query all motors with longer delays (1.5s)")
        print("="*70)
        
        motors_found_test2 = set()
        for motor_id in KNOWN_MOTORS:
            print(f"\nQuerying Motor {motor_id}...")
            responses = query_motor(ser, motor_id, wait_time=1.5)
            
            for resp in responses:
                all_responses_log.append({
                    'test': 'Test2',
                    'motor': motor_id,
                    'response': resp
                })
                detected_id = extract_motor_id(resp)
                if detected_id:
                    motors_found_test2.add(detected_id)
                    print(f"  -> Detected Motor {detected_id}")
        
        print(f"\nTest 2 Results: Found {len(motors_found_test2)} motors: {sorted(motors_found_test2)}")
        motors_found_sequences.append(('Long delays (1.5s)', motors_found_test2))
        time.sleep(1.0)
        
        # Test 3: Query known working motors first, then missing ones
        print("\n" + "="*70)
        print("TEST 3: Query working motors (1,3,14) first, then missing (7,9,11)")
        print("="*70)
        
        motors_found_test3 = set()
        working_order = [1, 3, 14, 7, 9, 11]
        
        for motor_id in working_order:
            print(f"\nQuerying Motor {motor_id}...")
            responses = query_motor(ser, motor_id, wait_time=1.0)
            
            for resp in responses:
                all_responses_log.append({
                    'test': 'Test3',
                    'motor': motor_id,
                    'response': resp
                })
                detected_id = extract_motor_id(resp)
                if detected_id:
                    motors_found_test3.add(detected_id)
                    print(f"  -> Detected Motor {detected_id}")
        
        print(f"\nTest 3 Results: Found {len(motors_found_test3)} motors: {sorted(motors_found_test3)}")
        motors_found_sequences.append(('Working-first order', motors_found_test3))
        time.sleep(1.0)
        
        # Test 4: Query only missing motors with longer waits
        print("\n" + "="*70)
        print("TEST 4: Query only missing motors (7,9,11) with 2s delays")
        print("="*70)
        
        motors_found_test4 = set()
        for motor_id in [7, 9, 11]:
            print(f"\nQuerying Motor {motor_id}...")
            responses = query_motor(ser, motor_id, wait_time=2.0)
            
            for resp in responses:
                all_responses_log.append({
                    'test': 'Test4',
                    'motor': motor_id,
                    'response': resp
                })
                detected_id = extract_motor_id(resp)
                if detected_id:
                    motors_found_test4.add(detected_id)
                    print(f"  -> Detected Motor {detected_id}")
                elif len(resp) > 10:
                    print(f"  -> Response: {resp}")
        
        print(f"\nTest 4 Results: Found {len(motors_found_test4)} motors: {sorted(motors_found_test4)}")
        motors_found_sequences.append(('Missing-only (2s)', motors_found_test4))
        
        # Test 5: Continuous passive listening after queries
        print("\n" + "="*70)
        print("TEST 5: Passive listening (10s) after all queries")
        print("="*70)
        
        motors_found_test5 = set()
        print("Listening for 10 seconds...")
        
        start_time = time.time()
        message_buffer = bytearray()
        
        while time.time() - start_time < 10.0:
            if ser.in_waiting > 0:
                message_buffer.extend(ser.read(ser.in_waiting))
            
            # Parse messages
            while True:
                crlf_pos = -1
                for i in range(len(message_buffer) - 1):
                    if message_buffer[i] == 0x0d and message_buffer[i+1] == 0x0a:
                        crlf_pos = i
                        break
                
                if crlf_pos >= 0:
                    msg_bytes = message_buffer[:crlf_pos+2]
                    msg_hex = msg_bytes.hex()
                    
                    all_responses_log.append({
                        'test': 'Test5',
                        'motor': 'passive',
                        'response': msg_hex
                    })
                    
                    detected_id = extract_motor_id(msg_hex)
                    if detected_id:
                        motors_found_test5.add(detected_id)
                        elapsed = time.time() - start_time
                        print(f"  [{elapsed:.1f}s] Detected Motor {detected_id}")
                    
                    message_buffer = message_buffer[crlf_pos+2:]
                else:
                    break
            
            time.sleep(0.1)
        
        print(f"\nTest 5 Results: Found {len(motors_found_test5)} motors: {sorted(motors_found_test5)}")
        motors_found_sequences.append(('Passive listen', motors_found_test5))
        
        ser.close()
        
        # Final Analysis
        print("\n" + "="*70)
        print("DEBUGGING ANALYSIS")
        print("="*70)
        print()
        
        print("Results by Test:")
        for test_name, motors in motors_found_sequences:
            print(f"  {test_name:25s}: {len(motors)} motors - {sorted(motors)}")
        
        # Find which motors were detected in which tests
        print("\nMotor Detection Summary:")
        for motor_id in KNOWN_MOTORS:
            detected_in = [name for name, motors in motors_found_sequences if motor_id in motors]
            if detected_in:
                print(f"  Motor {motor_id:2d}: Detected in {len(detected_in)} test(s) - {', '.join(detected_in)}")
            else:
                print(f"  Motor {motor_id:2d}: NEVER detected in any test")
        
        # Analyze responses
        print("\nResponse Analysis:")
        unique_responses = {}
        for log_entry in all_responses_log:
            resp = log_entry['response']
            if resp not in unique_responses:
                unique_responses[resp] = []
            unique_responses[resp].append(log_entry)
        
        print(f"  Total responses captured: {len(all_responses_log)}")
        print(f"  Unique response patterns: {len(unique_responses)}")
        
        # Show unparsed responses
        unparsed = []
        for resp, entries in unique_responses.items():
            detected_id = extract_motor_id(resp)
            if not detected_id and len(resp) > 20 and resp not in ["4f4b0d0a", "014a0d0a", "014d0d0a"]:
                unparsed.append((resp, len(entries)))
        
        if unparsed:
            print(f"\n  Unparsed responses ({len(unparsed)}):")
            for resp, count in unparsed[:10]:  # Show first 10
                print(f"    [{count}x] {resp[:80]}...")
        
        print()
        print("="*70)
        
        return {
            'sequences': motors_found_sequences,
            'all_responses': all_responses_log
        }
        
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
    print("Debugging why we can't find all 6 motors at once...")
    print("This will run multiple tests with different sequences and timing")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    results = debug_all_motors(port)

