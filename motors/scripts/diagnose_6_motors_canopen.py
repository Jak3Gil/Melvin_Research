#!/usr/bin/env python3
"""
Diagnose why only 4 out of 6 motors respond when all connected
Monitors CAN messages and identifies which motors respond using CanOPEN protocol
"""
import serial
import time
import sys
from collections import defaultdict
from datetime import datetime

# Known motor CAN IDs
KNOWN_MOTORS = [1, 3, 7, 9, 11, 14]

def extract_can_id_from_message(raw_hex):
    """Extract CAN ID from message (same as decode script)"""
    hex_clean = raw_hex.replace('0d0a', '').lower()
    
    if not hex_clean.startswith('4154'):
        return None
    
    # Long format: 41542007e8XX...
    if hex_clean.startswith('41542007e8'):
        if len(hex_clean) >= 12:
            id_byte_hex = hex_clean[10:12]
            try:
                id_byte = int(id_byte_hex, 16)
                long_format_map = {
                    0x0c: 1, 0x1c: 3, 0x3c: 7, 0x4c: 9, 0x74: 14
                }
                if id_byte in long_format_map:
                    return long_format_map[id_byte]
            except:
                pass
    
    # Short format: 41540007e8XX...
    elif hex_clean.startswith('41540007e8'):
        if len(hex_clean) >= 12:
            id_byte_hex = hex_clean[10:12]
            try:
                id_byte = int(id_byte_hex, 16)
                short_format_map = {0x7c: 7, 0x9c: 11}
                if id_byte in short_format_map:
                    return short_format_map[id_byte]
            except:
                pass
    
    return None

def monitor_and_diagnose(port='COM6', baudrate=921600, duration=60):
    """
    Monitor COM6 and diagnose which motors respond
    """
    motors_seen = defaultdict(list)
    all_messages = []
    message_buffer = bytearray()
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print("="*70)
        print("CanOPEN Motor Diagnostic Tool")
        print("="*70)
        print(f"Port: {port}")
        print(f"Expected motors: {KNOWN_MOTORS}")
        print(f"Monitoring for {duration} seconds...")
        print()
        print("INSTRUCTIONS:")
        print("1. Make sure all 6 motors are connected")
        print("2. Open Motor Studio")
        print("3. Start detection/querying")
        print("4. Watch this terminal for motor responses")
        print("="*70)
        print()
        
        start_time = time.time()
        last_summary_time = start_time
        
        while time.time() - start_time < duration:
            data = ser.read(1000)
            
            if data:
                message_buffer.extend(data)
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                
                # Process complete messages (ending with 0d0a)
                while True:
                    crlf_pos = -1
                    for i in range(len(message_buffer) - 1):
                        if message_buffer[i] == 0x0d and message_buffer[i+1] == 0x0a:
                            crlf_pos = i
                            break
                    
                    if crlf_pos >= 0:
                        msg_bytes = message_buffer[:crlf_pos+2]
                        msg_hex = msg_bytes.hex()
                        
                        if len(msg_hex) >= 4:
                            all_messages.append(msg_hex)
                            can_id = extract_can_id_from_message(msg_hex)
                            
                            if can_id and isinstance(can_id, int):
                                motors_seen[can_id].append({
                                    'time': timestamp,
                                    'raw': msg_hex
                                })
                                
                                # Print when we see a motor
                                if len(motors_seen[can_id]) == 1:  # First time seeing this motor
                                    print(f"[{timestamp}] ✓ Motor {can_id} detected! ({len(motors_seen[can_id])} message)")
                                else:
                                    print(f"[{timestamp}] Motor {can_id}: {len(motors_seen[can_id])} messages")
                        
                        message_buffer = message_buffer[crlf_pos+2:]
                    else:
                        break
            
            # Print summary every 5 seconds
            current_time = time.time()
            if current_time - last_summary_time >= 5.0:
                elapsed = int(current_time - start_time)
                found = sorted(motors_seen.keys())
                print(f"\n[{elapsed}s] Summary: Found {len(found)} motor(s): {found}")
                if len(found) < len(KNOWN_MOTORS):
                    missing = set(KNOWN_MOTORS) - set(found)
                    print(f"         Missing: {sorted(missing)}")
                last_summary_time = current_time
            
            time.sleep(0.01)
        
        ser.close()
        
        # Final summary
        print()
        print("="*70)
        print("FINAL DIAGNOSTIC RESULTS")
        print("="*70)
        print()
        
        found_motors = sorted(motors_seen.keys())
        missing_motors = sorted(set(KNOWN_MOTORS) - set(found_motors))
        
        print(f"Motors detected: {len(found_motors)} out of {len(KNOWN_MOTORS)}")
        print()
        
        if found_motors:
            print("RESPONDING MOTORS:")
            for motor_id in found_motors:
                count = len(motors_seen[motor_id])
                print(f"  Motor {motor_id}: {count} message(s)")
                print(f"    First seen: {motors_seen[motor_id][0]['time']}")
        
        if missing_motors:
            print()
            print("NON-RESPONDING MOTORS:")
            for motor_id in missing_motors:
                print(f"  Motor {motor_id}: No messages received")
        
        print()
        print("="*70)
        print("DIAGNOSIS:")
        print("="*70)
        
        if len(found_motors) == len(KNOWN_MOTORS):
            print("✓ All motors responded! Issue might be intermittent or resolved.")
        elif len(found_motors) == 4:
            print(f"⚠️  Only 4 out of 6 motors responded (Motors {found_motors})")
            print()
            print("This suggests a CanOPEN protocol issue:")
            print(f"  - Motors {missing_motors} might not be in Operational state")
            print("  - They might need NMT Start command individually")
            print("  - Possible CanOPEN node ID conflict")
            print("  - Bus priority/timing issue")
            print()
            print("SOLUTIONS TO TRY:")
            print("  1. In Motor Studio, try querying motors individually first")
            print("  2. Send CanOPEN NMT Start to each motor before scanning")
            print("  3. Check if motors {missing_motors} need different CanOPEN configuration")
            print("  4. Try querying in a different order")
        else:
            print(f"Found {len(found_motors)} motor(s), expected {len(KNOWN_MOTORS)}")
        
        print("="*70)
        
        return motors_seen
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        print("\nMake sure Motor Studio is CLOSED first!")
        return None
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        if 'ser' in locals():
            ser.close()
        return motors_seen
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    duration = 60
    if len(sys.argv) > 2:
        duration = int(sys.argv[2])
    
    motors = monitor_and_diagnose(port, duration=duration)

