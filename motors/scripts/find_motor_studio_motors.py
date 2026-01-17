#!/usr/bin/env python3
"""
Find motors that Motor Studio can see using CANopen extended frames
Motor Studio uses: Extended frames, 1Mbps, CANopen protocol
"""
import serial
import struct
import time
import sys

# Motors that Motor Studio CAN see
MOTOR_STUDIO_MOTORS = [5, 6, 7, 10, 11, 12, 13, 14]

def create_canopen_sdo_read(can_id, index=0x2000, subindex=0x00):
    """
    Create CANopen SDO (Service Data Object) read request
    Format: 0x200 + node_id for SDO request
    """
    # CANopen SDO read: 0x40 (expedited read, 4 bytes)
    # Index and subindex specify what to read
    extended_id = 0x600 + can_id  # SDO request to node
    
    # SDO read command format
    data = bytearray([
        0x40,  # Command: Read 4 bytes
        index & 0xFF,  # Index low byte
        (index >> 8) & 0xFF,  # Index high byte
        subindex,  # Subindex
        0x00, 0x00, 0x00, 0x00  # Reserved
    ])
    
    return extended_id, data

def create_canopen_nmt_command(can_id, command=0x01):
    """
    Create CANopen NMT (Network Management) command
    Format: 0x000 for NMT, data contains node_id and command
    """
    extended_id = 0x000  # NMT COB-ID
    data = bytearray([command, can_id])  # Command + node ID
    return extended_id, data

def send_canopen_frame_serial(ser, extended_id, data, frame_format='extended'):
    """
    Send CANopen frame over serial adapter
    Different adapters use different formats - try common ones
    """
    responses = []
    
    # Format 1: SLCAN format (common for USB-CAN adapters)
    # Format: t<id><dlc><data>\r
    # Extended: T<id_8chars><dlc><data>\r
    if frame_format == 'extended':
        # Extended frame: T + 8 hex chars for ID + DLC + data
        id_str = f"{extended_id:08X}"
        dlc = len(data)
        data_str = ''.join(f"{b:02X}" for b in data)
        slcan_cmd = f"T{id_str}{dlc:01X}{data_str}\r"
        ser.write(slcan_cmd.encode())
        time.sleep(0.1)
        response = ser.read(100)
        if response:
            responses.append(('SLCAN', response))
    
    # Format 2: Binary format with header
    # Format: [0xAA, 0x55, id_bytes, dlc, data...]
    packet = bytearray()
    packet.append(0xAA)  # Frame start
    packet.append(0x55)  # Extended frame marker
    packet.extend(struct.pack('<I', extended_id)[:4])  # 29-bit ID
    packet.append(len(data))  # DLC
    packet.extend(data)
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    time.sleep(0.1)
    response = ser.read(100)
    if response:
        responses.append(('Binary', response))
    
    # Format 3: Simple binary (no header)
    packet2 = struct.pack('<I', extended_id)[:4]
    packet2 += bytes([len(data)])
    packet2 += data
    
    ser.write(packet2)
    time.sleep(0.1)
    response = ser.read(100)
    if response:
        responses.append(('Simple', response))
    
    return responses

def wait_for_port(port, max_wait=30):
    """Wait for COM port to become available"""
    import time
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            ser = serial.Serial(port, timeout=0.1)
            ser.close()
            return True
        except:
            print(f"  Waiting for {port} to become available... ({int(time.time() - start_time)}s)", end='\r')
            time.sleep(1)
    return False

