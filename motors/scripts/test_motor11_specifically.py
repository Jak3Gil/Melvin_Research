#!/usr/bin/env python3
"""
Test Motor 11 specifically with byte 0x9c
It might need different timing or format when all motors are connected
"""
import serial
import time
import sys

def test_motor11_variations(port='COM6', baudrate=921600):
    """Test Motor 11 with various formats and timings"""
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Testing Motor 11 (Byte 0x9c) - Various Formats")
        print("="*70)
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        # Test variations
        tests = [
            {
                'name': 'Short format (original)',
                'cmd': '41540007e89c01000d0a',
                'delay': 1.0
            },
            {
                'name': 'Short format with longer delay',
                'cmd': '41540007e89c01000d0a',
                'delay': 2.0
            },
            {
                'name': 'Try querying after Motor 7',
                'cmd': '41540007e89c01000d0a',
                'delay': 1.0,
                'pre_query': '41540007e87401000d0a'  # Query Motor 7 first
            },
            {
                'name': 'Try querying after Motor 9',
                'cmd': '41540007e89c01000d0a',
                'delay': 1.0,
                'pre_query': '41540007e85c01000d0a'  # Query Motor 9 first
            },
        ]
        
        for i, test in enumerate(tests, 1):
            print(f"\nTest {i}: {test['name']}")
            print("-" * 70)
            
            if 'pre_query' in test:
                print(f"  Pre-query...", end='', flush=True)
                ser.reset_input_buffer()
                ser.write(bytes.fromhex(test['pre_query']))
                time.sleep(0.5)
                ser.read(500)
                print(" [done]")
            
            print(f"  Sending: {test['cmd']}")
            ser.reset_input_buffer()
            ser.write(bytes.fromhex(test['cmd']))
            time.sleep(test['delay'])
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 4:
                resp_hex = response.hex()
                resp_clean = resp_hex.replace('0d0a', '').replace('0d', '').lower()
                print(f"  [RESPONSE] {resp_hex}")
                
                if resp_clean.startswith('41541000'):
                    print(f"    -> Standard format (41541000XXec)")
                elif resp_clean.startswith('41540000'):
                    print(f"    -> New format (41540000XXXX)")
                    if len(resp_clean) >= 12:
                        print(f"    -> ID Part: {resp_clean[8:12]}")
                else:
                    print(f"    -> Unknown format")
            else:
                print(f"  [NO RESPONSE]")
            
            time.sleep(0.5)
        
        ser.close()
        
        print()
        print("="*70)
        print("Motor 11 Summary:")
        print("  - Known to work individually with byte 0x9c")
        print("  - When all motors connected, may need:")
        print("    * Different timing")
        print("    * Different sequence (query after other motors)")
        print("    * May respond but in different format")
        print("="*70)
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    test_motor11_variations(port)

