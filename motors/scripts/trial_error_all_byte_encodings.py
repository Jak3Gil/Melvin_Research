#!/usr/bin/env python3
"""
Trial and Error - Test all possible byte encodings to find motors 7, 9, 11
Systematically tries different byte values in the command format
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
            # Known patterns
            known_responses = {
                '0fec': 1,
                '1fec': 3,
                '77ec': 14,
            }
            if id_bytes in known_responses:
                return known_responses[id_bytes]
    
    return None

def test_all_byte_encodings(port='COM6', baudrate=921600):
    """
    Test all possible byte encodings (0x00 to 0xFF) to find motors 7, 9, 11
    """
    
    motors_found = defaultdict(list)
    all_responses = []
    
    try:
        ser = serial.Serial(port, baudrate, timeout=3.0)
        print("="*70)
        print("Trial and Error - Testing All Byte Encodings")
        print("="*70)
        print()
        print("Testing byte values in the command format:")
        print("Format: AT 20 07 e8 [BYTE] 08 00 c4 00 00 00 00 00")
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
        
        # Focus on likely ranges first
        # Motor 1: 0x0c, Motor 3: 0x1c, Motor 14: 0x74
        # So motors 7, 9, 11 might be: 0x3c, 0x4c, 0x9c or similar
        
        # Priority ranges to test first (most likely)
        priority_ranges = [
            (0x3c, 0x50),  # Around known values (3c, 4c) - likely for motors 7, 9
            (0x70, 0x80),  # Around motor 14 (74)
            (0x90, 0xa0),  # Around motor 11 (9c)
        ]
        
        tested = set()
        found_count = 0
        
        for start_byte, end_byte in priority_ranges:
            print(f"\nTesting priority range 0x{start_byte:02x} to 0x{end_byte:02x}:")
            print("-" * 70)
            
            for byte_val in range(start_byte, end_byte + 1):
                if byte_val in tested:
                    continue
                tested.add(byte_val)
                
                # Long format: AT 20 07 e8 [byte] 08 00 c4 00 00 00 00 00
                cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val])
                cmd.extend([0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00])
                cmd.extend([0x0d, 0x0a])
                
                # Skip known working ones (we'll test them briefly for comparison)
                is_known = byte_val in [0x0c, 0x1c, 0x74]
                
                # Test this byte value
                ser.reset_input_buffer()
                ser.write(bytes(cmd))
                time.sleep(0.5)  # Shorter delay for speed
                
                # Quick response check
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
                            'response': resp_hex
                        })
                        found_count += 1
                        print(f"  [FOUND] Byte 0x{byte_val:02x} -> Motor {detected_id}!")
                        print(f"          Response: {resp_hex[:60]}...")
                    elif len(resp_hex) > 20 and not is_known:
                        # Got response but couldn't parse (might be motors 7, 9, 11)
                        all_responses.append({
                            'byte': byte_val,
                            'response': resp_hex
                        })
                        print(f"  [?] Byte 0x{byte_val:02x} -> Unparsed response: {resp_hex[:50]}...")
                
                time.sleep(0.1)  # Small delay between tests
        
        # Now test remaining range if we haven't found motors 7, 9, 11
        if found_count < 3:
            print("\n" + "="*70)
            print("Testing remaining range 0x00 to 0xFF...")
            print("(Skipping already tested and known values)")
            print("-" * 70)
            
            for byte_val in range(0x00, 0x100):
                if byte_val in tested:
                    continue
                
                # Long format
                cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val])
                cmd.extend([0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00])
                cmd.extend([0x0d, 0x0a])
                
                ser.reset_input_buffer()
                ser.write(bytes(cmd))
                time.sleep(0.3)
                
                response = bytearray()
                start = time.time()
                while time.time() - start < 1.0:
                    if ser.in_waiting > 0:
                        response.extend(ser.read(ser.in_waiting))
                    time.sleep(0.05)
                
                if len(response) > 4:
                    resp_hex = response.hex()
                    detected_id = extract_motor_id(resp_hex)
                    
                    if detected_id:
                        motors_found[detected_id].append({
                            'byte': byte_val,
                            'response': resp_hex
                        })
                        print(f"  [FOUND] Byte 0x{byte_val:02x} -> Motor {detected_id}!")
                    elif len(resp_hex) > 20:
                        all_responses.append({
                            'byte': byte_val,
                            'response': resp_hex
                        })
                
                # Progress every 32 bytes
                if byte_val % 32 == 0:
                    print(f"    Progress: 0x{byte_val:02x}...")
                
                time.sleep(0.05)
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("TRIAL AND ERROR RESULTS")
        print("="*70)
        print()
        
        if motors_found:
            print("MOTORS FOUND:")
            for motor_id in sorted(motors_found.keys()):
                for result in motors_found[motor_id]:
                    print(f"  Motor {motor_id}: Byte encoding 0x{result['byte']:02x}")
                    print(f"    Response: {result['response'][:60]}...")
        else:
            print("No motors found with parsed responses")
        
        if all_responses:
            print(f"\nUNPARSED RESPONSES ({len(all_responses)}):")
            print("(These might be motors 7, 9, 11 in a different format)")
            for result in all_responses[:30]:  # Show first 30
                print(f"  Byte 0x{result['byte']:02x}: {result['response'][:50]}...")
        
        print()
        print("="*70)
        print(f"Total unique motors found: {len(motors_found)}")
        
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
    print("Testing all possible byte encodings to find motors 7, 9, 11...")
    print("This will test byte values systematically")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = test_all_byte_encodings(port)

