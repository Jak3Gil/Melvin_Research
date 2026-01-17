#!/usr/bin/env python3
"""
Systematically debug and find all 6 motors
Tests different command formats to discover the correct protocol
"""
import serial
import struct
import time
import sys
from collections import defaultdict

KNOWN_MOTORS = [1, 3, 7, 9, 11, 14]

def extract_motor_id_from_response(msg_hex):
    """Extract motor ID from response message"""
    msg_clean = msg_hex.replace('0d0a', '').lower()
    
    if not msg_clean.startswith('4154'):
        return None
    
    # Long format: 41542007e8XX...
    if msg_clean.startswith('41542007e8'):
        if len(msg_clean) >= 12:
            id_byte_hex = msg_clean[10:12]
            try:
                id_byte = int(id_byte_hex, 16)
                motor_map = {0x0c: 1, 0x1c: 3, 0x3c: 7, 0x4c: 9, 0x74: 14}
                return motor_map.get(id_byte)
            except:
                pass
    
    # Short format: 41540007e8XX...
    elif msg_clean.startswith('41540007e8'):
        if len(msg_clean) >= 12:
            id_byte_hex = msg_clean[10:12]
            try:
                id_byte = int(id_byte_hex, 16)
                motor_map = {0x7c: 7, 0x9c: 11}
                return motor_map.get(id_byte)
            except:
                pass
    
    return None

