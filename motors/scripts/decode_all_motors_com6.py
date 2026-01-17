#!/usr/bin/env python3
"""
Decode all CAN messages from COM6 CH340 adapter
Identifies all motors by parsing the CAN bus data
"""
import serial
import struct
import time
import sys
from collections import defaultdict
from datetime import datetime

def parse_can_message(raw_hex):
    """
    Parse CAN message from hex string
    Format examples:
    - 41542007e80c0800c40000000000000d0a (long format)
    - 41540007e87c01000d0a (short format)
    - 415400007ffc0801020304050600000d0a (CanOPEN)
    """
    # Remove CRLF (0d0a) at end
    if raw_hex.endswith('0d0a'):
        raw_hex = raw_hex[:-4]
    
    # Check for "AT" prefix (4154)
    if not raw_hex.startswith('4154'):
        return None
    
    # Skip "AT" and analyze the rest
    data_hex = raw_hex[4:]
    
    if len(data_hex) < 4:
        return None
    
    # Try to extract CAN ID from different positions
    can_id = None
    message_type = "unknown"
    
    # Long format: 41542007e80c0800c40000000000000d0a
    # Pattern: AT + 20 + 07e8 + [CAN data...]
    if data_hex.startswith('20'):
        # Skip "20", then we have "07e8..."
        rest = data_hex[2:]
        if len(rest) >= 4:
            # Look at position that might contain CAN ID
            # Try extracting from different positions
            # Position 2-3 after "07e8" might be part of CAN ID
            if len(rest) >= 8:
                byte_at_2 = rest[4:6]  # The byte that changes (0c, 1c, 3c, 4c, 74)
                byte_at_3 = rest[6:8]
                # Try different interpretations
                message_type = "long_format"
    
    # Short format: 41540007e87c01000d0a
    # Pattern: AT + 00 + 07e8 + [data]
    elif data_hex.startswith('00'):
        rest = data_hex[2:]
        if len(rest) >= 8:
            # Extract the byte that might represent CAN ID
            byte_after_e8 = rest[4:6]  # e8 9c -> 9c
            if byte_after_e8:
                try:
                    # Try as direct CAN ID
                    can_id_val = int(byte_after_e8, 16)
                    # Or it might be encoded differently
                    message_type = "short_format"
                except:
                    pass
    
    return {
        'raw': raw_hex,
        'type': message_type,
        'data': data_hex
    }

def extract_can_id_from_message(raw_hex):
    """
    Extract CAN ID from message hex string
    Based on the patterns provided by the user
    
    Known patterns:
    - CAN ID 1:  41542007e80c0800c40000000000000d0a -> byte 0c
    - CAN ID 3:  41542007e81c0800c40000000000000d0a -> byte 1c
    - CAN ID 7:  41542007e83c0800c40000000000000d0a -> byte 3c
                  41540007e87c01000d0a -> byte 7c (different format)
    - CAN ID 9:  41542007e84c0800c40000000000000d0a -> byte 4c
    - CAN ID 11: 41540007e89c01000d0a -> byte 9c
    - CAN ID 14: 41542007e8740800c40000000000000d0a -> byte 74
    """
    # Remove CRLF and convert to lowercase
    hex_clean = raw_hex.replace('0d0a', '').lower()
    
    if not hex_clean.startswith('4154'):
        return None
    
    # Direct mapping based on observed patterns
    # Format 1: 41542007e8XX... (long format)
    if hex_clean.startswith('41542007e8'):
        if len(hex_clean) >= 12:
            id_byte_hex = hex_clean[10:12]
            try:
                id_byte = int(id_byte_hex, 16)
                # Direct mapping from observed values
                long_format_map = {
                    0x0c: 1,   # CAN ID 1
                    0x1c: 3,   # CAN ID 3
                    0x3c: 7,   # CAN ID 7
                    0x4c: 9,   # CAN ID 9
                    0x74: 14,  # CAN ID 14
                }
                if id_byte in long_format_map:
                    return long_format_map[id_byte]
                # If not in map, try to decode: might be CAN ID encoded as (byte >> 2) - 2
                # But only for unlisted values
                return id_byte
            except:
                pass
    
    # Format 2: 41540007e8XX... (short format)
    elif hex_clean.startswith('41540007e8'):
        if len(hex_clean) >= 12:
            id_byte_hex = hex_clean[10:12]
            try:
                id_byte = int(id_byte_hex, 16)
                # Direct mapping for short format
                short_format_map = {
                    0x7c: 7,   # CAN ID 7
                    0x9c: 11,  # CAN ID 11
                }
                if id_byte in short_format_map:
                    return short_format_map[id_byte]
                # Try decoding: for short format, might be different encoding
                # 7c = 124, CAN ID 7; 9c = 156, CAN ID 11
                # Pattern unclear, but maybe: (byte - 100) / 8? (124-100)/8=3, no
                # Or: byte >> 3? 124>>3=15, no
                # Keep raw for now
                return id_byte
            except:
                pass
    
    # Format 3: CanOPEN format 415400007ffc...
    elif hex_clean.startswith('415400007ffc'):
        # This is a CanOPEN to private protocol message
        return "CanOPEN"
    
    return None

