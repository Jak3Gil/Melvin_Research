#!/usr/bin/env python3
"""
Passively listen for all motor messages (heartbeats, boot messages, etc.)
Motors might send unsolicited messages that we can detect
"""
import serial
import time
import sys
from collections import defaultdict

KNOWN_MOTORS = [1, 3, 7, 9, 11, 14]

def extract_motor_id(msg_hex):
    """Extract motor ID from message"""
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

def passive_listen(port='COM6', baudrate=921600, duration=30):
    """Passively listen for any motor messages"""
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print("="*70)
        print("Passive Motor Listening")
        print("="*70)
        print(f"Port: {port} at {baudrate} baud")
        print(f"Duration: {duration} seconds")
        print()
        print("Listening for any CAN messages from motors...")
        print("(boot messages, heartbeats, unsolicited responses, etc.)")
        print("="*70)
        print()
        
        # Initialize adapter
        print("Initializing adapter...")
        init_cmd = bytes.fromhex("41542b41540d0a")  # AT+AT
        ser.write(init_cmd)
        time.sleep(0.5)
        ser.read(200)
        print("  [OK] Adapter initialized")
        print()
        
        # Send device read (might trigger responses)
        print("Sending device read command...")
        read_cmd = bytes.fromhex("41542b41000d0a")  # AT+A
        ser.write(read_cmd)
        time.sleep(0.5)
        ser.read(200)
        print("  [OK] Device read sent")
        print()
        
        # Now listen passively
        print(f"Listening for {duration} seconds...")
        print("-" * 70)
        
        motors_found = defaultdict(list)
        all_messages = []
        message_buffer = bytearray()
        start_time = time.time()
        message_count = 0
        
        while time.time() - start_time < duration:
            # Read data
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                message_buffer.extend(data)
            
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
                        message_count += 1
                        timestamp = time.time() - start_time
                        
                        # Check if it's a motor message
                        motor_id = extract_motor_id(msg_hex)
                        
                        if motor_id:
                            motors_found[motor_id].append({
                                'time': timestamp,
                                'hex': msg_hex
                            })
                            print(f"[{timestamp:.1f}s] Motor {motor_id} detected! ({len(motors_found[motor_id])} message(s))")
                        elif msg_hex != "4f4b0d0a" and msg_hex not in ["014a0d0a", "014d0d0a"]:
                            # Non-motor message but interesting
                            all_messages.append(msg_hex)
                            print(f"[{timestamp:.1f}s] Unknown message: {msg_hex[:60]}...")
                    
                    message_buffer = message_buffer[crlf_pos+2:]
                else:
                    break
            
            time.sleep(0.05)
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("LISTENING RESULTS")
        print("="*70)
        print()
        print(f"Total messages captured: {message_count}")
        print(f"Motor messages: {sum(len(v) for v in motors_found.values())}")
        print()
        
        if motors_found:
            print(f"Found {len(motors_found)} motor(s):")
            for motor_id in sorted(motors_found.keys()):
                count = len(motors_found[motor_id])
                print(f"  Motor {motor_id}: {count} message(s)")
                # Show first message
                if motors_found[motor_id]:
                    print(f"    Example: {motors_found[motor_id][0]['hex'][:60]}...")
        else:
            print("No motors detected in passive listening!")
        
        missing = [m for m in KNOWN_MOTORS if m not in motors_found]
        if missing:
            print(f"\nMissing motors: {missing}")
        
        if all_messages:
            print(f"\nOther messages captured: {len(all_messages)}")
            for msg in all_messages[:5]:  # Show first 5
                print(f"  {msg}")
        
        print("="*70)
        return motors_found
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        return None
    except KeyboardInterrupt:
        print("\n\nListening stopped by user")
        if 'ser' in locals():
            ser.close()
        return motors_found
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    duration = 30
    if len(sys.argv) > 2:
        duration = int(sys.argv[2])
    
    print()
    print("Make sure all 6 motors are connected and powered!")
    print(f"Starting passive listening for {duration} seconds...")
    time.sleep(2)
    print()
    
    motors = passive_listen(port, duration=duration)

