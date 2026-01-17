#!/usr/bin/env python3
"""
Test Motor Studio command format on COM6
Format: AT+AT (init), then AT + 00 07 + [4 bytes CAN ID] + 01 00 + CRLF
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
        print(f"  [OK] Response ({len(response)} bytes): {response.hex()[:80]}...")
        print(f"       ASCII: {response.decode('ascii', errors='ignore')[:40]}")
    else:
        print("  [X] No response")
    print()
    return response

def send_motor_studio_command(ser, can_id, encoding_name, id_bytes):
    """
    Send Motor Studio command: AT + 00 07 + [4 bytes CAN ID] + 01 00 + CRLF
    
    Args:
        ser: Serial port object
        can_id: CAN node ID
        encoding_name: Name of encoding being tested
        id_bytes: 4 bytes representing the CAN ID
    """
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.extend([0x00, 0x07])  # Command type/length
    packet.extend(id_bytes)  # 4 bytes CAN ID
    packet.extend([0x01, 0x00])  # Enable + parameter
    packet.extend([0x0d, 0x0a])  # CRLF
    
    ser.write(packet)
    time.sleep(0.4)  # Give motor time to respond
    
    response = ser.read(200)
    return response

def test_motor_id(ser, motor_id):
    """Test one motor ID with different 4-byte encodings"""
    print(f"Motor {motor_id} (CAN ID {motor_id}):")
    
    # Try different 4-byte encodings
    encodings = [
        # Direct node ID (little-endian 32-bit)
        ("Direct ID (little-endian)", struct.pack('<I', motor_id)),
        # Direct node ID (big-endian 32-bit)
        ("Direct ID (big-endian)", struct.pack('>I', motor_id)),
        # CANopen SDO COB-ID: 0x600 + node_id (little-endian)
        ("CANopen SDO (0x600+ID)", struct.pack('<I', 0x600 + motor_id)),
        # CANopen RPDO COB-ID: 0x180 + node_id (little-endian)
        ("CANopen RPDO (0x180+ID)", struct.pack('<I', 0x180 + motor_id)),
        # CANopen TPDO COB-ID: 0x200 + node_id (little-endian)
        ("CANopen TPDO (0x200+ID)", struct.pack('<I', 0x200 + motor_id)),
        # CANopen Emergency: 0x80 + node_id (little-endian)
        ("CANopen Emergency (0x80+ID)", struct.pack('<I', 0x80 + motor_id)),
        # Node ID in low byte: ID 00 00 00
        ("ID in low byte", struct.pack('<I', motor_id & 0xFF)),
        # ID in first byte, zeros: ID 00 00 00
        ("ID in first byte", bytes([motor_id, 0x00, 0x00, 0x00])),
    ]
    
    found = []
    for encoding_name, id_bytes in encodings:
        print(f"  Trying {encoding_name}: {id_bytes.hex()}")
        
        # Build command
        packet = bytearray([0x41, 0x54, 0x00, 0x07])
        packet.extend(id_bytes)
        packet.extend([0x01, 0x00, 0x0d, 0x0a])
        
        print(f"    Command: {packet.hex()}")
        
        response = send_motor_studio_command(ser, motor_id, encoding_name, id_bytes)
        
        if response and len(response) > 0:
            print(f"    [OK] RESPONSE! ({len(response)} bytes): {response.hex()[:80]}...")
            try:
                ascii_str = response.decode('ascii', errors='ignore')
                if ascii_str.strip():
                    print(f"         ASCII: {ascii_str[:60]}")
            except:
                pass
            found.append((encoding_name, response))
            print()
            break  # Found working encoding, move to next motor
        else:
            print(f"    [X] No response")
    
    if not found:
        print(f"  [X] No encodings worked for Motor {motor_id}")
    print()
    
    return found

def wait_for_port(port, max_wait=10):
    """Wait for COM port to become available"""
    import time
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            ser = serial.Serial(port, timeout=0.1)
            ser.close()
            return True
        except:
            elapsed = int(time.time() - start_time)
            print(f"  Waiting for {port} to become available... ({elapsed}s)", end='\r')
            time.sleep(1)
    return False

def test_all_motors(port, baudrate=921600):
    """Test all motors with Motor Studio format"""
    # Wait for port to be available
    print(f"Checking if {port} is available...")
    if not wait_for_port(port):
        print(f"\n[X] {port} is still in use. Please close Motor Studio and try again.")
        return {}, {}
    print(f"\n[OK] {port} is available!\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*60)
        print("Motor Studio Command Format Tester")
        print("="*60)
        print(f"Port: {port} at {baudrate} baud")
        print("="*60)
        print()
        
        # Step 1: Initialize
        initialize_adapter(ser)
        time.sleep(0.5)
        
        # Step 2: Test working motors first (to understand the format)
        print("="*60)
        print("Testing motors Motor Studio CAN see (for reference):")
        print("="*60)
        print()
        working_motors = [5, 6, 7, 10, 11, 12, 13, 14]
        working_responses = {}
        
        for motor_id in working_motors:
            responses = test_motor_id(ser, motor_id)
            if responses:
                working_responses[motor_id] = responses[0]
            time.sleep(0.3)
        
        # Step 3: Test missing motors
        print("="*60)
        print("Testing motors Motor Studio CANNOT see:")
        print("="*60)
        print()
        missing_motors = [1, 2, 4, 8, 9]
        missing_responses = {}
        
        for motor_id in missing_motors:
            responses = test_motor_id(ser, motor_id)
            if responses:
                missing_responses[motor_id] = responses[0]
            time.sleep(0.3)
        
        ser.close()
        
        # Summary
        print("="*60)
        print("SUMMARY")
        print("="*60)
        print(f"\nWorking motors (5-14) - Found {len(working_responses)} response(s):")
        for motor_id, (encoding, response) in working_responses.items():
            print(f"  Motor {motor_id}: {encoding}")
            print(f"    Response: {response.hex()[:60]}...")
        
        print(f"\nMissing motors (1,2,4,8,9) - Found {len(missing_responses)} response(s):")
        if missing_responses:
            for motor_id, (encoding, response) in missing_responses.items():
                print(f"  Motor {motor_id}: {encoding}")
                print(f"    Response: {response.hex()[:60]}...")
        else:
            print("  [X] None responded - need to find correct 4-byte encoding")
        
        print("\n[OK] Test complete!")
        
        return working_responses, missing_responses
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        return {}, {}
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        ser.close()
        return {}, {}
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    test_all_motors(port)

