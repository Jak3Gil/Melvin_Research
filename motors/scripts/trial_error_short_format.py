#!/usr/bin/env python3
"""
Test short format for motors 7, 9, 11
Motor 11 uses short format: 41540007e89c01000d0a
Maybe motors 7 and 9 also use short format?
"""
import serial
import time
import sys
from collections import defaultdict

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

def test_short_format(port='COM6', baudrate=921600):
    """
    Test short format: AT 00 07 e8 [byte] 01 00 0d 0a
    Motor 11 uses this format with byte 0x9c
    """
    
    motors_found = defaultdict(list)
    all_responses = []
    
    try:
        ser = serial.Serial(port, baudrate, timeout=3.0)
        print("="*70)
        print("Testing Short Format for Motors 7, 9, 11")
        print("="*70)
        print()
        print("Short format: AT 00 07 e8 [BYTE] 01 00 0d 0a")
        print("Motor 11 uses this with byte 0x9c")
        print("Maybe motors 7 and 9 also use this format?")
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
        
        # Test likely byte values for short format
        # Motor 11: 0x9c
        # Motors 7, 9 might be: 0x7c, 0x8c, 0xac, 0xbc, etc.
        
        # Focus on values around 0x9c and patterns
        test_bytes = []
        
        # Around motor 11's 0x9c
        test_bytes.extend(range(0x7c, 0xa0))
        
        # Other patterns
        test_bytes.extend([0x3c, 0x4c, 0x5c, 0x6c])  # Motors 7, 9 might use these
        
        # Remove duplicates and sort
        test_bytes = sorted(set(test_bytes))
        
        print(f"Testing {len(test_bytes)} byte values with short format...")
        print("-" * 70)
        print()
        
        for byte_val in test_bytes:
            # Short format: AT 00 07 e8 [byte] 01 00 0d 0a
            cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val])
            cmd.extend([0x01, 0x00, 0x0d, 0x0a])
            
            ser.reset_input_buffer()
            ser.write(bytes(cmd))
            time.sleep(0.5)
            
            # Collect response
            response = bytearray()
            start = time.time()
            while time.time() - start < 1.5:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.05)
            
            if len(response) > 4:
                resp_hex = response.hex()
                detected_id = extract_motor_id(resp_hex)
                
                if detected_id:
                    motors_found[detected_id].append({
                        'byte': byte_val,
                        'response': resp_hex,
                        'format': 'short'
                    })
                    print(f"  [FOUND] Byte 0x{byte_val:02x} (short format) -> Motor {detected_id}!")
                    print(f"          Response: {resp_hex[:60]}...")
                elif len(resp_hex) > 10:
                    all_responses.append({
                        'byte': byte_val,
                        'response': resp_hex,
                        'format': 'short'
                    })
                    print(f"  [?] Byte 0x{byte_val:02x} (short) -> Response: {resp_hex[:50]}...")
            
            time.sleep(0.1)
            
            # Progress
            if byte_val % 10 == 0:
                print(f"    Progress: 0x{byte_val:02x}...")
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("SHORT FORMAT TEST RESULTS")
        print("="*70)
        print()
        
        if motors_found:
            print("MOTORS FOUND with short format:")
            for motor_id in sorted(motors_found.keys()):
                for result in motors_found[motor_id]:
                    print(f"  Motor {motor_id}: Byte 0x{result['byte']:02x}")
                    print(f"    Response: {result['response'][:60]}...")
        
        if all_responses:
            print(f"\nUNPARSED RESPONSES ({len(all_responses)}):")
            for result in all_responses[:20]:
                print(f"  Byte 0x{result['byte']:02x}: {result['response'][:50]}...")
        
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
    print("Testing short format for motors 7, 9, 11...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = test_short_format(port)

