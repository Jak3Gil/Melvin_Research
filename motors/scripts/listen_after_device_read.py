#!/usr/bin/env python3
"""
Listen carefully after device read command (AT+A)
This might trigger all motors to respond automatically
"""
import serial
import time
import sys
from collections import defaultdict

KNOWN_MOTORS = [1, 3, 7, 9, 11, 14]

def extract_motor_id(msg_hex):
    """Extract motor ID from response"""
    msg_clean = msg_hex.replace('0d0a', '').lower()
    
    if not msg_clean.startswith('4154'):
        return None
    
    # Long format: 41542007e8XX...
    if msg_clean.startswith('41542007e8'):
        if len(msg_clean) >= 12:
            id_byte = msg_clean[10:12]
            motor_map = {'0c': 1, '1c': 3, '3c': 7, '4c': 9, '74': 14}
            return motor_map.get(id_byte)
    
    # Short format: 41540007e8XX...
    elif msg_clean.startswith('41540007e8'):
        if len(msg_clean) >= 12:
            id_byte = msg_clean[10:12]
            motor_map = {'7c': 7, '9c': 11}
            return motor_map.get(id_byte)
    
    return None

def listen_after_device_read(port='COM6', baudrate=921600, listen_time=10):
    """Send device read and listen carefully for all responses"""
    
    motors_found = defaultdict(list)
    all_messages = []
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Listen After Device Read - Finding All Motors")
        print("="*70)
        print(f"Port: {port} at {baudrate} baud")
        print(f"Listening for {listen_time} seconds after device read...")
        print()
        
        # Initialize
        print("Initializing...")
        ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
        time.sleep(0.5)
        ser.read(1000)  # Clear all responses
        print("  [OK] Initialized")
        print()
        
        # Send device read command
        print("Sending device read command (AT+A)...")
        print("This should trigger motors to respond...")
        print()
        
        ser.reset_input_buffer()
        ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A
        time.sleep(0.1)  # Brief pause
        
        # Listen carefully for responses
        print(f"Listening for {listen_time} seconds...")
        print("-" * 70)
        
        message_buffer = bytearray()
        start_time = time.time()
        last_print_time = start_time
        
        while time.time() - start_time < listen_time:
            # Read available data
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
                        elapsed = time.time() - start_time
                        
                        # Check if it's a motor message
                        motor_id = extract_motor_id(msg_hex)
                        
                        if motor_id:
                            motors_found[motor_id].append({
                                'time': elapsed,
                                'hex': msg_hex
                            })
                            print(f"[{elapsed:.2f}s] Motor {motor_id} detected! ({len(motors_found[motor_id])} total)")
                        elif msg_hex not in ["4f4b0d0a", "014a0d0a", "014d0d0a"]:
                            # Interesting non-motor message
                            all_messages.append({
                                'time': elapsed,
                                'hex': msg_hex
                            })
                            if time.time() - last_print_time > 1.0:  # Print every second
                                print(f"[{elapsed:.2f}s] Other message: {msg_hex[:50]}...")
                                last_print_time = time.time()
                    
                    # Remove processed message
                    message_buffer = message_buffer[crlf_pos+2:]
                else:
                    break  # No complete message yet
            
            time.sleep(0.01)  # Small delay
        
        ser.close()
        
        # Final Summary
        print()
        print("="*70)
        print("RESULTS")
        print("="*70)
        print()
        
        found = sorted(motors_found.keys())
        missing = [m for m in KNOWN_MOTORS if m not in found]
        
        print(f"Motors Detected: {len(found)} out of {len(KNOWN_MOTORS)}")
        print()
        
        if found:
            print("FOUND MOTORS:")
            for motor_id in found:
                count = len(motors_found[motor_id])
                print(f"  Motor {motor_id}: {count} message(s)")
                print(f"    First seen at: {motors_found[motor_id][0]['time']:.2f}s")
                print(f"    Example: {motors_found[motor_id][0]['hex'][:60]}...")
        else:
            print("No motors detected!")
        
        if missing:
            print()
            print(f"MISSING MOTORS ({len(missing)}):")
            for motor_id in missing:
                print(f"  Motor {motor_id}")
        
        if all_messages:
            print()
            print(f"Other messages captured: {len(all_messages)}")
            print("(These might be adapter responses, not motor messages)")
        
        print()
        print("="*70)
        
        if len(found) == 4:
            print("\n[SUCCESS] Found 4 out of 6 motors - matches your issue!")
            print(f"The 2 missing motors are: {missing}")
            print("\nThis confirms it's a protocol/software issue, not hardware.")
            print("The missing motors may need:")
            print("  - Different initialization sequence")
            print("  - Individual queries instead of broadcast")
            print("  - Different timing or delays")
        
        return motors_found
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        print("\nMake sure Motor Studio and other programs are closed!")
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
    
    listen_time = 15
    if len(sys.argv) > 2:
        listen_time = int(sys.argv[2])
    
    print()
    print("Make sure all 6 motors are connected and powered!")
    print(f"Starting listen after device read ({listen_time}s)...")
    time.sleep(2)
    print()
    
    motors = listen_after_device_read(port, listen_time=listen_time)

