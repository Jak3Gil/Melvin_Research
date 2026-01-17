#!/usr/bin/env python3
"""
Solve CAN Bus Arbitration Issues
Query motors in reverse priority order (high IDs first) to prevent arbitration conflicts
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
    
    if msg_clean.startswith('41541000'):
        if len(msg_clean) >= 12:
            id_bytes = msg_clean[8:12]
            known_responses = {
                '0fec': 1,
                '1fec': 3,
                '77ec': 14,
                '3fec': 7,   # Try patterns
                '4fec': 9,
                '9fec': 11,
            }
            if id_bytes in known_responses:
                return known_responses[id_bytes]
    
    return None

def solve_arbitration_issue(port='COM6', baudrate=921600):
    """
    Solve CAN bus arbitration by:
    1. Querying high-ID motors FIRST (they have lower priority, need to respond before low-ID motors interfere)
    2. Using longer delays between queries
    3. Extended timeouts for responses
    4. Passive listening after all queries for delayed retries
    """
    
    motors_found = defaultdict(list)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=5.0)
        print("="*70)
        print("Solving CAN Bus Arbitration Issue")
        print("="*70)
        print()
        print("Strategy:")
        print("  1. Query HIGH-ID motors FIRST (14, 11, 9, 7)")
        print("  2. Then query LOW-ID motors (3, 1)")
        print("  3. Long delays between queries (3 seconds)")
        print("  4. Extended timeouts (5 seconds per response)")
        print("  5. Passive listening for delayed retries (10 seconds)")
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
        
        # Motor queries
        motor_queries = {
            1: bytes.fromhex("41542007e80c0800c40000000000000d0a"),
            3: bytes.fromhex("41542007e81c0800c40000000000000d0a"),
            7: bytes.fromhex("41542007e83c0800c40000000000000d0a"),
            9: bytes.fromhex("41542007e84c0800c40000000000000d0a"),
            11: bytes.fromhex("41540007e89c01000d0a"),
            14: bytes.fromhex("41542007e8740800c40000000000000d0a"),
        }
        
        # CRITICAL: Query in REVERSE priority order
        # High IDs first (lower CAN priority) = 14, 11, 9, 7
        # Then low IDs (higher CAN priority) = 3, 1
        query_order = [14, 11, 9, 7, 3, 1]  # Reverse priority order
        
        print("Querying motors in REVERSE priority order:")
        print("="*70)
        print()
        
        for motor_id in query_order:
            query_cmd = motor_queries[motor_id]
            
            print(f"Motor {motor_id} (CAN ID {motor_id}):")
            print(f"  Priority: {'LOW' if motor_id > 10 else 'HIGH'} (higher CAN ID = lower priority)")
            
            # Clear buffer completely
            ser.reset_input_buffer()
            time.sleep(0.3)
            
            # Send query
            print(f"  Sending query...")
            ser.write(query_cmd)
            
            # Extended timeout for response (motors may need time after bus contention)
            print(f"  Waiting for response (5 second timeout)...")
            response = bytearray()
            start_time = time.time()
            
            # Collect response with extended timeout
            while time.time() - start_time < 5.0:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    response.extend(data)
                    
                    # Check if we have complete message
                    if len(response) >= 2 and response[-2] == 0x0d and response[-1] == 0x0a:
                        # Complete message - wait a bit more in case there's more data
                        time.sleep(0.3)
                        if ser.in_waiting == 0:
                            break
                
                time.sleep(0.1)
            
            # Final read
            if ser.in_waiting > 0:
                response.extend(ser.read(ser.in_waiting))
            
            # Parse response
            if len(response) > 4:
                resp_hex = response.hex()
                elapsed = time.time() - start_time
                print(f"  Response received after {elapsed:.2f}s: {len(response)} bytes")
                print(f"    Hex: {resp_hex[:60]}...")
                
                detected_id = extract_motor_id(resp_hex)
                
                if detected_id == motor_id:
                    motors_found[motor_id].append(resp_hex)
                    print(f"  [OK] Motor {motor_id} DETECTED!")
                elif detected_id:
                    print(f"  [?] Got Motor {detected_id} instead of {motor_id}")
                else:
                    print(f"  [?] Response received but couldn't parse ID")
                    # Store for analysis
                    motors_found[motor_id].append(f"UNPARSED:{resp_hex}")
            else:
                print(f"  [X] No response from Motor {motor_id}")
            
            print()
            
            # CRITICAL: Long delay between queries to let bus settle
            # High-ID motors need more time after low-ID motors respond
            delay = 3.0  # 3 second delay
            print(f"  Waiting {delay} seconds before next query (allows bus to settle)...")
            time.sleep(delay)
            print()
        
        # Step 2: Passive listening for delayed retries
        print("="*70)
        print("Step 2: Passive listening for delayed responses")
        print("="*70)
        print()
        print("Motors that lost arbitration may retry now...")
        print("Listening for 10 seconds...")
        print()
        
        passive_start = time.time()
        message_buffer = bytearray()
        passive_responses = []
        
        while time.time() - passive_start < 10.0:
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
                    
                    if len(msg_hex) > 10:
                        elapsed = time.time() - passive_start
                        detected_id = extract_motor_id(msg_hex)
                        
                        if detected_id:
                            motors_found[detected_id].append(msg_hex)
                            print(f"  [{elapsed:.1f}s] Motor {detected_id} detected (delayed retry)!")
                        
                        passive_responses.append(msg_hex)
                    
                    message_buffer = message_buffer[crlf_pos+2:]
                else:
                    break
            
            time.sleep(0.1)
        
        print(f"\n  Passive listening complete: {len(passive_responses)} additional message(s)")
        print()
        
        ser.close()
        
        # Final Summary
        print("="*70)
        print("ARBITRATION SOLUTION RESULTS")
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
        
        if len(found) == len(KNOWN_MOTORS):
            print("\n[SUCCESS] Found ALL 6 motors!")
            print("CAN bus arbitration solution worked!")
        elif len(found) > 3:
            print(f"\n[PROGRESS] Found {len(found)} motors (up from 3)!")
            print("Arbitration solution is helping.")
        else:
            print(f"\nStill finding {len(found)} motors.")
            print("May need further adjustments or different approach.")
        
        print("="*70)
        
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
    print("Solving CAN bus arbitration issue...")
    print("Querying high-ID motors first to prevent conflicts")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = solve_arbitration_issue(port)

