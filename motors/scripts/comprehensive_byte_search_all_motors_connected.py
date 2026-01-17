#!/usr/bin/env python3
"""
Comprehensive byte search when ALL motors connected
Motor Studio also can't detect Motors 7 and 9, so we need to find
what byte encodings they use when all 6 motors are present
"""
import serial
import time

def send_and_get_response(ser, cmd, timeout=0.5):
    """Send command and get response"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.03)
    
    return response.hex() if len(response) > 0 else None

port = 'COM6'
print("="*70)
print("Comprehensive Byte Search - All Motors Connected")
print("="*70)
print()
print("Motor Studio also can't detect Motors 7 and 9 with all motors!")
print("Testing ALL byte combinations to find what they respond to...")
print()
print("CONNECT ALL 6 MOTORS BEFORE RUNNING!")
print()
print("Starting in 3 seconds...")
time.sleep(3)
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Known working bytes (to identify patterns)
    # Motor 1: 0x08-0x0f (pattern 0ff4)
    # Motor 3: 0x18-0x1f (pattern 1ff4)
    # Motor 11: 0x58-0x5f (pattern 5ff4)
    # Motor 14: 0x70-0x77 (pattern 77f4)
    
    # Motors 7 and 9 individual bytes:
    # Motor 7 individual: 0x3c, 0x7c, 0xbc
    # Motor 9 individual: 0x4c, 0xdc, 0x8c
    
    responding_bytes = []
    
    print("="*70)
    print("SCAN 1: Standard Format (0x00) - All Bytes")
    print("="*70)
    print()
    print("Testing all 256 bytes with standard format...")
    print("Looking for new response patterns (not 0ff4, 1ff4, 5ff4, 77f4)...")
    print()
    
    new_patterns_found = []
    
    # Test all bytes systematically
    for byte_val in range(256):
        if (byte_val % 32) == 0:
            print(f"  Testing bytes 0x{byte_val:02x}-0x{min(byte_val+31, 255):02x}...", end='\r')
        
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.4)
        
        if resp:
            resp_clean = resp.lower().replace('0d0a', '').replace('0d', '')
            
            # Check if it's a known pattern or new
            known_patterns = ['0ff4', '1ff4', '5ff4', '77f4']
            is_known = any(pattern in resp_clean for pattern in known_patterns)
            
            if not is_known:
                # New pattern!
                pattern = resp_clean[:8] if len(resp_clean) >= 8 else resp_clean
                new_patterns_found.append({
                    'byte': byte_val,
                    'response': resp,
                    'pattern': pattern
                })
                print(f"\n  NEW PATTERN! Byte 0x{byte_val:02x}: {pattern}...")
            
            responding_bytes.append({
                'byte': byte_val,
                'response': resp,
                'format': 'standard'
            })
        
        time.sleep(0.05)  # Short delay
    
    print()  # New line after progress indicator
    print()
    
    if new_patterns_found:
        print(f"Found {len(new_patterns_found)} new response patterns!")
        print()
        for item in new_patterns_found:
            print(f"Byte 0x{item['byte']:02x}: Pattern {item['pattern']}")
            print(f"  Response: {item['response'][:80]}...")
            print()
    else:
        print("No new patterns found with standard format.")
    
    print()
    
    # Scan 2: Extended format (0x20)
    print("="*70)
    print("SCAN 2: Extended Format (0x20) - Key Byte Ranges")
    print("="*70)
    print()
    print("Testing extended format for likely Motor 7/9 byte ranges...")
    print()
    
    # Focus on ranges around known individual bytes
    test_ranges = [
        (0x30, 0x50, "Around Motor 7 (0x3c, 0x4c)"),
        (0x70, 0x90, "Around Motor 14/Motor 7 variations"),
        (0xd0, 0xf0, "Around Motor 9 (0xdc)"),
        (0xb0, 0xd0, "Motor 7/9 variations"),
    ]
    
    extended_new_patterns = []
    
    for start, end, desc in test_ranges:
        print(f"Range {desc} (0x{start:02x}-0x{end:02x}):")
        for byte_val in range(start, min(end+1, 256)):
            cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                            0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
            resp = send_and_get_response(ser, cmd, timeout=0.4)
            
            if resp:
                resp_clean = resp.lower().replace('0d0a', '').replace('0d', '')
                
                # Check for new patterns
                known_patterns = ['0fec', '1fec', '5fec', '77ec', '3fec', '4fec']
                is_known = any(pattern in resp_clean for pattern in known_patterns)
                
                if not is_known and len(resp_clean) > 8:
                    pattern = resp_clean[:8]
                    extended_new_patterns.append({
                        'byte': byte_val,
                        'response': resp,
                        'pattern': pattern,
                        'format': 'extended'
                    })
                    print(f"  Byte 0x{byte_val:02x}: NEW - {pattern}...")
                elif resp:
                    print(f"  Byte 0x{byte_val:02x}: {resp_clean[:20]}...")
            
            time.sleep(0.05)
        
        print()
    
    if extended_new_patterns:
        print(f"Found {len(extended_new_patterns)} new extended format patterns!")
        print()
    
    ser.close()
    
    print("="*70)
    print("SCAN COMPLETE")
    print("="*70)
    print()
    print(f"Total bytes with responses: {len(responding_bytes)}")
    print(f"New patterns found (standard): {len(new_patterns_found)}")
    print(f"New patterns found (extended): {len(extended_new_patterns)}")
    print()
    
    if new_patterns_found or extended_new_patterns:
        print("NEW PATTERNS DISCOVERED - These might be Motors 7 and 9!")
        print("Check the bytes and responses above.")
        print("If Motors 7 or 9 moved when testing those bytes, that's the answer!")
    else:
        print("No new patterns found.")
        print("Motors 7 and 9 may not be responding at all when all motors connected.")
        print("Possible causes:")
        print("  - Hardware fault ('Bus voltage too low')")
        print("  - Different communication method needed")
        print("  - Power/voltage issue preventing response")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

