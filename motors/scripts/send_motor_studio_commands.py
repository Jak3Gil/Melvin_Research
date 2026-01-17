#!/usr/bin/env python3
"""
Send Motor Studio-style commands to missing motors (1, 2, 4, 8, 9)
Mimics Motor Studio's AT command format: 41540007ebc401000d0a
"""
import serial
import time
import sys

# Motors that Motor Studio can't see
MISSING_MOTORS = [1, 2, 4, 8, 9]
# Motors that Motor Studio CAN see (for testing format)
WORKING_MOTORS = [5, 6, 7, 10, 11, 12, 13, 14]

def create_motor_studio_command(motor_id, enable=1):
    """
    Create Motor Studio-style AT command
    Format: AT + 00 07 + CAN_ID + enable + 00 + CRLF
    Based on: 41540007ebc401000d0a
    """
    # Motor Studio format: AT + 00 07 + CAN_ID_bytes + enable + 00 + CRLF
    # CAN ID might be encoded as: 0x07 + (motor_id << 8) or similar
    # Let's try different encodings
    
    packet = bytearray()
    packet.extend([0x41, 0x54])  # "AT"
    packet.extend([0x00, 0x07])  # Command type/length
    
    # Try different CAN ID encodings
    # Option 1: 0x07 + motor_id in high byte
    can_id_byte1 = 0x07
    can_id_byte2 = motor_id & 0xFF
    
    # Option 2: motor_id in both bytes (little endian)
    # can_id_byte1 = motor_id & 0xFF
    # can_id_byte2 = (motor_id >> 8) & 0xFF
    
    # Option 3: Direct motor ID
    # can_id_byte1 = motor_id & 0xFF
    # can_id_byte2 = 0x00
    
    packet.extend([can_id_byte1, can_id_byte2])
    packet.extend([enable, 0x00])  # Enable flag + parameter
    packet.extend([0x0d, 0x0a])   # CRLF
    
    return packet

def try_motor_studio_scan(port, baudrate=921600):
    """Try Motor Studio-style scanning for missing motors"""
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print(f"[OK] Connected to {port} at {baudrate} baud\n")
        
        found_motors = []
        
        for motor_id in MISSING_MOTORS:
            print(f"Testing Motor {motor_id} with Motor Studio format...")
            
            # Try different CAN ID encodings
            # Based on 41540007ebc401000d0a, eb c4 might be CANopen node ID encoding
            encodings = [
                ("0x07 + ID", 0x07, motor_id),
                ("ID + 0x00", motor_id, 0x00),
                ("ID little-endian", motor_id & 0xFF, (motor_id >> 8) & 0xFF),
                ("0x07eb format", 0x07, 0xeb),  # Like the example
                ("Direct ID", motor_id, 0x00),
                ("ID swapped", 0x00, motor_id),
                # CANopen node ID format: 0x600 + node_id (standard CANopen)
                ("CANopen 0x600+ID", (0x600 + motor_id) >> 8, (0x600 + motor_id) & 0xFF),
                ("CANopen 0x700+ID", (0x700 + motor_id) >> 8, (0x700 + motor_id) & 0xFF),
                # Try the exact format from example: eb c4
                ("ebc4 pattern", 0xeb, 0xc4),
                # Try variations with motor ID
                ("0xeb + ID", 0xeb, motor_id),
                ("ID + 0xc4", motor_id, 0xc4),
            ]
            
            for encoding_name, byte1, byte2 in encodings:
                packet = bytearray()
                packet.extend([0x41, 0x54])  # "AT"
                packet.extend([0x00, 0x07])  # Command type
                packet.extend([byte1, byte2])  # CAN ID bytes
                packet.extend([0x01, 0x00])  # Enable + param
                packet.extend([0x0d, 0x0a])  # CRLF
                
                print(f"  Trying {encoding_name}: {packet.hex()}")
                ser.write(packet)
                time.sleep(0.3)
                
                response = ser.read(100)
                if response and len(response) > 0:
                    print(f"    [OK] RESPONSE! {len(response)} bytes: {response.hex()[:40]}...")
                    found_motors.append((motor_id, encoding_name, response))
                    break
                else:
                    print(f"    [X] No response")
            
            print()
            time.sleep(0.2)
        
        ser.close()
        
        if found_motors:
            print("\n" + "="*50)
            print("FOUND MOTORS:")
            print("="*50)
            for motor_id, encoding, response in found_motors:
                print(f"Motor {motor_id} - {encoding}")
                print(f"  Response: {response.hex()[:60]}...")
        else:
            print("\n[X] No motors responded to Motor Studio format")
            print("\nTry manually entering these CAN IDs in Motor Studio:")
            for motor_id in MISSING_MOTORS:
                print(f"  - CAN ID {motor_id}")
        
        return found_motors
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        print("\nNOTE: COM3 might be in use by Motor Studio.")
        print("Please close Motor Studio and try again, or use a different COM port.")
        return []

