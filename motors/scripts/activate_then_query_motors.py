#!/usr/bin/env python3
"""
Activate motors first, then query them
Motors 7, 9, 11 might need activation before they respond
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
            }
            if id_bytes in known_responses:
                return known_responses[id_bytes]
    
    return None

def activate_motor(ser, motor_id):
    """Activate a motor using L91 activate command"""
    # Format: AT 00 07 e8 <can_id_byte> 01 00 0d 0a
    motor_byte_map = {
        1: 0x0c, 3: 0x1c, 7: 0x3c, 9: 0x4c, 11: 0x9c, 14: 0x74
    }
    
    can_id_byte = motor_byte_map.get(motor_id)
    if can_id_byte is None:
        return False
    
    # Activate command: AT 00 07 e8 <byte> 01 00
    cmd = bytearray([0x41, 0x54, 0x20, 0x00, 0x07, 0xe8])
    cmd.append(can_id_byte)
    cmd.extend([0x01, 0x00, 0x0d, 0x0a])
    
    ser.write(bytes(cmd))
    time.sleep(0.5)
    response = ser.read(200)
    return len(response) > 0

def query_motor(ser, motor_id):
    """Query a motor using the exact command format"""
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
        return None, ""
    
    ser.reset_input_buffer()
    ser.write(query_cmd)
    time.sleep(1.0)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < 2.5:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.1)
    
    if ser.in_waiting > 0:
        response.extend(ser.read(ser.in_waiting))
    
    return response.hex() if len(response) > 0 else None, response.hex()

def activate_and_query_all(port='COM6', baudrate=921600):
    """Activate each motor, then query it"""
    
    motors_found = defaultdict(list)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Activate Then Query - Finding All 6 Motors")
        print("="*70)
        print()
        
        # Initialize
        print("Initializing adapter...")
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(200)
        print("  [OK]")
        print()
        
        # Device read
        print("Sending device read...")
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(200)
        print("  [OK]")
        print()
        
        # For each motor: activate, then query
        print("Activating and querying each motor:")
        print("-" * 70)
        
        for motor_id in KNOWN_MOTORS:
            print(f"\nMotor {motor_id}:")
            
            # Step 1: Activate
            print(f"  Step 1: Activating Motor {motor_id}...")
            if activate_motor(ser, motor_id):
                print(f"    [OK] Activation command sent")
            else:
                print(f"    [INFO] Activation command sent (no response expected)")
            
            time.sleep(0.5)
            
            # Step 2: Query
            print(f"  Step 2: Querying Motor {motor_id}...")
            resp_hex, full_resp = query_motor(ser, motor_id)
            
            if resp_hex:
                print(f"    Response: {resp_hex[:80]}...")
                detected_id = extract_motor_id(resp_hex)
                
                if detected_id == motor_id:
                    motors_found[motor_id].append(resp_hex)
                    print(f"    [SUCCESS] Motor {motor_id} detected!")
                elif detected_id:
                    print(f"    [?] Got Motor {detected_id} instead")
                else:
                    print(f"    [?] Response received but couldn't parse ID")
                    # Store it anyway
                    motors_found[motor_id].append(f"UNPARSED:{resp_hex}")
            else:
                print(f"    [X] No response")
            
            time.sleep(0.5)
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("RESULTS")
        print("="*70)
        print()
        
        found = sorted([m for m in motors_found.keys() if motors_found[m] and not motors_found[m][0].startswith("UNPARSED")])
        unparsed = [m for m in motors_found.keys() if motors_found[m] and motors_found[m][0].startswith("UNPARSED")]
        missing = [m for m in KNOWN_MOTORS if m not in motors_found.keys()]
        
        print(f"Found: {len(found)} motors")
        if found:
            print("  Motors:", found)
        
        if unparsed:
            print(f"\nUnparsed responses: {len(unparsed)} motors")
            for m in unparsed:
                print(f"  Motor {m}: {motors_found[m][0]}")
        
        if missing:
            print(f"\nMissing: {len(missing)} motors")
            print("  Motors:", missing)
        
        print()
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
    print("Activating then querying all motors...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = activate_and_query_all(port)

