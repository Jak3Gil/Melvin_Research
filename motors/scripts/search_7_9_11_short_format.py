#!/usr/bin/env python3
"""
Search for motors 7, 9, 11 using short format
Motor 11 uses: 41540007e89c01000d0a (byte 0x9c)
Try similar patterns for motors 7 and 9
"""
import serial
import time
import sys
from collections import defaultdict

def extract_motor_id(msg_hex):
    """Extract motor ID from response - try multiple formats"""
    msg_clean = msg_hex.replace('0d0a', '').lower()
    
    if not msg_clean.startswith('4154'):
        return None
    
    # Standard response format: 41541000XXec...
    if msg_clean.startswith('41541000'):
        if len(msg_clean) >= 12:
            id_bytes = msg_clean[8:12]
            known_responses = {
                '0fec': 1,
                '1fec': 3,
                '77ec': 14,
                '3fec': 7,   # Try patterns for 7, 9, 11
                '4fec': 9,
                '9fec': 11,
            }
            if id_bytes in known_responses:
                return known_responses[id_bytes]
    
    # Check for other response formats
    # The response 415400005ff4084e4330209c23370d0d0a suggests other formats exist
    
    return None

def search_short_format_7_9_11(port='COM6', baudrate=921600):
    """
    Search for motors 7, 9, 11 using short format
    Short format: AT 00 07 e8 [byte] 01 00 0d 0a
    """
    
    motors_found = defaultdict(list)
    all_responses = []
    
    try:
        ser = serial.Serial(port, baudrate, timeout=3.0)
        print("="*70)
        print("Searching for Motors 7, 9, 11 - Short Format")
        print("="*70)
        print()
        print("Short format: AT 00 07 e8 [BYTE] 01 00 0d 0a")
        print("Motor 11: uses byte 0x9c")
        print("Testing likely bytes for motors 7 and 9...")
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
        
        # Target motors: 7, 9, 11
        # Motor 11 uses: 0x9c (we know this works individually)
        # Motor 7: try 0x3c, 0x7c, 0x5c (variations)
        # Motor 9: try 0x4c, 0x8c, 0x6c (variations)
        
        target_motors = {
            7: [0x3c, 0x7c, 0x5c, 0x2c, 0x6c, 0xbc],
            9: [0x4c, 0x8c, 0x6c, 0x5c, 0xac],
            11: [0x9c],  # Known to work
        }
        
        print("Testing short format for each motor:")
        print("-" * 70)
        
        for motor_id, test_bytes in sorted(target_motors.items()):
            print(f"\nMotor {motor_id}:")
            
            for byte_val in test_bytes:
                # Short format: AT 00 07 e8 [byte] 01 00 0d 0a
                cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val])
                cmd.extend([0x01, 0x00, 0x0d, 0x0a])
                
                print(f"  Testing byte 0x{byte_val:02x}...", end=' ')
                
                ser.reset_input_buffer()
                ser.write(bytes(cmd))
                time.sleep(0.8)  # Wait for response
                
                # Collect response
                response = bytearray()
                start = time.time()
                while time.time() - start < 2.0:
                    if ser.in_waiting > 0:
                        response.extend(ser.read(ser.in_waiting))
                    time.sleep(0.1)
                
                if len(response) > 4:
                    resp_hex = response.hex()
                    detected_id = extract_motor_id(resp_hex)
                    
                    if detected_id == motor_id:
                        motors_found[motor_id].append({
                            'byte': byte_val,
                            'response': resp_hex,
                            'format': 'short'
                        })
                        print(f"[FOUND!] Motor {motor_id}")
                        print(f"         Response: {resp_hex}")
                        break  # Found this motor, move to next
                    elif detected_id:
                        print(f"[Got Motor {detected_id} instead]")
                        print(f"         Response: {resp_hex[:60]}...")
                    elif len(resp_hex) > 10:
                        all_responses.append({
                            'motor': motor_id,
                            'byte': byte_val,
                            'response': resp_hex
                        })
                        print(f"[Response received]")
                        print(f"         Response: {resp_hex[:60]}...")
                    else:
                        print("[No response]")
                else:
                    print("[No response]")
                
                time.sleep(0.3)
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("SHORT FORMAT SEARCH RESULTS")
        print("="*70)
        print()
        
        if motors_found:
            print("MOTORS FOUND:")
            for motor_id in sorted(motors_found.keys()):
                for result in motors_found[motor_id]:
                    print(f"  Motor {motor_id}: Byte 0x{result['byte']:02x} (short format)")
                    print(f"    Response: {result['response'][:80]}...")
        else:
            print("No motors found with standard response format")
        
        if all_responses:
            print(f"\nRESPONSES RECEIVED (but unparsed - {len(all_responses)}):")
            for result in all_responses:
                print(f"  Motor {result['motor']}, Byte 0x{result['byte']:02x}:")
                print(f"    {result['response']}")
                print(f"    -> This might be Motor {result['motor']} responding in different format!")
        
        print()
        print("="*70)
        
        return motors_found, all_responses
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print()
    print("Searching for motors 7, 9, 11 using short format...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors, responses = search_short_format_7_9_11(port)