def scan_motor_studio_motors(port, baudrate=921600):
    """Scan for motors using Motor Studio's CANopen protocol"""
    # Wait for port to be available
    print(f"\nWaiting for {port} to become available...")
    if not wait_for_port(port):
        print(f"\n[X] {port} is still in use. Please close Motor Studio and try again.")
        return []
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print(f"[OK] Connected to {port} at {baudrate} baud")
        print("Scanning for motors using CANopen extended frames (Motor Studio protocol)\n")
        
        found_motors = []
        
        for motor_id in MOTOR_STUDIO_MOTORS:
            print(f"Testing Motor {motor_id} (CAN ID {motor_id})...")
            
            # Try different CANopen commands
            test_commands = [
                ("NMT Start", create_canopen_nmt_command(motor_id, 0x01)),
                ("NMT Pre-op", create_canopen_nmt_command(motor_id, 0x80)),
                ("SDO Read 0x2000", create_canopen_sdo_read(motor_id, 0x2000, 0x00)),
                ("SDO Read 0x1000", create_canopen_sdo_read(motor_id, 0x1000, 0x00)),
            ]
            
            motor_found = False
            for cmd_name, (extended_id, data) in test_commands:
                print(f"  Trying {cmd_name} (ID: 0x{extended_id:03X})...")
                
                # Try different frame formats
                for fmt in ['extended', 'binary']:
                    responses = send_canopen_frame_serial(ser, extended_id, data, fmt)
                    
                    for fmt_name, response in responses:
                        if response and len(response) > 0:
                            print(f"    [OK] {fmt_name} response: {response.hex()[:60]}...")
                            found_motors.append((motor_id, cmd_name, fmt_name, response))
                            motor_found = True
                            break
                    
                    if motor_found:
                        break
                
                if motor_found:
                    break
                
                time.sleep(0.1)
            
            if not motor_found:
                print(f"  [X] No response")
            
            print()
            time.sleep(0.2)
        
        ser.close()
        
        if found_motors:
            print("\n" + "="*60)
            print("FOUND MOTORS (Motor Studio Protocol):")
            print("="*60)
            for motor_id, cmd, fmt, response in found_motors:
                print(f"Motor {motor_id} - {cmd} ({fmt})")
                print(f"  Response: {response.hex()[:80]}...")
                print()
        else:
            print("\n[X] No motors responded")
            print("\nNOTE: Motor Studio uses CANopen extended frames at 1Mbps")
            print("The adapter might need specific initialization or configuration.")
            print("\nTry:")
            print("1. Check if adapter needs AT commands to enable CANopen mode")
            print("2. Verify bitrate is set to 1Mbps")
            print("3. Check if extended frames are enabled")
        
        return found_motors
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        return []
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_adapter_config(port, baudrate=921600):
    """Test if adapter needs configuration commands"""
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print("\nTesting adapter configuration...")
        
        # Common adapter initialization commands
        init_commands = [
            ("AT+AT", b"AT+AT\r\n"),  # Some adapters need this
            ("ATZ", b"ATZ\r\n"),  # Reset
            ("AT S8", b"AT S8\r\n"),  # Set bitrate code
            ("AT O", b"AT O\r\n"),  # Open channel
        ]
        
        for cmd_name, cmd_bytes in init_commands:
            print(f"  Sending {cmd_name}...")
            ser.write(cmd_bytes)
            time.sleep(0.2)
            response = ser.read(100)
            if response:
                print(f"    Response: {response}")
        
        ser.close()
        
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    port = 'COM3'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print("="*60)
    print("Find Motor Studio Motors - CANopen Extended Frames")
    print("="*60)
    print(f"Target motors: {MOTOR_STUDIO_MOTORS}")
    print(f"Port: {port}")
    print("Protocol: CANopen extended frames (29-bit IDs)")
    print("Bitrate: 1Mbps")
    print("="*60)
    print()
    
    # Test adapter configuration first
    test_adapter_config(port)
    print()
    
    # Scan for motors
    found = scan_motor_studio_motors(port)
    
    if found:
        print("\n[OK] Success! Found motors using Motor Studio protocol")
        print("\nThese motors are configured for CANopen and visible in Motor Studio:")
        for motor_id, cmd, fmt, _ in found:
            print(f"  Motor {motor_id} - CAN ID {motor_id}")

