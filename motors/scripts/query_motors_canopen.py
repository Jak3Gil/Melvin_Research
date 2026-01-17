#!/usr/bin/env python3
"""
Query motors using CanOPEN protocol via COM6
Uses CanOPEN SDO (Service Data Object) to query each motor node
"""
import serial
import struct
import time
import sys
from collections import defaultdict

# Known motor CAN IDs from your captured messages
KNOWN_MOTOR_IDS = [1, 3, 7, 9, 11, 14]

def send_canopen_sdo_read(ser, node_id, index=0x1000, subindex=0x00):
    """
    Send CanOPEN SDO read request
    Client to Server: COB-ID = 0x600 + node_id
    Command: 0x40 (expedited read, 4 bytes)
    """
    # CanOPEN SDO request COB-ID
    cob_id = 0x600 + node_id
    
    # SDO read command format
    # 0x40 = expedited read, 4 bytes indicated
    sdo_data = bytearray([
        0x40,           # Command: Read 4 bytes expedited
        index & 0xFF,           # Index low byte
        (index >> 8) & 0xFF,    # Index high byte  
        subindex,               # Subindex
        0x00, 0x00, 0x00, 0x00  # Reserved/padding
    ])
    
    # Based on your message format: 41542007e8XX...
    # Format might be: AT + 20 + CAN ID (little endian?) + data
    # Try format: AT + 20 + [COB-ID bytes] + [data]
    
    # Format 1: Try the format from captured messages
    # 41542007e80c0800c40000000000000d0a
    # AT(4154) + 20 + 07e8(?) + 0c(?) + 08 + 00 + c4 + 00...
    cmd = bytearray([0x41, 0x54])  # "AT"
    cmd.append(0x20)  # Command type
    
    # Try encoding COB-ID: cob_id = 0x600 + node_id
    # For node 1: 0x601 = 0x0601
    # Little-endian: 01 06, but we see 07e8...
    # Maybe it's: 0x07e8 = 2024, and 2024 - 0x600 = 2024 - 1536 = 488? No...
    
    # Actually, looking at the pattern:
    # Motor 1: 41542007e80c... -> 0c at position
    # Motor 3: 41542007e81c... -> 1c at position  
    # Motor 7: 41542007e83c... -> 3c at position
    # Motor 9: 41542007e84c... -> 4c at position
    # Motor 14: 41542007e874... -> 74 at position
    
    # The byte that changes is at position after "07e8"
    # Maybe 07e8 is a base, and the next byte encodes the node ID?
    
    # Try standard format: AT + 20 + COB-ID (2 bytes LE) + data length + data
    cob_id_bytes = struct.pack('<H', cob_id)  # Little-endian 16-bit
    cmd.extend(cob_id_bytes)
    cmd.append(len(sdo_data))  # Data length
    cmd.extend(sdo_data)
    
    # Pad to match your message length (if needed)
    while len(cmd) < 22:  # Your messages are longer
        cmd.append(0x00)
    
    cmd.extend([0x0d, 0x0a])  # CRLF
    
    return cmd

