#!/usr/bin/env python3
"""
Sequential Query - Query ONE motor at a time with proper delays
This handles CAN bus contention when all motors are connected together
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
            }
            if id_bytes in known_responses:
                return known_responses[id_bytes]
    
    return None

def sequential_query_all(port='COM6', baudrate=921600):
    """
    Query motors ONE AT A TIME with proper delays
    This prevents CAN bus contention when all motors are connected
    """
    
    motors_found = defaultdict(list)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=3.0)
        print("="*70)
        print("Sequential Query - One Motor At A Time")
        print("="*70)
        print("This method prevents CAN bus contention when all motors are connected")
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
        
        print("Querying motors ONE AT A TIME with proper delays:")
        print("="*70)
        print()
        
        for motor_id in sorted(motor_queries.keys()):
            query_cmd = motor_queries[motor_id]
            
            print(f"Motor {motor_id}:")
            
            # CRITICAL: Clear buffer BEFORE querying
            ser.reset_input_buffer()
            time.sleep(0.2)  # Brief pause after clearing
            
            # Send query
            print(f"  Sending query...")
            ser.write(query_cmd)
            
            # Wait for response with longer timeout
            print(f"  Waiting for response (3 second timeout)...")
            response = bytearray()
            start_time = time.time()
            
            # Collect response carefully
            while time.time() - start_time < 3.0:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    response.extend(data)
                    
                    # If we got a complete message, check if we're done
                    # Messages end with 0d0a
                    if len(response) >= 2 and response[-2] == 0x0d and response[-1] == 0x0a:
                        # Got a complete message, but wait a bit more for any additional data
                        time.sleep(0.2)
                        if ser.in_waiting == 0:
                            break  # No more data, we have complete message
                
                time.sleep(0.05)
            
            # Final read of any remaining data
            if ser.in_waiting > 0:
                response.extend(ser.read(ser.in_waiting))
            
            # Parse response
            if len(response) > 4:
                resp_hex = response.hex()
                print(f"  Response received: {len(response)} bytes")
                print(f"    Hex: {resp_hex[:60]}...")
                
                detected_id = extract_motor_id(resp_hex)
                
                if detected_id == motor_id:
                    motors_found[motor_id].append(resp_hex)
                    print(f"  [OK] Motor {motor_id} DETECTED!")
                elif detected_id:
                    print(f"  [?] Got Motor {detected_id} instead of {motor_id}")
                else:
                    print(f"  [?] Response received but couldn't parse motor ID")
                    # Still store it - might be valid response
                    motors_found[motor_id].append(f"UNPARSED:{resp_hex}")
            else:
                print(f"  [X] No response from Motor {motor_id}")
            
            print()
            
            # CRITICAL: Wait BEFORE querying next motor
            # This gives the CAN bus time to settle and prevents collisions
            print(f"  Waiting 1 second before next query (prevents bus contention)...")
            time.sleep(1.0)
            print()
        
        ser.close()
        
        # Summary
        print("="*70)
        print("SEQUENTIAL QUERY RESULTS")
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
            print("\n[SUCCESS] Found ALL motors using sequential query!")
            print("This confirms it was a CAN bus contention issue.")
        elif len(found) > 3:
            print(f"\n[PROGRESS] Found {len(found)} motors (up from 3)!")
            print("Sequential querying is helping.")
        else:
            print(f"\nStill only finding {len(found)} motors.")
            print("May need even longer delays or different approach.")
        
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
    print("Sequential querying - prevents CAN bus contention!")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = sequential_query_all(port)

