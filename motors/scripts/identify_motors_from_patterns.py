#!/usr/bin/env python3
"""
Identify which motors correspond to which response patterns
Analyze the response data to extract motor information
"""
import serial
import time
import sys

def analyze_pattern_responses(port='COM6', baudrate=921600):
    """Query each pattern and analyze the response data in detail"""
    
    patterns = {
        '0ff4': {
            'bytes': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
            'id_part': '0ff4',
            'hypothesis': 'Motor 1? (0x0c-0x0f range)'
        },
        '5ff4': {
            'bytes': [0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e, 0x5f],
            'id_part': '5ff4',
            'hypothesis': 'Motor 7 or 9? (contains 9c=Motor 11)'
        },
        '77f4': {
            'bytes': [0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77],
            'id_part': '77f4',
            'hypothesis': 'Motor 7 or 9? (contains 9c=Motor 11)'
        },
        '1ff4': {
            'bytes': [0x18, 0x1c],
            'id_part': '1ff4',
            'hypothesis': 'Motor 3? (includes 0x1c which is Motor 3)'
        },
    }
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Identifying Motors from Response Patterns")
        print("="*70)
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        results = {}
        
        for pattern_name, pattern_info in patterns.items():
            print(f"\n{'='*70}")
            print(f"Pattern: {pattern_name} ({pattern_info['hypothesis']})")
            print(f"{'='*70}")
            
            # Use first byte in range
            test_byte = pattern_info['bytes'][0]
            
            cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, test_byte])
            cmd.extend([0x01, 0x00, 0x0d, 0x0a])
            
            ser.reset_input_buffer()
            ser.write(bytes(cmd))
            time.sleep(1.0)
            
            response = bytearray()
            start_time = time.time()
            while time.time() - start_time < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 4:
                resp_hex = response.hex()
                resp_clean = resp_hex.replace('0d0a', '').replace('0d', '').lower()
                
                print(f"\nQuery byte: 0x{test_byte:02x}")
                print(f"Full response: {resp_hex}")
                print(f"\nResponse breakdown:")
                print(f"  Prefix:      {resp_clean[:8]}")
                print(f"  ID Part:     {resp_clean[8:12]} ({pattern_name})")
                print(f"  Next byte:   {resp_clean[12:14]}")
                print(f"  Data:        {resp_clean[14:]}")
                
                # Analyze data for motor encodings
                data = resp_clean[14:]
                motor_encodings = {
                    '0c': (1, 'Motor 1 (long format)'),
                    '1c': (3, 'Motor 3 (long format)'),
                    '3c': (7, 'Motor 7 (long format)'),
                    '4c': (9, 'Motor 9 (long format)'),
                    '7c': (7, 'Motor 7 (short format alt)'),
                    '9c': (11, 'Motor 11 (short format)'),
                    '74': (14, 'Motor 14 (long format)'),
                }
                
                found_motors = []
                for enc, (motor_id, desc) in motor_encodings.items():
                    if enc in data:
                        pos = data.find(enc)
                        found_motors.append((motor_id, enc, pos, desc))
                
                print(f"\nMotor encodings found in data:")
                if found_motors:
                    for motor_id, enc, pos, desc in found_motors:
                        print(f"  Position {pos}: '{enc}' = {desc}")
                        print(f"    -> This pattern indicates Motor {motor_id} is present/active")
                else:
                    print(f"  None found")
                
                # Try to decode which motor this pattern represents
                # Based on query byte range
                print(f"\nQuery byte analysis:")
                print(f"  Query bytes: {[hex(b) for b in pattern_info['bytes']]}")
                print(f"  Range: 0x{pattern_info['bytes'][0]:02x} - 0x{pattern_info['bytes'][-1]:02x}")
                
                # Try to map query byte to motor ID
                # If query byte encodes motor ID somehow
                for motor_id in [7, 9, 11]:
                    # Motor 7: long format uses 0x3c, short might use range around it
                    # Motor 9: long format uses 0x4c, short might use range around it
                    # Motor 11: short format uses 0x9c
                    
                    if motor_id == 7:
                        # 0x3c is Motor 7 long format
                        # Short format might be 0x3c + offset, or 0x7c range
                        if 0x70 <= test_byte <= 0x77:  # Pattern 77f4
                            print(f"  -> Byte 0x{test_byte:02x} might be Motor 7 (in 0x70-0x77 range)")
                    elif motor_id == 9:
                        # 0x4c is Motor 9 long format
                        if 0x58 <= test_byte <= 0x5f:  # Pattern 5ff4
                            print(f"  -> Byte 0x{test_byte:02x} might be Motor 9 (in 0x58-0x5f range)")
                    elif motor_id == 11:
                        # 0x9c is Motor 11 short format
                        # But we see 9c in the data, not in query
                        pass
                
                results[pattern_name] = {
                    'response': resp_hex,
                    'data': data,
                    'found_motors': found_motors,
                    'query_bytes': pattern_info['bytes']
                }
            
            time.sleep(0.5)
        
        ser.close()
        
        # Summary for motors 7, 9, 11
        print()
        print("="*70)
        print("SUMMARY FOR MOTORS 7, 9, 11")
        print("="*70)
        print()
        
        print("Pattern 5ff4 (bytes 0x58-0x5f):")
        if '5ff4' in results:
            print(f"  Contains Motor 11 encoding in data")
            print(f"  -> Could be Motor 9 responding (query byte range 0x58-0x5f)")
            print(f"  -> Try querying with bytes in this range when looking for Motor 9")
        
        print("\nPattern 77f4 (bytes 0x70-0x77):")
        if '77f4' in results:
            print(f"  Contains Motor 11 encoding in data")
            print(f"  -> Could be Motor 7 responding (query byte range 0x70-0x77)")
            print(f"  -> Try querying with bytes in this range when looking for Motor 7")
        
        print("\nMotor 11:")
        print(f"  Known: Uses byte 0x9c in short format individually")
        print(f"  When all connected: Appears in data of patterns 5ff4 and 77f4")
        print(f"  -> Motors 7, 9, 11 might share response format when all connected")
        
        print()
        print("="*70)
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    analyze_pattern_responses(port)