def send_specific_command(port, motor_id, can_id_bytes, enable=1):
    """Send specific Motor Studio command"""
    try:
        ser = serial.Serial(port, 921600, timeout=1.0)
        
        packet = bytearray()
        packet.extend([0x41, 0x54])  # "AT"
        packet.extend([0x00, 0x07])  # Command type
        packet.extend(can_id_bytes)  # CAN ID bytes
        packet.extend([enable, 0x00])  # Enable + param
        packet.extend([0x0d, 0x0a])  # CRLF
        
        print(f"Sending to Motor {motor_id}: {packet.hex()}")
        ser.write(packet)
        time.sleep(0.3)
        
        response = ser.read(100)
        ser.close()
        
        if response:
            print(f"[OK] Response: {response.hex()}")
            return response
        else:
            print("[X] No response")
            return None
            
    except Exception as e:
        print(f"[X] Error: {e}")
        return None

def test_l91_protocol(port, motor_id, baudrate=921600):
    """Test L91 protocol format (0xAA 0x55) that Python scripts use"""
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        
        # L91 protocol format from instant_test.py
        import struct
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.append(sum(packet[2:]) & 0xFF)
        
        print(f"  L91 format: {packet.hex()}")
        ser.write(packet)
        time.sleep(0.3)
        
        response = ser.read(100)
        ser.close()
        
        if response:
            print(f"  [OK] L91 response: {response.hex()[:40]}...")
            return True
        else:
            print(f"  [X] No L91 response")
            return False
            
    except Exception as e:
        print(f"  [X] L91 error: {e}")
        return False

def test_working_motors(port, baudrate=921600):
    """Test working motors to understand the correct format"""
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print(f"\n[TEST] Testing working motors to find correct format...")
        print(f"Testing motors: {WORKING_MOTORS}\n")
        
        # Try a simple format on working motor 5
        test_id = 5
        print(f"Testing Motor {test_id} (known working)...")
        
        # Try the most likely format: direct ID
        packet = bytearray()
        packet.extend([0x41, 0x54])  # "AT"
        packet.extend([0x00, 0x07])  # Command type
        packet.extend([test_id, 0x00])  # CAN ID
        packet.extend([0x01, 0x00])  # Enable + param
        packet.extend([0x0d, 0x0a])  # CRLF
        
        print(f"  AT format: {packet.hex()}")
        ser.write(packet)
        time.sleep(0.3)
        
        response = ser.read(100)
        if response:
            print(f"  [OK] AT response: {response.hex()[:40]}...")
        else:
            print(f"  [X] No AT response")
        
        ser.close()
        
        # Also try L91 protocol
        print(f"\n  Also trying L91 protocol format...")
        test_l91_protocol(port, test_id, baudrate)
        
        return True
            
    except Exception as e:
        print(f"[X] Error testing: {e}")
        return False

if __name__ == "__main__":
    # Default to COM3 on Windows
    port = 'COM3'
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print("="*50)
    print("Motor Studio Command Sender")
    print("="*50)
    print(f"Target motors: {MISSING_MOTORS}")
    print(f"Port: {port}")
    print("="*50)
    print()
    
    # First, test if we can communicate with a working motor
    test_working_motors(port)
    print()
    
    # Try scanning with Motor Studio format
    found = try_motor_studio_scan(port)
    
    if found:
        print("\n[OK] Success! These motors responded to Motor Studio format")
        print("\nYou can now try entering these CAN IDs in Motor Studio:")
        for motor_id, encoding, _ in found:
            print(f"  Motor {motor_id} - {encoding}")