def try_format_1_l91_standard(ser, node_id):
    """
    Format 1: Standard L91 CAN TX format
    AT + 0x01 + CAN_ID (2 bytes) + Data Length + Data + CRLF
    """
    # CanOPEN SDO read: COB-ID = 0x600 + node_id
    cob_id = 0x600 + node_id
    sdo_data = bytes([0x40, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    cmd = bytearray([0x41, 0x54, 0x01])  # AT + CAN TX command
    cmd.append((cob_id >> 8) & 0xFF)      # CAN ID high byte
    cmd.append(cob_id & 0xFF)              # CAN ID low byte
    cmd.append(len(sdo_data))              # Data length
    cmd.extend(sdo_data)                   # Data
    while len(cmd) < 14:                   # Padding
        cmd.append(0x00)
    cmd.extend([0x0d, 0x0a])               # CRLF
    
    return bytes(cmd)

def try_format_2_l91_20_command(ser, node_id):
    """
    Format 2: Using 0x20 command type (from captured messages)
    AT + 0x20 + CAN_ID_bytes + data
    """
    # Try different CAN ID encodings
    cob_id = 0x600 + node_id
    
    cmd = bytearray([0x41, 0x54, 0x20])  # AT + command 0x20
    cmd.extend(struct.pack('<H', cob_id))  # CAN ID little-endian
    cmd.extend([0x08, 0x00])              # Length/flags
    cmd.extend([0x40, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00])  # SDO data
    while len(cmd) < 22:                   # Pad to match captured length
        cmd.append(0x00)
    cmd.extend([0x0d, 0x0a])               # CRLF
    
    return bytes(cmd)

def try_format_3_direct_motor_bytes(ser, node_id):
    """
    Format 3: Using motor-specific byte encoding (from captured messages)
    Based on observed pattern: 41542007e8XX... where XX encodes motor ID
    """
    motor_byte_map = {
        1: 0x0c, 3: 0x1c, 7: 0x3c, 9: 0x4c, 11: 0x7c, 14: 0x74
    }
    
    if node_id not in motor_byte_map:
        return None
    
    id_byte = motor_byte_map[node_id]
    
    # Try long format: 41542007e8XX...
    cmd = bytearray([0x41, 0x54, 0x20])  # AT + 20
    cmd.extend([0x07, 0xe8])              # Base (07e8)
    cmd.append(id_byte)                   # Motor ID byte
    cmd.extend([0x08, 0x00])              # Length
    cmd.extend([0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # Data
    cmd.extend([0x0d, 0x0a])              # CRLF
    
    return bytes(cmd)

def try_format_4_short_format(ser, node_id):
    """
    Format 4: Short format for motors 7 and 11
    41540007e8XX01000d0a
    """
    if node_id == 7:
        id_byte = 0x7c
    elif node_id == 11:
        id_byte = 0x9c
    else:
        return None
    
    cmd = bytearray([0x41, 0x54, 0x00])  # AT + 00
    cmd.extend([0x07, 0xe8])              # Base
    cmd.append(id_byte)                   # Motor ID byte
    cmd.extend([0x01, 0x00])              # Flags
    cmd.extend([0x0d, 0x0a])              # CRLF
    
    return bytes(cmd)

def try_format_5_nmt_start_then_query(ser, node_id):
    """
    Format 5: Send NMT Start first, then query
    """
    # NMT Start command for specific node
    nmt_cmd = bytearray([0x41, 0x54, 0x20])  # AT + 20
    nmt_cmd.extend([0x00, 0x00])             # CAN ID 0x000 (NMT)
    nmt_cmd.extend([0x02, 0x00])             # Length 2
    nmt_cmd.extend([0x01])                   # NMT Start
    nmt_cmd.append(node_id)                  # NMT Start + node ID
    nmt_cmd.extend([0x0d, 0x0a])             # CRLF
    
    # SDO query
    cob_id = 0x600 + node_id
    sdo_cmd = bytearray([0x41, 0x54, 0x20])
    sdo_cmd.extend(struct.pack('<H', cob_id))
    sdo_cmd.extend([0x08, 0x00])
    sdo_cmd.extend([0x40, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00])
    while len(sdo_cmd) < 22:
        sdo_cmd.append(0x00)
    sdo_cmd.extend([0x0d, 0x0a])
    
    return nmt_cmd, sdo_cmd

def test_motor_with_formats(ser, node_id, formats):
    """Test a motor node with multiple formats"""
    results = []
    
    for format_name, format_func in formats:
        try:
            cmd = format_func(ser, node_id)
            if cmd is None:
                continue
                
            # Clear buffer
            ser.reset_input_buffer()
            
            # Special handling for format 5 (NMT then query)
            if format_name == "Format 5":
                nmt_cmd, sdo_cmd = cmd
                ser.write(nmt_cmd)
                time.sleep(0.2)
                ser.read(200)  # Clear response
                ser.write(sdo_cmd)
                time.sleep(0.3)  # Wait for response to SDO query
                cmd = sdo_cmd  # For logging
            else:
                # Send command
                ser.write(cmd)
                time.sleep(0.3)
            
            # Collect responses
            responses = bytearray()
            start_time = time.time()
            while time.time() - start_time < 0.5:
                if ser.in_waiting > 0:
                    responses.extend(ser.read(ser.in_waiting))
                time.sleep(0.05)
            
            # Check for motor response
            response_hex = responses.hex()
            motor_id = extract_motor_id_from_response(response_hex)
            
            if motor_id == node_id:
                results.append({
                    'format': format_name,
                    'success': True,
                    'response': response_hex[:80],
                    'cmd': cmd.hex()[:60]
                })
                return results  # Found it!
            elif motor_id:
                results.append({
                    'format': format_name,
                    'success': False,
                    'response': response_hex[:80],
                    'note': f"Got motor {motor_id} instead of {node_id}"
                })
            elif len(response_hex) > 4:
                results.append({
                    'format': format_name,
                    'success': False,
                    'response': response_hex[:80],
                    'note': "Got response but not recognized motor"
                })
            else:
                results.append({
                    'format': format_name,
                    'success': False,
                    'response': response_hex[:80],
                    'note': "No response"
                })
                
        except Exception as e:
            results.append({
                'format': format_name,
                'success': False,
                'error': str(e)
            })
    
    return results

def find_all_motors(port='COM6', baudrate=921600):
    """Systematically test all formats to find all 6 motors"""
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print("="*70)
        print("Systematic Motor Discovery - All 6 Motors")
        print("="*70)
        print(f"Port: {port} at {baudrate} baud")
        print(f"Testing motors: {KNOWN_MOTORS}")
        print()
        
        # Initialize adapter
        print("Initializing adapter...")
        init_cmd = bytes.fromhex("41542b41540d0a")  # AT+AT
        ser.write(init_cmd)
        time.sleep(0.5)
        ser.read(200)
        print("  [OK] Adapter initialized")
        
        # Send CanOPEN NMT Start All (broadcast to wake all motors)
        print("\nSending CanOPEN NMT Start All (broadcast)...")
        nmt_all_cmd = bytearray([0x41, 0x54, 0x20])  # AT + 20
        nmt_all_cmd.extend([0x00, 0x00])             # CAN ID 0x000 (NMT)
        nmt_all_cmd.extend([0x02, 0x00])             # Length 2
        nmt_all_cmd.extend([0x01, 0x00])             # NMT Start All (node 0x00 = broadcast)
        nmt_all_cmd.extend([0x0d, 0x0a])             # CRLF
        ser.write(bytes(nmt_all_cmd))
        time.sleep(0.5)
        response = ser.read(200)
        if response:
            print(f"  NMT response: {response.hex()[:40]}...")
        print("  Waiting 1 second for motors to respond...")
        time.sleep(1.0)
        
        # Listen for any motor responses (boot messages, heartbeats, etc.)
        print("\nListening for motor responses (2 seconds)...")
        ser.reset_input_buffer()
        passive_data = bytearray()
        start_time = time.time()
        while time.time() - start_time < 2.0:
            if ser.in_waiting > 0:
                passive_data.extend(ser.read(ser.in_waiting))
            time.sleep(0.05)
        
        if len(passive_data) > 0:
            print(f"  Captured {len(passive_data)} bytes of passive data")
            # Parse for motor messages
            passive_hex = passive_data.hex()
            print(f"  Data: {passive_hex[:80]}...")
        else:
            print("  No passive responses detected")
        
        print()
        
        # Define all formats to try
        formats = [
            ("Format 3 (Direct Motor Bytes)", try_format_3_direct_motor_bytes),  # Try this first - matches captured data
            ("Format 4 (Short Format)", try_format_4_short_format),  # For motors 7 and 11
            ("Format 2 (L91 0x20)", try_format_2_l91_20_command),
            ("Format 1 (L91 Standard)", try_format_1_l91_standard),
            ("Format 5 (NMT + SDO)", try_format_5_nmt_start_then_query),
        ]
        
        found_motors = {}
        all_results = {}
        
        # Send device read command (like Motor Studio does)
        print("Sending device read command (AT+A)...")
        read_cmd = bytes.fromhex("41542b41000d0a")  # AT+A + 00 + CRLF
        ser.write(read_cmd)
        time.sleep(0.5)
        ser.read(200)  # Clear response
        print("  [OK] Device read sent")
        print()
        
        # Test each motor
        for node_id in KNOWN_MOTORS:
            print(f"Testing Motor Node {node_id}:")
            print("-" * 70)
            
            results = test_motor_with_formats(ser, node_id, formats)
            all_results[node_id] = results
            
            # Check if we found this motor
            found = False
            for result in results:
                if result.get('success'):
                    found_motors[node_id] = {
                        'format': result['format'],
                        'command': result['cmd']
                    }
                    found = True
                    print(f"  [OK] Found Motor {node_id} using {result['format']}!")
                    break
            
            if not found:
                print(f"  [X] Motor {node_id} not found with any format")
                # Show best attempt
                for result in results:
                    if result.get('response'):
                        print(f"    {result['format']}: {result.get('note', result['response'][:40])}")
            
            print()
            time.sleep(0.5)  # Brief pause between motors
        
        ser.close()
        
        # Summary
        print("="*70)
        print("DISCOVERY RESULTS")
        print("="*70)
        print()
        
        found_count = len(found_motors)
        missing = [m for m in KNOWN_MOTORS if m not in found_motors]
        
        if found_count == len(KNOWN_MOTORS):
            print(f"[SUCCESS] Found all {found_count} motors!")
        else:
            print(f"Found {found_count} out of {len(KNOWN_MOTORS)} motors")
            if missing:
                print(f"Missing motors: {missing}")
        
        print()
        print("Working formats:")
        for motor_id, info in sorted(found_motors.items()):
            print(f"  Motor {motor_id}: {info['format']}")
        
        if found_count < len(KNOWN_MOTORS):
            print()
            print("DEBUGGING INFO:")
            print("="*70)
            for motor_id in missing:
                print(f"\nMotor {motor_id} test results:")
                for result in all_results.get(motor_id, []):
                    print(f"  {result['format']}:")
                    if 'error' in result:
                        print(f"    Error: {result['error']}")
                    elif 'response' in result:
                        print(f"    Response: {result['response']}")
                        if 'note' in result:
                            print(f"    Note: {result['note']}")
        
        print("="*70)
        return found_motors
        
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
    
    print()
    print("Make sure all 6 motors are connected and powered!")
    print("Starting discovery in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = find_all_motors(port)

