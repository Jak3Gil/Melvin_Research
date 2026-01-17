#!/usr/bin/env python3
"""
Analyze the response format from byte 0x5c: 415400005ff4084e4330209c23370d0d0a
This might be the format motors 7, 9, 11 use when all motors are connected
"""
import serial
import time
import sys

def analyze_response_5c_format(resp_hex):
    """
    Analyze: 415400005ff4084e4330209c23370d0d0a
    Breakdown:
    - 4154 = AT
    - 00 = command/type
    - 00 = ? 
    - 5ff4 = might encode motor ID?
    - 084e4330209c2337 = data
    - 0d0d0a = CR CR LF
    """
    print(f"\nAnalyzing response: {resp_hex}")
    print(f"  Length: {len(resp_hex)} hex chars = {len(resp_hex)//2} bytes")
    
    # Extract parts
    parts = {
        'prefix': resp_hex[:4],      # 4154 = AT
        'byte1': resp_hex[4:6],      # 00
        'byte2': resp_hex[6:8],      # 00
        'id_part1': resp_hex[8:12],  # 5ff4
        'data': resp_hex[12:-6],     # Rest
        'ending': resp_hex[-6:],     # 0d0d0a
    }
    
    print(f"\nStructure:")
    for key, value in parts.items():
        print(f"  {key:10s}: {value}")
    
    # Try to decode motor ID from 5ff4
    id_val = int(parts['id_part1'], 16)
    print(f"\nID part (5ff4) = 0x{id_val:04x} = {id_val} decimal")
    
    # Check if data contains motor encodings
    if '9c' in parts['data']:
        pos = parts['data'].find('9c')
        print(f"\nFound '9c' (Motor 11 encoding) at position {pos} in data")
        print(f"  This might indicate Motor 11 is responding!")

def test_5c_response_more(port='COM6', baudrate=921600):
    """Test byte 0x5c more carefully to see response pattern"""
    
    try:
        ser = serial.Serial(port, baudrate, timeout=3.0)
        print("="*70)
        print("Analyzing Response from Byte 0x5c")
        print("="*70)
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        # Test byte 0x5c multiple times
        print("Testing byte 0x5c (short format) multiple times...")
        print("-" * 70)
        
        responses = []
        
        for i in range(3):
            print(f"\nTest {i+1}:")
            
            cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x5c])
            cmd.extend([0x01, 0x00, 0x0d, 0x0a])
            
            ser.reset_input_buffer()
            ser.write(bytes(cmd))
            time.sleep(1.0)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 0:
                resp_hex = response.hex()
                responses.append(resp_hex)
                print(f"  Response: {resp_hex}")
                
                if i == 0:
                    analyze_response_5c_format(resp_hex)
        
        ser.close()
        
        # Check consistency
        print()
        print("="*70)
        if len(responses) > 0:
            print(f"Consistent responses: {len(set(responses)) == 1}")
            if len(set(responses)) == 1:
                print("  -> Same response every time (reliable)")
            else:
                print("  -> Different responses (might be multiple motors)")
                for i, resp in enumerate(set(responses), 1):
                    print(f"    Variant {i}: {resp[:60]}...")
        
        print("="*70)
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    test_5c_response_more(port)

