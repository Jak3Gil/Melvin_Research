#!/usr/bin/env python3
"""
Comprehensive motor scanning - tries everything to find all 6 motors
Collects ALL responses and analyzes which motors are detected
"""
import serial
import struct
import time
import sys
from collections import defaultdict

KNOWN_MOTORS = [1, 3, 7, 9, 11, 14]

def extract_motor_id(msg_hex):
    """Extract motor ID from response message"""
    msg_clean = msg_hex.replace('0d0a', '').lower()
    
    if not msg_clean.startswith('4154'):
        return None
    
    # NEW FORMAT: 41541000XXec... (response format)
    # Motor 1: 415410000fec... (0fec)
    # Motor 3: 415410001fec... (1fec)
    # Motor 14: 4154100077ec... (77ec)
    if msg_clean.startswith('41541000'):
        if len(msg_clean) >= 12:
            # Look at bytes 8-11 (after 41541000)
            id_bytes = msg_clean[8:12]  # e.g., "0fec", "1fec", "77ec"
            try:
                id_val = int(id_bytes, 16)
                # Try to decode: 0fec, 1fec, 77ec
                # 0fec = 4076, 1fec = 8172, 77ec = 30668
                # Maybe: (id_val >> 8) or extract from lower bytes?
                # Or reverse: ec = 236, the ID might be in different position
                # Let me try: 0f = 15? 1f = 31? 77 = 119?
                # Actually looking at pattern: 0f, 1f, 77
                # If we shift or mask: 0f >> 4 = 0, 1f >> 4 = 1, 77 >> 4 = 7... no
                # Let me try the first byte: 0f & 0x0f = 15, 1f & 0x0f = 15... no
                # Maybe: 0fec -> 0f = motor 1? 1fec -> 1f = motor 3? 77ec -> 77 = motor 14?
                # 0f = 15, 1f = 31, 77 = 119 - these don't directly map
                # Let's try extracting from the pattern we see
                # For now, create a mapping based on observed values
                known_responses = {
                    '0fec': 1,   # Motor 1
                    '1fec': 3,   # Motor 3
                    '77ec': 14,  # Motor 14
                }
                if id_bytes in known_responses:
                    return known_responses[id_bytes]
            except:
                pass
    
    # Original long format: 41542007e8XX...
    if msg_clean.startswith('41542007e8'):
        if len(msg_clean) >= 12:
            id_byte = msg_clean[10:12]
            motor_map = {'0c': 1, '1c': 3, '3c': 7, '4c': 9, '74': 14}
            return motor_map.get(id_byte)
    
    # Original short format: 41540007e8XX...
    elif msg_clean.startswith('41540007e8'):
        if len(msg_clean) >= 12:
            id_byte = msg_clean[10:12]
            motor_map = {'7c': 7, '9c': 11}
            return motor_map.get(id_byte)
    
    return None

