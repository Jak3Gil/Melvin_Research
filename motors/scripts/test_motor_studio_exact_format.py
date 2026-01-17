#!/usr/bin/env python3
"""
Test Motor Studio's exact format:
1. AT+AT (initialization)
2. AT + 00 07 + [4 bytes from Motor Studio] + 01 00 + CRLF
"""
import serial
import struct
import time
import sys

def initialize_adapter(ser):
    """Send AT+AT initialization command"""
    cmd = bytes.fromhex("41542b41540d0a")  # AT+AT + CRLF
    print("Step 1: Sending AT+AT (initialization)...")
    ser.write(cmd)
    time.sleep(0.5)
    response = ser.read(200)
    if response:
        print(f"  [OK] Response: {response.hex()[:60]}...")
    print()
    return response

def send_motor_studio_command_exact(ser, four_bytes_hex):
    """
    Send Motor Studio command with exact 4-byte format
    Format: AT + 00 07 + [4 bytes] + 01 00 + CRLF
    """
    four_bytes = bytes.fromhex(four_bytes_hex.replace(' ', ''))
    
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.extend([0x00, 0x07])  # Command type/length
    packet.extend(four_bytes)  # 4 bytes from Motor Studio
    packet.extend([0x01, 0x00])  # Enable + parameter
    packet.extend([0x0d, 0x0a])  # CRLF
    
    print(f"  Sending: {packet.hex()}")
    ser.write(packet)
    time.sleep(0.4)
    
    response = ser.read(200)
    return response

def test_known_motor11(port, baudrate=921600):
    """Test the known Motor 11 format"""
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*60)
        print("Testing Motor Studio Exact Format")
        print("="*60)
        print(f"Port: {port} at {baudrate} baud")
        print("="*60)
        print()
        
        # Initialize
        initialize_adapter(ser)
        
        # Test Motor 11 (known format)
        print("Testing Motor 11 (known format: e8 9c 01 00):")
        response = send_motor_studio_command_exact(ser, "e89c0100")
        if response and len(response) > 0:
            print(f"  [OK] Motor 11 RESPONDED! ({len(response)} bytes)")
            print(f"       Response: {response.hex()[:80]}...")
            try:
                ascii_str = response.decode('ascii', errors='ignore')
                if ascii_str.strip():
                    print(f"       ASCII: {ascii_str[:60]}")
            except:
                pass
        else:
            print("  [X] Motor 11: No response")
        print()
        
        ser.close()
        return response
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    test_known_motor11(port)
    
    print("\n" + "="*60)
    print("NOTE: We need more examples from Motor Studio!")
    print("="*60)
    print("To find the pattern, we need to know:")
    print("  - What 4 bytes Motor Studio uses for Motor 5")
    print("  - What 4 bytes Motor Studio uses for Motor 6")
    print("  - What 4 bytes Motor Studio uses for Motor 7")
    print("\nThen we can figure out how to calculate the 4 bytes")
    print("for motors 1, 2, 4, 8, 9")
    print("="*60)

