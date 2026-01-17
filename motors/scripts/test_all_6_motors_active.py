#!/usr/bin/env python3
"""
Actively test all 6 motors to see which respond when all are connected
Uses the message format from captured Motor Studio traffic
"""
import serial
import time
import sys
from collections import defaultdict

# Motor mappings based on captured data
MOTOR_QUERIES = {
    1: "41542007e80c0800c40000000000000d0a",   # Motor 1
    3: "41542007e81c0800c40000000000000d0a",   # Motor 3
    7: "41542007e83c0800c40000000000000d0a",   # Motor 7 (long format)
    9: "41542007e84c0800c40000000000000d0a",   # Motor 9
    11: "41540007e89c01000d0a",                 # Motor 11 (short format)
    14: "41542007e8740800c40000000000000d0a",  # Motor 14
}

def test_all_motors(port='COM6', baudrate=921600):
    """
    Test all 6 motors by querying each one
    """
    results = {}
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print("="*70)
        print("Active Motor Test - All 6 Motors")
        print("="*70)
        print(f"Port: {port}")
        print(f"Testing motors: {sorted(MOTOR_QUERIES.keys())}")
        print()
        
        # Initialize adapter
        print("Initializing adapter...")
        init_cmd = bytes.fromhex("41542b41540d0a")  # AT+AT
        ser.write(init_cmd)
        time.sleep(0.5)
        ser.read(200)  # Clear response
        print("  [OK] Adapter initialized")
        print()
        
        # Send device read command (like Motor Studio does)
        # This should trigger all motors to respond
        print("Sending device read command (triggers all motors)...")
        read_cmd = bytes.fromhex("41542b41000d0a")  # AT+A + 00 + CRLF
        ser.reset_input_buffer()
        ser.write(read_cmd)
        time.sleep(0.5)
        
        # Collect all responses for 3 seconds
        print("Collecting responses from all motors (3 seconds)...")
        print("-" * 70)
        
        all_data = bytearray()
        start_time = time.time()
        
        while time.time() - start_time < 3.0:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                all_data.extend(data)
            time.sleep(0.05)
        
        # Parse messages from collected data
        messages = []
        message_buffer = bytearray()
        
        for byte in all_data:
            message_buffer.append(byte)
            if len(message_buffer) >= 2 and message_buffer[-2] == 0x0d and message_buffer[-1] == 0x0a:
                # Complete message found
                msg_hex = message_buffer.hex()
                messages.append(msg_hex)
                message_buffer = bytearray()
        
        # Also check for any remaining data
        if len(message_buffer) > 0:
            messages.append(message_buffer.hex())
        
        # Extract motor IDs from messages
        print(f"\nFound {len(messages)} message(s)")
        print("Raw messages:")
        for i, msg in enumerate(messages, 1):
            print(f"  {i}. {msg}")
        print()
        
        # Map of known motor patterns
        motor_patterns = {
            '0c': 1,   # 41542007e80c...
            '1c': 3,   # 41542007e81c...
            '3c': 7,   # 41542007e83c...
            '4c': 9,   # 41542007e84c...
            '74': 14,  # 41542007e874...
            '7c': 7,   # 41540007e87c... (alternative format)
            '9c': 11,  # 41540007e89c...
        }
        
        seen_motors = set()
        
        for msg in messages:
            msg_lower = msg.lower()
            # Check for motor response patterns
            if '41542007e8' in msg_lower:
                # Long format
                if len(msg_lower) >= 12:
                    byte_at_pos = msg_lower[10:12]  # Byte after 07e8
                    if byte_at_pos in motor_patterns:
                        motor_id = motor_patterns[byte_at_pos]
                        seen_motors.add(motor_id)
                        if motor_id not in results:
                            results[motor_id] = {
                                'status': 'RESPONDED',
                                'response': msg,
                                'response_len': len(msg),
                                'messages': []
                            }
                        results[motor_id]['messages'].append(msg)
                        print(f"  Motor {motor_id} detected: {msg[:60]}...")
            
            elif '41540007e8' in msg_lower:
                # Short format
                if len(msg_lower) >= 12:
                    byte_at_pos = msg_lower[10:12]
                    if byte_at_pos in motor_patterns:
                        motor_id = motor_patterns[byte_at_pos]
                        seen_motors.add(motor_id)
                        if motor_id not in results:
                            results[motor_id] = {
                                'status': 'RESPONDED',
                                'response': msg,
                                'response_len': len(msg),
                                'messages': []
                            }
                        results[motor_id]['messages'].append(msg)
                        print(f"  Motor {motor_id} detected: {msg[:60]}...")
        
        # Mark motors that didn't respond
        for motor_id in MOTOR_QUERIES.keys():
            if motor_id not in seen_motors:
                results[motor_id] = {
                    'status': 'NO_RESPONSE',
                    'response': '',
                    'response_len': 0,
                    'messages': []
                }
                print(f"  Motor {motor_id}: NOT detected")
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("TEST RESULTS")
        print("="*70)
        print()
        
        responding = [mid for mid, r in results.items() if r['status'] == 'RESPONDED']
        partial = [mid for mid, r in results.items() if r['status'] == 'PARTIAL']
        not_responding = [mid for mid, r in results.items() if r['status'] == 'NO_RESPONSE']
        
        print(f"[OK] Responding: {len(responding)} motor(s)")
        if responding:
            for mid in sorted(responding):
                print(f"    Motor {mid}")
        
        if partial:
            print(f"\n[?] Partial responses: {len(partial)} motor(s)")
            for mid in sorted(partial):
                print(f"    Motor {mid}")
        
        print(f"\n[X] Not responding: {len(not_responding)} motor(s)")
        if not_responding:
            for mid in sorted(not_responding):
                print(f"    Motor {mid}")
        
        print()
        print("="*70)
        
        if len(responding) == 6:
            print("[OK] ALL 6 MOTORS RESPONDED!")
        elif len(responding) == 4:
            print(f"[WARNING] Only 4 out of 6 motors responded!")
            print(f"    Missing motors: {sorted(not_responding)}")
            print()
            print("This confirms the issue: some motors don't respond when all are connected.")
            print("This is likely a CanOPEN protocol/bus state issue, not hardware.")
        else:
            print(f"Found {len(responding)} responding motor(s)")
        
        print("="*70)
        
        return results
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        print("\nMake sure:")
        print("  - CH340 adapter is connected")
        print("  - Motor Studio is CLOSED")
        print("  - All 6 motors are powered and connected")
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
    print("IMPORTANT: Make sure all 6 motors are connected and powered!")
    print("           Close Motor Studio before running this test.")
    print()
    print("Starting test in 2 seconds...")
    time.sleep(2)
    print()
    
    results = test_all_motors(port)

