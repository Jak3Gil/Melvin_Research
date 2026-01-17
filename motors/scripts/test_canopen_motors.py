#!/usr/bin/env python3
"""
Test motors using CANopen protocol with extended frames at 1Mbps
Motor Studio uses: Extended frame, 1Mbps, CANopen protocol
"""
import serial
import struct
import time
import sys

# Missing motors that Motor Studio can't see
MISSING_MOTORS = [1, 2, 4, 8, 9]

def create_canopen_extended_frame(can_id, data):
    """
    Create CANopen extended frame (29-bit ID)
    CANopen uses specific ID ranges:
    - 0x600 + node_id: TPDO1 (Transmit Process Data Object)
    - 0x700 + node_id: Emergency messages
    - 0x180 + node_id: RPDO1 (Receive Process Data Object) - for control
    - 0x200 + node_id: SDO (Service Data Object) - for configuration
    
    For motor control, we typically use:
    - 0x200 + node_id for SDO (configuration/control)
    - 0x180 + node_id for RPDO (real-time control)
    """
    # CANopen extended frame format over serial
    # Format might be: [frame_type][extended_id][dlc][data]
    # Or: [0xAA][0x55][extended_id_bytes][data]
    
    # Try CANopen SDO format (0x200 + node_id)
    extended_id = 0x200 + can_id
    
    # Serial CAN adapter format (varies by adapter)
    # Common format: [0xAA, 0x55, id_byte3, id_byte2, id_byte1, id_byte0, dlc, data...]
    packet = bytearray()
    packet.append(0xAA)  # Frame start
    packet.append(0x55)  # Extended frame marker
    
    # Extended ID (29-bit) - little endian
    packet.extend(struct.pack('<I', extended_id)[:4])
    
    # DLC (Data Length Code)
    packet.append(len(data))
    
    # Data
    packet.extend(data)
    
    # Checksum (if needed)
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    return packet

def create_canopen_rpdo_frame(can_id, data):
    """
    Create CANopen RPDO frame (0x180 + node_id) for real-time control
    """
    extended_id = 0x180 + can_id
    
    packet = bytearray()
    packet.append(0xAA)
    packet.append(0x55)
    packet.extend(struct.pack('<I', extended_id)[:4])
    packet.append(len(data))
    packet.extend(data)
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    return packet

def test_canopen_motors(port, baudrate=921600):
    """Test motors using CANopen protocol"""
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print(f"[OK] Connected to {port} at {baudrate} baud")
        print("Testing CANopen extended frame protocol (1Mbps equivalent)\n")
        
        found_motors = []
        
        for motor_id in MISSING_MOTORS:
            print(f"Testing Motor {motor_id} with CANopen...")
            
            # Try different CANopen message types
            test_commands = [
                ("SDO Read (0x200+ID)", create_canopen_extended_frame(motor_id, [0x40, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00])),
                ("RPDO1 (0x180+ID)", create_canopen_rpdo_frame(motor_id, [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])),
                ("TPDO1 Request (0x600+ID)", create_canopen_extended_frame(motor_id - 0x200 + 0x600, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])),
            ]
            
            for cmd_name, packet in test_commands:
                print(f"  Trying {cmd_name}: {packet.hex()[:40]}...")
                ser.write(packet)
                time.sleep(0.2)
                
                response = ser.read(100)
                if response and len(response) > 0:
                    print(f"    [OK] RESPONSE! {len(response)} bytes: {response.hex()[:60]}...")
                    found_motors.append((motor_id, cmd_name, response))
                    break
                else:
                    print(f"    [X] No response")
            
            print()
            time.sleep(0.1)
        
        ser.close()
        
        if found_motors:
            print("\n" + "="*50)
            print("FOUND MOTORS WITH CANOPEN:")
            print("="*50)
            for motor_id, cmd_type, response in found_motors:
                print(f"Motor {motor_id} - {cmd_type}")
                print(f"  Response: {response.hex()[:60]}...")
        else:
            print("\n[X] No motors responded to CANopen protocol")
            print("\nNOTE: Motor Studio uses CANopen extended frames at 1Mbps")
            print("The adapter might need specific configuration for CANopen mode.")
        
        return found_motors
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        return []
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    port = 'COM3'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print("="*50)
    print("CANopen Extended Frame Motor Test")
    print("="*50)
    print(f"Target motors: {MISSING_MOTORS}")
    print(f"Port: {port}")
    print("Protocol: CANopen extended frames (29-bit IDs)")
    print("Bitrate: 1Mbps (via adapter)")
    print("="*50)
    print()
    
    found = test_canopen_motors(port)
    
    if found:
        print("\n[OK] Success! These motors responded to CANopen protocol")
        print("\nYou can now configure Motor Studio to use:")
        for motor_id, cmd_type, _ in found:
            print(f"  Motor {motor_id} - CAN ID {motor_id} (CANopen node {motor_id})")