def comprehensive_scan(port='COM6', baudrate=921600):
    """Comprehensive scan trying all methods"""
    
    all_responses = []
    motors_detected = defaultdict(list)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print("="*70)
        print("Comprehensive Motor Scan - Finding All 6 Motors")
        print("="*70)
        print(f"Port: {port} at {baudrate} baud")
        print()
        
        # Initialize
        print("Step 1: Initializing adapter...")
        ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
        time.sleep(0.5)
        ser.read(200)
        print("  [OK]")
        print()
        
        # Step 2: Send device read
        print("Step 2: Sending device read command...")
        ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A
        time.sleep(0.5)
        ser.read(200)
        print("  [OK]")
        print()
        
        # Step 3: Send CanOPEN NMT Start All (broadcast)
        print("Step 3: Sending CanOPEN NMT Start All (broadcast)...")
        nmt_all = bytearray([0x41, 0x54, 0x20, 0x00, 0x00, 0x02, 0x00, 0x01, 0x00, 0x0d, 0x0a])
        ser.write(bytes(nmt_all))
        time.sleep(1.0)
        print("  [OK] Waiting for boot messages...")
        time.sleep(1.0)
        
        # Collect all responses from NMT
        buffer = bytearray()
        start = time.time()
        while time.time() - start < 2.0:
            if ser.in_waiting > 0:
                buffer.extend(ser.read(ser.in_waiting))
            time.sleep(0.05)
        
        # Parse responses
        messages = []
        msg_buf = bytearray()
        for byte in buffer:
            msg_buf.append(byte)
            if len(msg_buf) >= 2 and msg_buf[-2] == 0x0d and msg_buf[-1] == 0x0a:
                messages.append(msg_buf.hex())
                all_responses.extend(msg_buf)
                msg_buf = bytearray()
        
        print(f"  Collected {len(messages)} message(s) from NMT")
        for msg in messages:
            motor_id = extract_motor_id(msg)
            if motor_id:
                motors_detected[motor_id].append(msg)
                print(f"    -> Motor {motor_id} detected!")
        print()
        
        # Step 4: Query each motor individually using exact captured formats
        print("Step 4: Querying each motor individually...")
        motor_queries = {
            1: bytes.fromhex("41542007e80c0800c40000000000000d0a"),
            3: bytes.fromhex("41542007e81c0800c40000000000000d0a"),
            7: bytes.fromhex("41542007e83c0800c40000000000000d0a"),  # Exact format from user
            9: bytes.fromhex("41542007e84c0800c40000000000000d0a"),  # Exact format from user
            11: bytes.fromhex("41540007e89c01000d0a"),                 # Exact format from user
            14: bytes.fromhex("41542007e8740800c40000000000000d0a"),
        }
        
        for motor_id, query_cmd in sorted(motor_queries.items()):
            print(f"  Querying Motor {motor_id}...")
            ser.reset_input_buffer()
            ser.write(query_cmd)
            time.sleep(0.8)  # Longer wait for motors 7, 9, 11
            
            # Collect response
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:  # Longer timeout
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            # Also check for any remaining data
            if ser.in_waiting > 0:
                response.extend(ser.read(ser.in_waiting))
            
            if len(response) > 0:
                resp_hex = response.hex()
                detected_id = extract_motor_id(resp_hex)
                if detected_id == motor_id:
                    motors_detected[motor_id].append(resp_hex)
                    print(f"    [OK] Motor {motor_id} responded!")
                elif detected_id:
                    print(f"    [?] Got response from Motor {detected_id} instead of {motor_id}")
                else:
                    print(f"    [?] Got response but couldn't parse: {resp_hex[:40]}...")
            else:
                print(f"    [X] No response")
        
        print()
        
        # Step 5: Try CanOPEN SDO queries
        print("Step 5: Trying CanOPEN SDO queries...")
        for motor_id in KNOWN_MOTORS:
            cob_id = 0x600 + motor_id
            sdo_cmd = bytearray([0x41, 0x54, 0x20])
            sdo_cmd.extend(struct.pack('<H', cob_id))
            sdo_cmd.extend([0x08, 0x00])
            sdo_cmd.extend([0x40, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00])
            while len(sdo_cmd) < 22:
                sdo_cmd.append(0x00)
            sdo_cmd.extend([0x0d, 0x0a])
            
            ser.reset_input_buffer()
            ser.write(bytes(sdo_cmd))
            time.sleep(0.3)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 0.5:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.05)
            
            if len(response) > 4:
                resp_hex = response.hex()
                detected_id = extract_motor_id(resp_hex)
                if detected_id:
                    motors_detected[detected_id].append(resp_hex)
                    if detected_id == motor_id:
                        print(f"  [OK] Motor {motor_id} via SDO!")
        
        print()
        
        # Step 6: Final passive listen
        print("Step 6: Final passive listening (5 seconds)...")
        ser.reset_input_buffer()
        time.sleep(5.0)
        
        buffer = bytearray()
        start = time.time()
        while time.time() - start < 5.0:
            if ser.in_waiting > 0:
                buffer.extend(ser.read(ser.in_waiting))
            time.sleep(0.05)
        
        # Parse final messages
        msg_buf = bytearray()
        for byte in buffer:
            msg_buf.append(byte)
            if len(msg_buf) >= 2 and msg_buf[-2] == 0x0d and msg_buf[-1] == 0x0a:
                msg_hex = msg_buf.hex()
                motor_id = extract_motor_id(msg_hex)
                if motor_id:
                    motors_detected[motor_id].append(msg_hex)
                    print(f"  Motor {motor_id} detected in passive listen!")
                msg_buf = bytearray()
        
        ser.close()
        
        # Final Summary
        print()
        print("="*70)
        print("SCAN RESULTS")
        print("="*70)
        print()
        
        found = sorted(motors_detected.keys())
        missing = [m for m in KNOWN_MOTORS if m not in found]
        
        print(f"Motors Detected: {len(found)} out of {len(KNOWN_MOTORS)}")
        print()
        
        if found:
            print("FOUND MOTORS:")
            for motor_id in found:
                count = len(motors_detected[motor_id])
                print(f"  Motor {motor_id}: {count} message(s)")
        else:
            print("No motors detected!")
        
        if missing:
            print()
            print("MISSING MOTORS:")
            for motor_id in missing:
                print(f"  Motor {motor_id}: Not detected")
        
        print()
        print("="*70)
        
        if len(found) == 4:
            print("\n[DIAGNOSIS] Only 4 out of 6 motors detected - matches your issue!")
            print("Missing motors:", missing)
            print("\nPossible causes:")
            print("  - CanOPEN node state issues")
            print("  - Bus priority/timing conflicts")
            print("  - Motors need individual initialization")
            print("  - Query order dependency")
        
        return motors_detected
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        print("\nClose Motor Studio and other programs using COM6!")
        return None
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
    print("Make sure all 6 motors are connected and powered!")
    print("Starting comprehensive scan in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = comprehensive_scan(port)

