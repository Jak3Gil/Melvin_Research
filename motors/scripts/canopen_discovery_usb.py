#!/usr/bin/env python3
"""
CANopen Motor Discovery via USB-to-CAN Adapter
Tests CANopen protocol to find motors that might not respond to RobStride protocol
"""
import serial
import time
import struct

PORT = '/dev/ttyUSB0'
BAUD = 921600

def send_canopen_via_l91(ser, can_id, data, extended=False):
    """
    Send CANopen message via L91 protocol (USB-to-CAN adapter)
    
    L91 format for CAN messages:
    AT + 0x01 (CAN TX) + CAN ID (2 bytes) + Data Length (1 byte) + Data (0-8 bytes) + 0x0D 0x0A
    """
    try:
        # L91 CAN transmit command format
        # Byte 0-1: 'AT' (0x41, 0x54)
        # Byte 2: Command type (0x01 = CAN TX)
        # Byte 3-4: CAN ID (high byte, low byte)
        # Byte 5: Data length
        # Byte 6-13: Data (up to 8 bytes)
        # Byte 14-15: 0x0D 0x0A
        
        cmd = bytearray([0x41, 0x54, 0x01])
        
        # CAN ID (11-bit standard)
        cmd.append((can_id >> 8) & 0xFF)
        cmd.append(can_id & 0xFF)
        
        # Data length
        cmd.append(len(data))
        
        # Data
        cmd.extend(data)
        
        # Padding if needed
        while len(cmd) < 14:
            cmd.append(0x00)
        
        # Terminator
        cmd.append(0x0D)
        cmd.append(0x0A)
        
        ser.write(bytes(cmd))
        return True
    except Exception as e:
        print(f"    Error sending: {e}")
        return False

def read_canopen_response(ser, timeout=0.3):
    """Read CANopen response from adapter"""
    response = b""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
            time.sleep(0.02)
    
    return response

