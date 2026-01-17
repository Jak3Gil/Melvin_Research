#!/usr/bin/env python3
"""
Find the missing 3 motors (7, 9, 11) by trying different query formats
"""
import serial
import struct
import time
import sys
from collections import defaultdict

def extract_motor_id_new_format(msg_hex):
    """Extract motor ID from new response format: 41541000XXec..."""
    msg_clean = msg_hex.replace('0d0a', '').lower()
    
    if not msg_clean.startswith('4154'):
        return None
    
    # New response format: 41541000XXec...
    if msg_clean.startswith('41541000'):
        if len(msg_clean) >= 12:
            id_bytes = msg_clean[8:12]
            known_responses = {
                '0fec': 1,
                '1fec': 3,
                '77ec': 14,
                # Need to find: 7, 9, 11
            }
            if id_bytes in known_responses:
                return known_responses[id_bytes]
    
    return None

def try_query_motor(ser, motor_id, query_cmd, format_name):
    """Try querying a motor and return response"""
    ser.reset_input_buffer()
    ser.write(query_cmd)
    time.sleep(0.5)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < 1.0:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.05)
    
    if len(response) > 4:
        resp_hex = response.hex()
        detected_id = extract_motor_id_new_format(resp_hex)
        
        if detected_id == motor_id:
            return True, resp_hex, "FOUND!"
        elif detected_id:
            return False, resp_hex, f"Got Motor {detected_id} instead"
        else:
            return False, resp_hex, "Response but couldn't parse ID"
    
    return False, "", "No response"

def find_missing_motors(port='COM6', baudrate=921600):
    """Find missing motors 7, 9, 11"""
    
    missing_motors = [7, 9, 11]
    found_motors = {}
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print("="*70)
        print("Finding Missing Motors (7, 9, 11)")
        print("="*70)
        print()
        
        # Initialize
        print("Initializing...")
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(200)
        print("  [OK]")
        print()
        
        # Motor byte mappings
        motor_byte_map = {
            7: [0x3c, 0x7c],   # Try both encodings
            9: [0x4c],
            11: [0x9c],
        }
        
        # Try different query formats for each missing motor
        for motor_id in missing_motors:
            print(f"Testing Motor {motor_id}:")
            print("-" * 70)
            
            can_id_bytes = motor_byte_map.get(motor_id, [])
            if not can_id_bytes:
                print(f"  [SKIP] No byte mapping for Motor {motor_id}")
                continue
            
            for can_id_byte in can_id_bytes:
                print(f"  Trying with byte 0x{can_id_byte:02x}...")
                
                # Format 1: Long format (like Motor 1, 3, 14)
                cmd1 = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8])
                cmd1.append(can_id_byte)
                cmd1.extend([0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00])
                cmd1.extend([0x0d, 0x0a])
                
                success, resp, note = try_query_motor(ser, motor_id, bytes(cmd1), "Long format")
                if success:
                    found_motors[motor_id] = resp
                    print(f"    [SUCCESS] Found Motor {motor_id} with long format!")
                    break
                elif len(resp) > 0:
                    print(f"    Response: {resp[:60]}... ({note})")
                
                time.sleep(0.2)
                
                # Format 2: Short format (like Motor 11 from captured data)
                if motor_id in [7, 11]:
                    cmd2 = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8])
                    cmd2.append(can_id_byte)
                    cmd2.extend([0x01, 0x00, 0x0d, 0x0a])
                    
                    success, resp, note = try_query_motor(ser, motor_id, bytes(cmd2), "Short format")
                    if success:
                        found_motors[motor_id] = resp
                        print(f"    [SUCCESS] Found Motor {motor_id} with short format!")
                        break
                    elif len(resp) > 0:
                        print(f"    Response: {resp[:60]}... ({note})")
                
                time.sleep(0.2)
                
                # Format 3: Try with different command byte (20 vs 00 vs 10)
                for cmd_byte in [0x20, 0x00, 0x10]:
                    cmd3 = bytearray([0x41, 0x54, cmd_byte, 0x07, 0xe8])
                    cmd3.append(can_id_byte)
                    cmd3.extend([0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00])
                    while len(cmd3) < 22:
                        cmd3.append(0x00)
                    cmd3.extend([0x0d, 0x0a])
                    
                    success, resp, note = try_query_motor(ser, motor_id, bytes(cmd3), f"Format with 0x{cmd_byte:02x}")
                    if success:
                        found_motors[motor_id] = resp
                        print(f"    [SUCCESS] Found Motor {motor_id} with command 0x{cmd_byte:02x}!")
                        break
                    elif len(resp) > 20:
                        print(f"    Response: {resp[:60]}... ({note})")
                    
                    time.sleep(0.2)
                
                if motor_id in found_motors:
                    break
            
            if motor_id not in found_motors:
                print(f"  [X] Motor {motor_id} not found with any format")
            
            print()
        
        ser.close()
        
        # Summary
        print("="*70)
        print("RESULTS")
        print("="*70)
        print()
        print(f"Found: {len(found_motors)} out of 3 missing motors")
        print()
        
        if found_motors:
            print("FOUND MOTORS:")
            for motor_id in sorted(found_motors.keys()):
                print(f"  Motor {motor_id}: {found_motors[motor_id][:60]}...")
        
        still_missing = [m for m in missing_motors if m not in found_motors]
        if still_missing:
            print()
            print(f"STILL MISSING: {still_missing}")
        
        print("="*70)
        return found_motors
        
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
    print("Finding missing motors 7, 9, and 11...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = find_missing_motors(port)
