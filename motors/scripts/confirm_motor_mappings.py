#!/usr/bin/env python3
"""
Confirm the motor mappings we discovered:
- Motor 7: bytes 0x70-0x77 in short format (pattern 77f4)
- Motor 9: bytes 0x58-0x5f in short format (pattern 5ff4)
- Motor 11: byte 0x9c in short format

We'll test:
1. Query each motor with our discovered bytes
2. Cross-reference with known long format commands
3. Try to extract motor ID from response data
4. Compare response patterns
"""
import serial
import time
import sys

def send_command(ser, cmd_hex, description):
    """Send command and get response"""
    ser.reset_input_buffer()
    ser.write(bytes.fromhex(cmd_hex.replace(' ', '')))
    time.sleep(1.0)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < 2.0:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.1)
    
    return response.hex() if len(response) > 0 else None

def confirm_motor_mappings(port='COM6', baudrate=921600):
    """
    Confirm motor mappings by:
    1. Testing discovered short format bytes
    2. Cross-referencing with known long format commands
    3. Comparing response patterns
    """
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Confirming Motor Mappings (7, 9, 11)")
        print("="*70)
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
        
        # Test mappings
        test_cases = [
            # Motor 7
            {
                'motor': 7,
                'short_format_bytes': [0x70, 0x74, 0x77],  # Test a few in the range
                'long_format_byte': 0x3c,  # Known from Motor Studio
                'description': 'Motor 7'
            },
            # Motor 9
            {
                'motor': 9,
                'short_format_bytes': [0x58, 0x5c, 0x5f],  # Test a few in the range
                'long_format_byte': 0x4c,  # Known from Motor Studio
                'description': 'Motor 9'
            },
            # Motor 11
            {
                'motor': 11,
                'short_format_bytes': [0x9c],  # Known
                'long_format_byte': None,  # No long format known for Motor 11
                'description': 'Motor 11'
            },
            # Known working motors for comparison
            {
                'motor': 1,
                'short_format_bytes': None,  # We know long format works
                'long_format_byte': 0x0c,
                'description': 'Motor 1 (control)'
            },
            {
                'motor': 3,
                'short_format_bytes': None,
                'long_format_byte': 0x1c,
                'description': 'Motor 3 (control)'
            },
            {
                'motor': 14,
                'short_format_bytes': None,
                'long_format_byte': 0x74,
                'description': 'Motor 14 (control)'
            },
        ]
        
        results = {}
        
        for test_case in test_cases:
            motor_id = test_case['motor']
            desc = test_case['description']
            
            print(f"\n{'='*70}")
            print(f"{desc} (Motor {motor_id})")
            print(f"{'='*70}")
            
            results[motor_id] = {
                'short_format': {},
                'long_format': {}
            }
            
            # Test short format if applicable
            if test_case['short_format_bytes']:
                print(f"\nShort Format Tests:")
                for byte_val in test_case['short_format_bytes']:
                    cmd_hex = f"41540007e8{byte_val:02x}01000d0a"
                    print(f"  Byte 0x{byte_val:02x}: ", end='', flush=True)
                    
                    resp = send_command(ser, cmd_hex, f"Motor {motor_id} short format 0x{byte_val:02x}")
                    
                    if resp:
                        resp_clean = resp.replace('0d0a', '').replace('0d', '').lower()
                        print(f"[RESPONSE] {resp[:50]}...")
                        
                        # Check response format
                        if resp_clean.startswith('41541000'):
                            print(f"    -> Format: 41541000XXec (standard motor response)")
                            results[motor_id]['short_format'][byte_val] = {'format': 'standard', 'response': resp}
                        elif resp_clean.startswith('41540000'):
                            id_part = resp_clean[8:12] if len(resp_clean) >= 12 else 'unknown'
                            print(f"    -> Format: 41540000{id_part}... (new format)")
                            results[motor_id]['short_format'][byte_val] = {'format': 'new', 'response': resp, 'id_part': id_part}
                        else:
                            print(f"    -> Format: Unknown")
                            results[motor_id]['short_format'][byte_val] = {'format': 'unknown', 'response': resp}
                    else:
                        print("[NO RESPONSE]")
                    
                    time.sleep(0.3)
            
            # Test long format if applicable
            if test_case['long_format_byte']:
                print(f"\nLong Format Test:")
                byte_val = test_case['long_format_byte']
                cmd_hex = f"41542007e8{byte_val:02x}0800c40000000000000d0a"
                print(f"  Byte 0x{byte_val:02x}: ", end='', flush=True)
                
                resp = send_command(ser, cmd_hex, f"Motor {motor_id} long format 0x{byte_val:02x}")
                
                if resp:
                    resp_clean = resp.replace('0d0a', '').replace('0d', '').lower()
                    print(f"[RESPONSE] {resp[:50]}...")
                    
                    if resp_clean.startswith('41541000'):
                        print(f"    -> Format: 41541000XXec (standard motor response)")
                        results[motor_id]['long_format'][byte_val] = {'format': 'standard', 'response': resp}
                    else:
                        print(f"    -> Format: {resp_clean[:20]}...")
                        results[motor_id]['long_format'][byte_val] = {'format': 'other', 'response': resp}
                else:
                    print("[NO RESPONSE]")
                
                time.sleep(0.3)
        
        ser.close()
        
        # Analysis and confirmation
        print()
        print("="*70)
        print("CONFIRMATION ANALYSIS")
        print("="*70)
        print()
        
        print("Motor 7:")
        if 7 in results:
            if results[7]['short_format']:
                print("  Short format responses:")
                for byte_val, data in results[7]['short_format'].items():
                    print(f"    Byte 0x{byte_val:02x}: {data['format']} - {data.get('id_part', 'N/A')}")
                    if data['format'] == 'new' and data.get('id_part') == '77f4':
                        print(f"      -> CONFIRMED: Pattern 77f4 matches Motor 7")
            
            if results[7]['long_format']:
                print("  Long format (0x3c):")
                for byte_val, data in results[7]['long_format'].items():
                    print(f"    Format: {data['format']}")
                    if data['format'] == 'standard':
                        print(f"      -> Motor 7 responds in standard format with long format command")
        
        print("\nMotor 9:")
        if 9 in results:
            if results[9]['short_format']:
                print("  Short format responses:")
                for byte_val, data in results[9]['short_format'].items():
                    print(f"    Byte 0x{byte_val:02x}: {data['format']} - {data.get('id_part', 'N/A')}")
                    if data['format'] == 'new' and data.get('id_part') == '5ff4':
                        print(f"      -> CONFIRMED: Pattern 5ff4 matches Motor 9")
            
            if results[9]['long_format']:
                print("  Long format (0x4c):")
                for byte_val, data in results[9]['long_format'].items():
                    print(f"    Format: {data['format']}")
                    if data['format'] == 'standard':
                        print(f"      -> Motor 9 responds in standard format with long format command")
        
        print("\nMotor 11:")
        if 11 in results:
            if results[11]['short_format']:
                print("  Short format responses:")
                for byte_val, data in results[11]['short_format'].items():
                    print(f"    Byte 0x{byte_val:02x}: {data['format']}")
                    if data['format'] == 'standard':
                        print(f"      -> Motor 11 responds in standard format")
                    elif data['format'] == 'new':
                        print(f"      -> Motor 11 responds in new format")
        
        print("\n" + "="*70)
        print("CONCLUSION:")
        print("="*70)
        
        # Check if patterns match
        motor_7_confirmed = False
        motor_9_confirmed = False
        motor_11_confirmed = False
        
        if 7 in results:
            for byte_val, data in results[7]['short_format'].items():
                if data.get('id_part') == '77f4':
                    motor_7_confirmed = True
                    print(f"[OK] Motor 7: CONFIRMED - Bytes 0x70-0x77 (pattern 77f4) work")
                    break
        
        if 9 in results:
            for byte_val, data in results[9]['short_format'].items():
                if data.get('id_part') == '5ff4':
                    motor_9_confirmed = True
                    print(f"[OK] Motor 9: CONFIRMED - Bytes 0x58-0x5f (pattern 5ff4) work")
                    break
        
        if 11 in results:
            for byte_val, data in results[11]['short_format'].items():
                if data['format'] in ['standard', 'new']:
                    motor_11_confirmed = True
                    print(f"[OK] Motor 11: CONFIRMED - Byte 0x9c works")
                    break
        
        if not motor_7_confirmed:
            print(f"[?] Motor 7: Needs verification")
        if not motor_9_confirmed:
            print(f"[?] Motor 9: Needs verification")
        if not motor_11_confirmed:
            print(f"[?] Motor 11: Needs verification (may need different timing/format)")
        
        print()
        print("="*70)
        
        return results
        
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
    print("Confirming motor mappings for Motors 7, 9, 11...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    results = confirm_motor_mappings(port)

