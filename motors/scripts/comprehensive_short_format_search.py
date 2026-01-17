#!/usr/bin/env python3
"""
Comprehensive search for motors 7, 9, 11 using short format
Test a wider range of bytes around known patterns
"""
import serial
import time
import sys
from collections import defaultdict

def test_short_format_bytes(port='COM6', baudrate=921600):
    """
    Test short format: AT 00 07 e8 [BYTE] 01 00 0d 0a
    Motor 11 uses: 0x9c (we know this works individually)
    Motors 7, 9: Try ranges around 0x3c, 0x4c, 0x7c, 0x8c
    """
    
    responses_found = defaultdict(list)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=3.0)
        print("="*70)
        print("Comprehensive Short Format Search for Motors 7, 9, 11")
        print("="*70)
        print()
        print("Format: AT 00 07 e8 [BYTE] 01 00 0d 0a")
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        # Focus ranges:
        # - Around 0x3c (Motor 7 pattern): 0x2c-0x4c, 0x5c-0x7c
        # - Around 0x4c (Motor 9 pattern): 0x3c-0x5c, 0x6c-0x8c  
        # - Around 0x9c (Motor 11): 0x8c-0xac
        # Also test 0x5c since it gave us a response
        
        test_ranges = [
            (0x2c, 0x4c, "Around 0x3c (Motor 7 pattern)"),
            (0x4c, 0x6c, "Around 0x4c (Motor 9 pattern)"),
            (0x6c, 0x8c, "Around 0x7c/0x8c"),
            (0x8c, 0xac, "Around 0x9c (Motor 11 pattern)"),
            (0x5c, 0x5d, "Byte 0x5c (known response)"),
        ]
        
        all_responses = []
        
        for start_byte, end_byte, description in test_ranges:
            print(f"\n{description}:")
            print(f"Testing bytes 0x{start_byte:02x} to 0x{end_byte-1:02x}...")
            
            for byte_val in range(start_byte, end_byte):
                cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val])
                cmd.extend([0x01, 0x00, 0x0d, 0x0a])
                
                ser.reset_input_buffer()
                ser.write(bytes(cmd))
                time.sleep(0.6)
                
                response = bytearray()
                start = time.time()
                while time.time() - start < 1.5:
                    if ser.in_waiting > 0:
                        response.extend(ser.read(ser.in_waiting))
                    time.sleep(0.05)
                
                if len(response) > 4:
                    resp_hex = response.hex()
                    
                    # Check for different response formats
                    resp_clean = resp_hex.replace('0d0a', '').replace('0d', '').lower()
                    
                    # Format 1: 41541000XXec... (motors 1, 3, 14)
                    if resp_clean.startswith('41541000') and len(resp_clean) >= 12:
                        id_part = resp_clean[8:12]
                        print(f"  Byte 0x{byte_val:02x}: [FORMAT 1] Response: {resp_hex[:40]}...")
                        responses_found[byte_val].append({
                            'format': '41541000XXec',
                            'response': resp_hex,
                            'id_part': id_part
                        })
                    
                    # Format 2: 415400005ff4... (byte 0x5c response)
                    elif resp_clean.startswith('415400005ff4'):
                        print(f"  Byte 0x{byte_val:02x}: [FORMAT 2] Response: {resp_hex}")
                        responses_found[byte_val].append({
                            'format': '415400005ff4',
                            'response': resp_hex
                        })
                    
                    # Format 3: Other responses
                    else:
                        print(f"  Byte 0x{byte_val:02x}: [FORMAT 3] Response: {resp_hex[:50]}...")
                        all_responses.append({
                            'byte': byte_val,
                            'response': resp_hex
                        })
                
                time.sleep(0.2)
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("COMPREHENSIVE SHORT FORMAT SEARCH RESULTS")
        print("="*70)
        print()
        
        if responses_found:
            print("BYTES THAT GOT RESPONSES:")
            for byte_val in sorted(responses_found.keys()):
                for result in responses_found[byte_val]:
                    print(f"\n  Byte 0x{byte_val:02x}:")
                    print(f"    Format: {result['format']}")
                    print(f"    Response: {result['response']}")
                    if 'id_part' in result:
                        print(f"    ID Part: {result['id_part']}")
        else:
            print("No responses found with known formats")
        
        if all_responses:
            print(f"\n\nOTHER RESPONSES ({len(all_responses)}):")
            for result in all_responses:
                print(f"  Byte 0x{result['byte']:02x}: {result['response'][:60]}...")
        
        print()
        print("="*70)
        
        return responses_found, all_responses
        
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
    print("Comprehensive short format search for motors 7, 9, 11...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    responses, others = test_short_format_bytes(port)

