#!/usr/bin/env python3
"""
Map ALL short format byte responses to see which bytes trigger which motors
This will help identify which bytes correspond to motors 7, 9, 11
"""
import serial
import time
import sys
from collections import defaultdict

def map_all_short_responses(port='COM6', baudrate=921600):
    """
    Test ALL bytes 0x00-0xFF in short format and map responses
    Format: AT 00 07 e8 [BYTE] 01 00 0d 0a
    """
    
    response_map = defaultdict(list)
    unique_responses = {}
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Mapping ALL Short Format Responses")
        print("="*70)
        print()
        print("This will test all 256 bytes...")
        print("Format: AT 00 07 e8 [BYTE] 01 00 0d 0a")
        print()
        
        # Initialize
        print("Initializing...")
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        print("  [OK]")
        print()
        
        print("Testing bytes... (this will take a while)")
        print()
        
        # Test all bytes, but prioritize known ranges
        # First test known ranges quickly, then do full scan
        priority_ranges = [
            (0x00, 0x10, "0x00-0x0f"),
            (0x2c, 0x50, "0x2c-0x4f (Motor 7/9 ranges)"),
            (0x58, 0x60, "0x58-0x5f (known responses)"),
            (0x70, 0x80, "0x70-0x7f (known responses)"),
            (0x8c, 0xa0, "0x8c-0x9f (Motor 11 range)"),
        ]
        
        # Full scan after priority
        full_scan = True
        
        tested_count = 0
        response_count = 0
        
        # Priority ranges first
        for start, end, desc in priority_ranges:
            print(f"Priority range {desc}: ", end='', flush=True)
            
            for byte_val in range(start, end):
                cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val])
                cmd.extend([0x01, 0x00, 0x0d, 0x0a])
                
                ser.reset_input_buffer()
                ser.write(bytes(cmd))
                time.sleep(0.4)
                
                response = bytearray()
                start_time = time.time()
                while time.time() - start_time < 1.2:
                    if ser.in_waiting > 0:
                        response.extend(ser.read(ser.in_waiting))
                    time.sleep(0.05)
                
                tested_count += 1
                
                if len(response) > 4:
                    resp_hex = response.hex()
                    resp_clean = resp_hex.replace('0d0a', '').replace('0d', '').lower()
                    
                    # Group by response signature
                    if resp_clean.startswith('41541000') and len(resp_clean) >= 12:
                        sig = resp_clean[:12]  # 41541000XXec
                    elif resp_clean.startswith('41540000') and len(resp_clean) >= 12:
                        sig = resp_clean[:12]  # 41540000XXXX
                    else:
                        sig = resp_hex[:20]  # First 10 bytes as signature
                    
                    if sig not in unique_responses:
                        unique_responses[sig] = resp_hex
                        response_map[sig] = []
                    
                    response_map[sig].append(byte_val)
                    response_count += 1
                
                time.sleep(0.15)
            
            print(f"[{response_count} responses found so far]")
        
        # Quick full scan (every 4th byte to save time)
        if full_scan:
            print(f"\nQuick full scan (every 4th byte): ", end='', flush=True)
            skipped_ranges = set()
            for start, end, _ in priority_ranges:
                skipped_ranges.update(range(start, end))
            
            for byte_val in range(0, 256, 4):
                if byte_val in skipped_ranges:
                    continue
                
                cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val])
                cmd.extend([0x01, 0x00, 0x0d, 0x0a])
                
                ser.reset_input_buffer()
                ser.write(bytes(cmd))
                time.sleep(0.3)
                
                response = bytearray()
                start_time = time.time()
                while time.time() - start_time < 1.0:
                    if ser.in_waiting > 0:
                        response.extend(ser.read(ser.in_waiting))
                    time.sleep(0.05)
                
                tested_count += 1
                
                if len(response) > 4:
                    resp_hex = response.hex()
                    resp_clean = resp_hex.replace('0d0a', '').replace('0d', '').lower()
                    
                    if resp_clean.startswith('41541000') and len(resp_clean) >= 12:
                        sig = resp_clean[:12]
                    elif resp_clean.startswith('41540000') and len(resp_clean) >= 12:
                        sig = resp_clean[:12]
                    else:
                        sig = resp_hex[:20]
                    
                    if sig not in unique_responses:
                        unique_responses[sig] = resp_hex
                        response_map[sig] = []
                    
                    response_map[sig].append(byte_val)
                    response_count += 1
                
                time.sleep(0.1)
            
            print(f"[{response_count} responses found]")
        
        ser.close()
        
        # Results
        print()
        print("="*70)
        print("SHORT FORMAT RESPONSE MAP")
        print("="*70)
        print()
        print(f"Total bytes tested: {tested_count}")
        print(f"Unique response patterns: {len(unique_responses)}")
        print(f"Total responses: {response_count}")
        print()
        
        print("RESPONSE PATTERNS:")
        print("-" * 70)
        
        for sig, bytes_list in sorted(response_map.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\nPattern: {sig}")
            print(f"  Bytes ({len(bytes_list)}): {bytes_list}")
            print(f"  Example response: {unique_responses[sig]}")
            
            # Try to identify motor
            resp = unique_responses[sig]
            resp_clean = resp.replace('0d0a', '').replace('0d', '').lower()
            
            # Check for motor encodings in response
            motor_hints = []
            if '0fec' in resp_clean or '0c' in resp_clean[:20]:
                motor_hints.append('1')
            if '1fec' in resp_clean or '1c' in resp_clean[:20]:
                motor_hints.append('3')
            if '3fec' in resp_clean or '3c' in resp_clean[:20]:
                motor_hints.append('7')
            if '4fec' in resp_clean or '4c' in resp_clean[:20]:
                motor_hints.append('9')
            if '9fec' in resp_clean or '9c' in resp_clean[:20]:
                motor_hints.append('11')
            if '77ec' in resp_clean or '74' in resp_clean[:20]:
                motor_hints.append('14')
            
            if motor_hints:
                print(f"  -> Possibly Motor(s): {', '.join(motor_hints)}")
        
        print()
        print("="*70)
        
        return response_map, unique_responses
        
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
    print("Mapping all short format responses...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    map_all, unique = map_all_short_responses(port)