def send_canopen_via_format(ser, node_id):
    """
    Try sending CanOPEN query using the exact format from captured messages
    """
    # Your captured format for Motor 1: 41542007e80c0800c40000000000000d0a
    # Let's try to reverse engineer this format
    
    # For each motor, the byte at position changes:
    # Motor 1 (node 1):  0c
    # Motor 3 (node 3):  1c  
    # Motor 7 (node 7):  3c
    # Motor 9 (node 9):  4c
    # Motor 14 (node 14): 74
    
    # Pattern: byte = (node_id << 4) + 0x0c? 
    # 1 << 4 = 16 = 0x10, + 0x0c = 0x1c (but Motor 1 uses 0c, not 1c)
    # (node_id - 1) << 4 + 0x0c?
    # Motor 1: (1-1)<<4+0x0c = 0x0c ✓
    # Motor 3: (3-1)<<4+0x0c = 0x2c (but we see 1c) ✗
    
    # Try: byte = node_id * 0x10 - 0x04?
    # Motor 1: 1*0x10-0x04 = 0x0c ✓
    # Motor 3: 3*0x10-0x04 = 0x2c ✗
    
    # Actually, let's just map directly for now
    id_byte_map = {
        1: 0x0c,
        3: 0x1c,
        7: 0x3c,
        9: 0x4c,
        11: 0x7c,  # From short format
        14: 0x74
    }
    
    if node_id not in id_byte_map:
        return None
    
    id_byte = id_byte_map[node_id]
    
    # Build command using long format: 41542007e8XX0800c40000000000000d0a
    cmd = bytearray([0x41, 0x54])  # "AT"
    cmd.append(0x20)  # Command type
    cmd.extend([0x07, 0xe8])  # Base (07e8)
    cmd.append(id_byte)  # Node ID encoding
    cmd.extend([0x08, 0x00])  # Length or flags
    cmd.extend([0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # Data/padding
    cmd.extend([0x0d, 0x0a])  # CRLF
    
    return cmd

def query_motors_canopen(port='COM6', baudrate=921600):
    """
    Query motors using CanOPEN protocol
    """
    motors_found = defaultdict(list)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print(f"[OK] Connected to {port} at {baudrate} baud")
        print("="*70)
        print()
        
        # Initialize adapter
        print("Initializing adapter...")
        init_cmd = bytes.fromhex("41542b41540d0a")  # AT+AT
        ser.write(init_cmd)
        time.sleep(0.5)
        response = ser.read(200)
        if response:
            print(f"  Init response: {response.hex()}")
        print()
        
        # Send CanOPEN NMT Start to put all nodes in Operational state
        print("Sending CanOPEN NMT Start (all nodes)...")
        # NMT Start All: CAN ID 0x000, Data [0x01, 0x00]
        # Try different formats the adapter might accept
        nmt_formats = [
            # Format 1: Standard CAN frame
            bytes.fromhex("41540000000001000000000000000000000d0a"),  # AT + 00 + CAN ID 0x000 + data
            # Format 2: With command type
            bytes.fromhex("41542000000001000000000000000000000d0a"),  # AT + 20 + CAN ID
        ]
        
        for i, nmt_cmd in enumerate(nmt_formats, 1):
            print(f"  Trying NMT format {i}: {nmt_cmd.hex()}")
            ser.write(nmt_cmd)
            time.sleep(0.5)
            response = ser.read(200)
            if response:
                print(f"    Response: {response.hex()}")
        print()
        
        # Query each known motor using CanOPEN
        print("Querying motors using CanOPEN SDO...")
        print("-" * 70)
        
        for node_id in KNOWN_MOTOR_IDS:
            print(f"\nQuerying Motor Node {node_id}:")
            
            # Try the format from captured messages
            cmd = send_canopen_via_format(ser, node_id)
            if cmd:
                print(f"  Sending: {cmd.hex()}")
                ser.write(cmd)
                time.sleep(0.5)
                
                response = ser.read(500)
                if response:
                    hex_response = response.hex()
                    print(f"  Response ({len(response)} bytes): {hex_response}")
                    
                    # Check if this looks like a motor response
                    # Responses should have similar format
                    if len(hex_response) > 10:
                        motors_found[node_id].append({
                            'raw': hex_response,
                            'bytes': len(response)
                        })
                        print(f"  [OK] Motor {node_id} RESPONDED!")
                    else:
                        print(f"  [INFO] Short response (might be ACK)")
                else:
                    print(f"  [X] No response from Motor {node_id}")
            else:
                print(f"  [SKIP] No format mapping for Motor {node_id}")
            
            time.sleep(0.2)
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("RESULTS:")
        print("="*70)
        
        if motors_found:
            print(f"Found {len(motors_found)} motor(s) responding:")
            for node_id in sorted(motors_found.keys()):
                count = len(motors_found[node_id])
                print(f"  Motor Node {node_id}: {count} response(s)")
                if motors_found[node_id]:
                    print(f"    Example: {motors_found[node_id][0]['raw'][:60]}...")
        else:
            print("No motors responded!")
        
        print()
        print(f"Expected: {len(KNOWN_MOTOR_IDS)} motors (IDs: {KNOWN_MOTOR_IDS})")
        if len(motors_found) < len(KNOWN_MOTOR_IDS):
            missing = set(KNOWN_MOTOR_IDS) - set(motors_found.keys())
            print(f"Missing: {sorted(missing)}")
            print("\nPossible reasons:")
            print("  - Those motors not powered/connected")
            print("  - CanOPEN node state issue (need NMT Start)")
            print("  - Bus contention when all connected")
        
        print("="*70)
        
        return motors_found
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        return None
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print("="*70)
    print("CanOPEN Motor Query Tool")
    print("="*70)
    print(f"Port: {port}")
    print(f"Protocol: CanOPEN SDO")
    print(f"Known motors: {KNOWN_MOTOR_IDS}")
    print()
    
    motors = query_motors_canopen(port)