def method1_nmt_reset(ser):
    """Method 1: NMT Reset Communication (all nodes)"""
    print("\n" + "="*70)
    print("  METHOD 1: NMT Reset Communication")
    print("="*70)
    print()
    print("Sending NMT Reset to all nodes...")
    print("CANopen nodes should send boot-up messages (0x700 + node_id)")
    print()
    
    # NMT Reset Communication: CAN ID 0x000, Data [0x81, 0x00]
    # Try standard L91 format first
    cmd = bytes([0x41, 0x54, 0x00, 0x00, 0x00, 0x81, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(1.0)
    
    print("Listening for boot-up messages (3 seconds)...")
    responses = []
    start = time.time()
    
    while time.time() - start < 3.0:
        response = read_canopen_response(ser, timeout=0.1)
        if len(response) > 4:
            responses.append(response)
            print(f"  Response: {response.hex()}")
    
    if not responses:
        print("  No boot-up messages detected")
    
    return responses

def method2_sdo_read(ser):
    """Method 2: SDO Read Device Type (Object 0x1000)"""
    print("\n" + "="*70)
    print("  METHOD 2: SDO Read Device Type")
    print("="*70)
    print()
    print("Scanning nodes 1-127 via SDO...")
    print()
    
    found_nodes = []
    
    for node_id in range(1, 128):
        # SDO Read: Object 0x1000 (Device Type)
        # Client to Server: 0x600 + node_id
        can_id = 0x600 + node_id
        
        # SDO Read command: [0x40, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00]
        sdo_data = bytes([0x40, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00])
        
        # Send via L91 format
        send_canopen_via_l91(ser, can_id, sdo_data)
        time.sleep(0.1)
        
        # Check for response (Server to Client: 0x580 + node_id)
        response = read_canopen_response(ser, timeout=0.15)
        
        if len(response) > 6:
            # Check if response looks like SDO response
            # SDO response starts with 0x4B (expedited read response)
            if response[5] == 0x4B or response[4] == 0x4B:
                found_nodes.append(node_id)
                print(f"  Found node {node_id:3d} (0x{node_id:02X})")
        
        if node_id % 20 == 0:
            print(f"  Scanned {node_id}/127...")
    
    print(f"\n✓ Found {len(found_nodes)} node(s) via SDO")
    return found_nodes

def method3_heartbeat_listen(ser):
    """Method 3: Listen for Heartbeat/Node Guard messages"""
    print("\n" + "="*70)
    print("  METHOD 3: Heartbeat/Node Guard Listening")
    print("="*70)
    print()
    print("Listening for heartbeat messages (5 seconds)...")
    print("CANopen nodes send heartbeat at 0x700 + node_id")
    print()
    
    found_nodes = set()
    start = time.time()
    
    while time.time() - start < 5.0:
        response = read_canopen_response(ser, timeout=0.1)
        if len(response) > 6:
            # Try to extract node ID from response
            # Heartbeat: CAN ID 0x700 + node_id
            # L91 response format: AT + Status + ID bytes + Data
            if len(response) >= 6:
                # Parse L91 response format
                # Response: [0x41, 0x54, status, id_high, id_low, data...]
                if response[0] == 0x41 and response[1] == 0x54:
                    if len(response) >= 5:
                        can_id = (response[3] << 8) | response[4]
                        if 0x700 <= can_id <= 0x77F:
                            node_id = can_id - 0x700
                            found_nodes.add(node_id)
                            print(f"  Heartbeat from node {node_id} (CAN ID 0x{can_id:03X})")
    
    found_nodes = sorted(list(found_nodes))
    print(f"\n✓ Found {len(found_nodes)} node(s) via heartbeat")
    return found_nodes

def method4_passive_listen(ser):
    """Method 4: Passive listening for any CANopen traffic"""
    print("\n" + "="*70)
    print("  METHOD 4: Passive Listening (All CANopen Traffic)")
    print("="*70)
    print()
    print("Listening for ANY CANopen messages (5 seconds)...")
    print()
    
    messages = []
    seen_ids = set()
    start = time.time()
    
    while time.time() - start < 5.0:
        response = read_canopen_response(ser, timeout=0.1)
        if len(response) > 4:
            # Store unique messages
            msg_hash = response.hex()[:20]  # First 20 chars for uniqueness
            if msg_hash not in seen_ids:
                seen_ids.add(msg_hash)
                messages.append(response)
                
                # Try to parse CAN ID
                if len(response) >= 5:
                    if response[0] == 0x41 and response[1] == 0x54:
                        can_id = (response[3] << 8) | response[4]
                        print(f"  CAN ID: 0x{can_id:03X}, Data: {response[5:].hex()[:16]}")
    
    print(f"\n✓ Captured {len(messages)} unique message(s)")
    return messages

def method5_try_robstride_format(ser):
    """Method 5: Try CANopen messages using RobStride L91 format"""
    print("\n" + "="*70)
    print("  METHOD 5: CANopen via RobStride L91 Format")
    print("="*70)
    print()
    print("Trying CANopen NMT using standard L91 command format...")
    print()
    
    found_nodes = []
    
    # Try NMT Reset using standard AT format
    print("  Sending NMT Reset (AT format)...")
    cmd = bytes([0x41, 0x54, 0x00, 0x00, 0x00, 0x81, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.5)
    
    response = read_canopen_response(ser, timeout=1.0)
    if len(response) > 4:
        print(f"  Response: {response.hex()}")
    
    # Try scanning nodes 1-50 (faster test)
    print("\n  Testing nodes 1-50 with CANopen SDO...")
    for node_id in range(1, 51):
        # Try sending CANopen SDO read via standard RobStride format
        # Format: AT + 0x20 (command) + CAN ID + Data
        can_id = 0x600 + node_id
        cmd = bytearray([0x41, 0x54, 0x20])
        cmd.extend(struct.pack('>H', can_id))  # CAN ID (big endian)
        cmd.extend([0x08, 0x00])  # Data length
        cmd.extend([0x40, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00])  # SDO read
        cmd.extend([0x0d, 0x0a])
        
        ser.reset_input_buffer()
        ser.write(bytes(cmd))
        time.sleep(0.05)
        
        response = read_canopen_response(ser, timeout=0.1)
        if len(response) > 6:
            if response[5] == 0x4B or response[4] == 0x4B:  # SDO response
                found_nodes.append(node_id)
                print(f"    Found node {node_id}")
    
    print(f"\n✓ Found {len(found_nodes)} node(s)")
    return found_nodes

def main():
    print("="*70)
    print("  CANopen Discovery via USB-to-CAN Adapter")
    print("="*70)
    print()
    print(f"Port: {PORT}")
    print(f"Baud: {BAUD}")
    print()
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"✓ Connected to {PORT}")
        print()
        
        # Send AT+AT to initialize adapter
        print("Initializing adapter...")
        ser.write(b'AT+AT\r\n')
        time.sleep(0.2)
        response = ser.read(100)
        if b'OK' in response:
            print("✓ Adapter responding")
        print()
        
        all_found = set()
        
        # Try all methods
        method1_nmt_reset(ser)
        
        nodes_sdo = method2_sdo_read(ser)
        all_found.update(nodes_sdo)
        
        nodes_heartbeat = method3_heartbeat_listen(ser)
        all_found.update(nodes_heartbeat)
        
        method4_passive_listen(ser)
        
        nodes_format = method5_try_robstride_format(ser)
        all_found.update(nodes_format)
        
        ser.close()
        
        # Summary
        print("\n" + "="*70)
        print("  FINAL RESULTS")
        print("="*70)
        print()
        
        all_found = sorted(list(all_found))
        
        if all_found:
            print(f"✓ Found {len(all_found)} CANopen node(s):")
            print()
            for node_id in all_found:
                print(f"  Node {node_id:3d} (0x{node_id:02X})")
            print()
            print("These nodes use CANopen protocol!")
            print("They may be the motors you're looking for.")
        else:
            print("✗ No CANopen nodes found")
            print()
            print("This suggests:")
            print("  - Motors use RobStride protocol, not CANopen")
            print("  - Or CANopen discovery via USB adapter not supported")
            print("  - Or motors need to be in CANopen mode")
        
        print("="*70)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