def decode_can_data(raw_hex):
    """
    Full decode of CAN message
    """
    can_id = extract_can_id_from_message(raw_hex)
    
    # Parse message structure
    hex_clean = raw_hex.replace('0d0a', '').lower()
    
    if hex_clean.startswith('4154'):
        data_start = 4  # Skip "AT"
        msg_type = hex_clean[data_start:data_start+2]  # "20" or "00"
        rest = hex_clean[data_start+2:]
        
        return {
            'can_id': can_id,
            'message_type': msg_type,
            'raw_hex': raw_hex,
            'full_data': rest
        }
    
    return None

def monitor_com6(port='COM6', baudrate=921600, duration=60):
    """
    Monitor COM6 and decode all CAN messages
    """
    motors_found = defaultdict(list)
    unrecognized_messages = []
    message_buffer = bytearray()  # Buffer for incomplete messages
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"[OK] Connected to {port} at {baudrate} baud")
        print(f"Monitoring for {duration} seconds...")
        print("="*70)
        print()
        
        # Send initialization command (like Motor Studio does)
        print("Sending initialization command (AT+AT)...")
        init_cmd = bytes.fromhex("41542b41540d0a")  # AT+AT + CRLF
        ser.write(init_cmd)
        time.sleep(0.5)
        init_response = ser.read(200)
        if init_response:
            print(f"  Response: {init_response.hex()}")
        print()
        
        # Send device read command (like Motor Studio does)
        print("Sending device read command (AT+A)...")
        read_cmd = bytes.fromhex("41542b41000d0a")  # AT+A + 00 + CRLF
        ser.write(read_cmd)
        time.sleep(0.5)
        read_response = ser.read(200)
        if read_response:
            print(f"  Response: {read_response.hex()}")
        print()
        
        # CanOPEN: Send NMT Start to all nodes to put them in Operational state
        # This might help all 6 motors respond when connected together
        print("Sending CanOPEN NMT Start (all nodes to Operational state)...")
        # NMT Start All: CAN ID 0x000, Data [0x01, 0x00]
        # The messages you captured show format 41542007e8XX... for responses
        # Commands might use a different format - try common ones
        
        # Based on your messages, try sending a CAN frame command
        # Format might be: AT + command + CAN ID + data
        nmt_commands = [
            bytes.fromhex("41540000000001000d0a"),  # AT + 00 + CAN ID 0x000 + data [0x01, 0x00]
            bytes.fromhex("41542000000001000d0a"),  # AT + 20 + CAN ID 0x000 + data
        ]
        
        for nmt_cmd in nmt_commands:
            ser.write(nmt_cmd)
            time.sleep(0.3)
            response = ser.read(200)
            if response:
                print(f"  NMT response: {response.hex()[:60]}...")
        print()
        
        # Give motors time to enter Operational state
        print("Waiting 1 second for motors to enter Operational state...")
        time.sleep(1.0)
        print()
        
        # Query each motor individually using the exact formats from captured data
        print("Querying each motor individually...")
        print("(Based on your captured messages showing all 6 motors)")
        print()
        
        motor_queries = [
            ("Motor 1 (CAN ID 1)", "41542007e80c0800c40000000000000d0a"),
            ("Motor 3 (CAN ID 3)", "41542007e81c0800c40000000000000d0a"),
            ("Motor 7 (CAN ID 7)", "41542007e83c0800c40000000000000d0a"),
            ("Motor 9 (CAN ID 9)", "41542007e84c0800c40000000000000d0a"),
            ("Motor 11 (CAN ID 11)", "41540007e89c01000d0a"),
            ("Motor 14 (CAN ID 14)", "41542007e8740800c40000000000000d0a"),
        ]
        
        # Actually, these look like RESPONSES, not queries
        # Let's try sending queries that might trigger these responses
        # Based on test_motor_studio_exact_format.py format
        motor_query_bytes = [
            ("Motor 1", "e80c0100"),   # From 41542007e80c...
            ("Motor 3", "e81c0100"),   # From 41542007e81c...
            ("Motor 7", "e83c0100"),   # From 41542007e83c...
            ("Motor 9", "e84c0100"),   # From 41542007e84c...
            ("Motor 11", "e89c0100"),  # From 41540007e89c...
            ("Motor 14", "e8740100"),  # From 41542007e874...
        ]
        
        print("Sending individual motor queries...")
        for motor_name, four_bytes in motor_query_bytes:
            # Format: AT + 00 07 + [4 bytes] + 01 00 + CRLF
            query = bytearray([0x41, 0x54])  # "AT"
            query.extend([0x00, 0x07])
            query.extend(bytes.fromhex(four_bytes))
            query.extend([0x01, 0x00])
            query.extend([0x0d, 0x0a])  # CRLF
            
            ser.write(query)
            time.sleep(0.3)  # Wait for response
            response = ser.read(500)
            if response:
                hex_response = response.hex()
                # Check if this looks like a motor response
                can_id = extract_can_id_from_message(hex_response)
                if can_id:
                    print(f"  {motor_name}: RESPONDED! (CAN ID {can_id})")
                else:
                    print(f"  {motor_name}: Response {len(response)} bytes - {hex_response[:80]}...")
            else:
                print(f"  {motor_name}: No response")
        print()
        
        start_time = time.time()
        message_count = 0
        total_bytes_received = 0
        all_raw_data = []  # Store all raw data for analysis
        last_query_time = 0
        query_interval = 1.0  # Query every 1 second
        
        print("Starting continuous monitoring with periodic queries...")
        print("Watch for CAN messages below:")
        print("-" * 70)
        print()
        
        while time.time() - start_time < duration:
            # Periodically send queries to trigger responses
            current_time = time.time()
            if current_time - last_query_time >= query_interval:
                last_query_time = current_time
                # Send device read command periodically
                read_cmd = bytes.fromhex("41542b41000d0a")
                ser.write(read_cmd)
                time.sleep(0.1)  # Brief pause
            
            # Read data
            data = ser.read(1000)
            
            if data:
                total_bytes_received += len(data)
                # Store raw data for analysis
                all_raw_data.append({
                    'time': datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    'data': data.hex()
                })
                # Add to buffer
                message_buffer.extend(data)
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                messages = []
                
                # Process complete messages (ending with 0d0a)
                while True:
                    # Find CRLF
                    crlf_pos = -1
                    for i in range(len(message_buffer) - 1):
                        if message_buffer[i] == 0x0d and message_buffer[i+1] == 0x0a:
                            crlf_pos = i
                            break
                    
                    if crlf_pos >= 0:
                        # Extract complete message
                        msg_bytes = message_buffer[:crlf_pos+2]
                        msg_hex = msg_bytes.hex()
                        
                        if len(msg_hex) >= 4:  # At least some data + CRLF
                            messages.append(msg_hex)
                        
                        # Remove processed message
                        message_buffer = message_buffer[crlf_pos+2:]
                    else:
                        # No complete message found, keep remainder in buffer
                        break
                
                # Process all complete messages
                for msg_hex in messages:
                    message_count += 1
                    
                    # Check for initialization messages
                    if msg_hex.startswith('41542b4154') or msg_hex.startswith('41542b41'):
                        print(f"[{timestamp}] Init message: {msg_hex}")
                        continue
                    
                    decoded = decode_can_data(msg_hex)
                    
                    if decoded:
                        motor_id = decoded['can_id']
                        
                        if motor_id and motor_id != "CanOPEN" and isinstance(motor_id, int):
                            # Valid motor ID found
                            motors_found[motor_id].append({
                                'time': timestamp,
                                'raw': msg_hex,
                                'decoded': decoded
                            })
                            
                            print(f"[{timestamp}] Message #{message_count}")
                            print(f"  CAN ID: {motor_id}")
                            print(f"  Type: {decoded['message_type']}")
                            print(f"  Hex: {msg_hex}")
                            print()
                        elif motor_id == "CanOPEN":
                            print(f"[{timestamp}] CanOPEN protocol message: {msg_hex[:60]}...")
                        else:
                            # Unrecognized format - save for analysis
                            unrecognized_messages.append({
                                'time': timestamp,
                                'raw': msg_hex
                            })
                            print(f"[{timestamp}] Message #{message_count} - UNRECOGNIZED (no CAN ID)")
                            print(f"  Hex: {msg_hex}")
                            # Try to show which format it might be
                            hex_clean = msg_hex.replace('0d0a', '').lower()
                            if hex_clean.startswith('41542007e8'):
                                print(f"  Format: Long format (41542007e8...)")
                                if len(hex_clean) >= 12:
                                    byte_val = hex_clean[10:12]
                                    print(f"  Byte at position: 0x{byte_val}")
                            elif hex_clean.startswith('41540007e8'):
                                print(f"  Format: Short format (41540007e8...)")
                                if len(hex_clean) >= 12:
                                    byte_val = hex_clean[10:12]
                                    print(f"  Byte at position: 0x{byte_val}")
                            print()
                    else:
                        # Could not decode at all
                        unrecognized_messages.append({
                            'time': timestamp,
                            'raw': msg_hex
                        })
                        print(f"[{timestamp}] Message #{message_count} - DECODE FAILED")
                        print(f"  Hex: {msg_hex}")
                        print()
            
            time.sleep(0.01)
        
        ser.close()
        
        print("="*70)
        print(f"Monitoring complete!")
        print(f"  Total bytes received: {total_bytes_received}")
        print(f"  Messages parsed: {message_count}")
        if len(message_buffer) > 0:
            print(f"  Unprocessed data in buffer: {len(message_buffer)} bytes - {message_buffer.hex()}")
        print("="*70)
        print()
        
        # Show all raw data received for analysis
        if all_raw_data:
            print("ALL RAW DATA RECEIVED:")
            print("="*70)
            for entry in all_raw_data:
                print(f"[{entry['time']}] {entry['data']}")
            print("="*70)
            print()
        
        # Summary
        print("MOTORS DETECTED:")
        print("="*70)
        if motors_found:
            for motor_id in sorted(motors_found.keys()):
                count = len(motors_found[motor_id])
                print(f"  Motor ID {motor_id}: {count} message(s)")
                # Show first message as example
                if motors_found[motor_id]:
                    example = motors_found[motor_id][0]
                    print(f"    Example: {example['raw'][:60]}...")
        else:
            print("  No motors detected!")
        
        print("="*70)
        print(f"Total unique motors: {len(motors_found)}")
        print(f"Expected: 6 motors")
        
        if unrecognized_messages:
            print(f"\nUNRECOGNIZED MESSAGES ({len(unrecognized_messages)}):")
            print("="*70)
            for msg in unrecognized_messages[:10]:  # Show first 10
                print(f"  [{msg['time']}] {msg['raw']}")
            if len(unrecognized_messages) > 10:
                print(f"  ... and {len(unrecognized_messages) - 10} more")
            print("="*70)
            print("\n[WARNING] Some messages could not be decoded!")
            print("    These might contain CAN IDs for the missing motors.")
            print("    Check the hex patterns above to identify the missing motor IDs.")
        
        if len(motors_found) < 6:
            print(f"\n[WARNING] Only found {len(motors_found)} out of 6 motors!")
            print("Possible reasons:")
            print("  - Some motors not responding")
            print("  - CAN ID extraction logic needs adjustment")
            print("  - Messages not being parsed correctly")
            if unrecognized_messages:
                print(f"  - {len(unrecognized_messages)} unrecognized message(s) might contain missing motors")
        
        return motors_found
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        print("\nMake sure:")
        print("  - CH340 adapter is connected")
        print("  - Motor Studio is closed")
        print("  - Port is not in use by another program")
        return None
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        if 'ser' in locals():
            ser.close()
        return motors_found
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()
        return None

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    duration = 60
    if len(sys.argv) > 2:
        duration = int(sys.argv[2])
    
    print("="*70)
    print("CAN Motor Decoder - COM6 Monitor")
    print("="*70)
    print(f"Port: {port}")
    print(f"Duration: {duration} seconds")
    print()
    print("INSTRUCTIONS:")
    print("1. Make sure Motor Studio is CLOSED")
    print("2. Connect all 6 motors")
    print("3. Run this script")
    print("4. Watch for CAN message decoding")
    print("="*70)
    print()
    
    motors = monitor_com6(port, duration=duration)

