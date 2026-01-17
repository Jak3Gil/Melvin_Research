#!/usr/bin/env python3
"""
Capture ALL responses without filtering - debug why motors 7, 9, 11 don't show up
Shows every byte received to see if they're responding in a different format
"""
import serial
import time
import sys
from collections import defaultdict

KNOWN_MOTORS = [1, 3, 7, 9, 11, 14]

def capture_all_responses(port='COM6', baudrate=921600):
    """Capture every single response without any filtering"""
    
    all_responses = []
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Capture ALL Responses - Raw Debug")
        print("="*70)
        print()
        
        # Initialize
        print("Initializing...")
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        print("  [OK]")
        print()
        
        # Query each motor and capture EVERYTHING
        motor_queries = {
            1: ("41542007e80c0800c40000000000000d0a", "Motor 1"),
            3: ("41542007e81c0800c40000000000000d0a", "Motor 3"),
            7: ("41542007e83c0800c40000000000000d0a", "Motor 7"),
            9: ("41542007e84c0800c40000000000000d0a", "Motor 9"),
            11: ("41540007e89c01000d0a", "Motor 11"),
            14: ("41542007e8740800c40000000000000d0a", "Motor 14"),
        }
        
        print("Querying each motor and capturing ALL responses:")
        print("="*70)
        
        for motor_id, (cmd_hex, name) in sorted(motor_queries.items()):
            print(f"\n{name} (ID {motor_id}):")
            print(f"  Command: {cmd_hex}")
            
            ser.reset_input_buffer()
            ser.write(bytes.fromhex(cmd_hex))
            time.sleep(2.0)  # Longer wait
            
            # Capture EVERYTHING
            all_data = bytearray()
            start = time.time()
            while time.time() - start < 3.0:  # 3 second collection window
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    all_data.extend(data)
                time.sleep(0.05)
            
            # Final read
            if ser.in_waiting > 0:
                all_data.extend(ser.read(ser.in_waiting))
            
            # Parse all messages
            messages = []
            msg_buf = bytearray()
            
            for byte in all_data:
                msg_buf.append(byte)
                if len(msg_buf) >= 2 and msg_buf[-2] == 0x0d and msg_buf[-1] == 0x0a:
                    messages.append(msg_buf.hex())
                    msg_buf = bytearray()
            
            if len(msg_buf) > 0:
                messages.append(msg_buf.hex())
            
            print(f"  Total bytes received: {len(all_data)}")
            print(f"  Messages parsed: {len(messages)}")
            
            if messages:
                print(f"  All responses:")
                for i, msg in enumerate(messages, 1):
                    print(f"    [{i}] {msg}")
                    
                    # Try to identify if this looks like a motor response
                    if msg.startswith('4154'):
                        if '1000' in msg and 'ec' in msg:
                            print(f"         -> Looks like motor response format (41541000XXec...)")
                        elif '2007e8' in msg:
                            print(f"         -> Looks like command/query format")
                        else:
                            print(f"         -> Unknown format")
                    
                    all_responses.append({
                        'motor': motor_id,
                        'name': name,
                        'response': msg,
                        'length': len(msg)
                    })
            else:
                print(f"  [X] NO RESPONSES CAPTURED")
                if len(all_data) > 0:
                    print(f"      Raw data (no CRLF): {all_data.hex()}")
            
            time.sleep(0.5)
        
        ser.close()
        
        # Analysis
        print("\n" + "="*70)
        print("RAW RESPONSE ANALYSIS")
        print("="*70)
        print()
        
        print(f"Total responses captured: {len(all_responses)}")
        print()
        
        # Group by motor
        print("Responses by Motor:")
        for motor_id in KNOWN_MOTORS:
            motor_responses = [r for r in all_responses if r['motor'] == motor_id]
            if motor_responses:
                print(f"  Motor {motor_id:2d}: {len(motor_responses)} response(s)")
                for resp in motor_responses:
                    print(f"    -> {resp['response'][:80]}...")
            else:
                print(f"  Motor {motor_id:2d}: NO RESPONSES")
        
        # Look for patterns
        print("\nResponse Pattern Analysis:")
        response_formats = defaultdict(list)
        for resp in all_responses:
            msg = resp['response']
            if msg.startswith('4154'):
                # Extract format pattern
                if len(msg) >= 12:
                    pattern = msg[:12]  # First 6 bytes as pattern
                    response_formats[pattern].append(resp)
        
        print(f"  Unique response formats: {len(response_formats)}")
        for pattern, responses in sorted(response_formats.items()):
            motors = [r['motor'] for r in responses]
            print(f"    Pattern {pattern}: Motors {sorted(set(motors))} ({len(responses)} response(s))")
        
        # Compare working vs non-working
        print("\nWorking vs Non-Working Motor Comparison:")
        working = [1, 3, 14]
        non_working = [7, 9, 11]
        
        working_responses = [r for r in all_responses if r['motor'] in working]
        non_working_responses = [r for r in all_responses if r['motor'] in non_working]
        
        print(f"  Working motors ({working}): {len(working_responses)} response(s)")
        if working_responses:
            print(f"    Format: {working_responses[0]['response'][:20]}...")
        
        print(f"  Non-working motors ({non_working}): {len(non_working_responses)} response(s)")
        if non_working_responses:
            print(f"    Format: {non_working_responses[0]['response'][:20]}...")
        else:
            print(f"    -> NO RESPONSES - motors may be:")
            print(f"       - Not powered")
            print(f"       - Not responding to these commands")
            print(f"       - Responding in format we're not capturing")
            print(f"       - Need different initialization")
        
        print()
        print("="*70)
        
        return all_responses
        
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
    print("Capturing ALL responses without filtering...")
    print("This will show if motors 7, 9, 11 are responding differently")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    responses = capture_all_responses(port)

