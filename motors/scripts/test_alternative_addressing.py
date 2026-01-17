#!/usr/bin/env python3
"""
Test alternative addressing - maybe motors 7, 9, 11 use different CAN IDs
when all motors are connected vs individual
"""
import serial
import time
import sys
from collections import defaultdict

def test_all_possible_ids(port='COM6', baudrate=921600):
    """
    When motors are connected together, they might:
    - Use different base addresses
    - Respond to different ID encodings
    - Need broadcast queries
    """
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Testing Alternative Addressing for Motors 7, 9, 11")
        print("="*70)
        print("When all motors connected, they might use different IDs/formats")
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        # Test different byte encodings for motors 7, 9, 11
        # Based on pattern: 0c->1, 1c->3, so maybe:
        # 0c = (1-1)*16 + 12 = 12 = 0x0c
        # 1c = (3-1)*16 + 12 = 44 = 0x2c? No, it's 0x1c
        # Let's try different calculations
        
        print("Testing different byte encodings for Motor 7:")
        print("-" * 70)
        
        # Motor 7: We know 0x3c works individually, try variations
        test_bytes_7 = [0x3c, 0x2c, 0x4c, 0x5c, 0x6c, 0x7c]  # Around 0x3c
        
        for byte_val in test_bytes_7:
            print(f"\nTrying byte 0x{byte_val:02x} for Motor 7...")
            cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val])
            cmd.extend([0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00])
            cmd.extend([0x0d, 0x0a])
            
            ser.reset_input_buffer()
            ser.write(bytes(cmd))
            time.sleep(1.5)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 4:
                resp_hex = response.hex()
                print(f"  [OK] Got response: {resp_hex[:60]}...")
                
                # Check if it looks like motor 7
                if '3fec' in resp_hex or '37ec' in resp_hex:
                    print(f"  [SUCCESS] This might be Motor 7!")
                    break
            else:
                print(f"  [X] No response")
            
            time.sleep(0.5)
        
        print("\n" + "="*70)
        print("Testing Motor 9:")
        print("-" * 70)
        
        # Motor 9: We know 0x4c should work
        test_bytes_9 = [0x4c, 0x3c, 0x5c, 0x6c]
        
        for byte_val in test_bytes_9:
            print(f"\nTrying byte 0x{byte_val:02x} for Motor 9...")
            cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val])
            cmd.extend([0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00])
            cmd.extend([0x0d, 0x0a])
            
            ser.reset_input_buffer()
            ser.write(bytes(cmd))
            time.sleep(1.5)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 4:
                resp_hex = response.hex()
                print(f"  [OK] Got response: {resp_hex[:60]}...")
            else:
                print(f"  [X] No response")
            
            time.sleep(0.5)
        
        print("\n" + "="*70)
        print("Testing Motor 11 (short format):")
        print("-" * 70)
        
        # Motor 11: Uses short format, try variations
        test_bytes_11 = [0x9c, 0x8c, 0xac, 0xbc]
        
        for byte_val in test_bytes_11:
            print(f"\nTrying byte 0x{byte_val:02x} for Motor 11 (short format)...")
            cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val])
            cmd.extend([0x01, 0x00, 0x0d, 0x0a])
            
            ser.reset_input_buffer()
            ser.write(bytes(cmd))
            time.sleep(1.5)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 4:
                resp_hex = response.hex()
                print(f"  [OK] Got response: {resp_hex[:60]}...")
            else:
                print(f"  [X] No response")
            
            time.sleep(0.5)
        
        ser.close()
        
        print("\n" + "="*70)
        print("If none of these found motors 7, 9, 11:")
        print("  - They may need to be configured/activated first")
        print("  - They may respond to broadcast queries only")
        print("  - They may use a completely different addressing scheme")
        print("  - CAN bus configuration may be different for them")
        print("="*70)
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print()
    print("Testing alternative addressing...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    test_all_possible_ids(port)

