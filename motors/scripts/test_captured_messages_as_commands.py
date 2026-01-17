#!/usr/bin/env python3
"""
Test if the captured messages from the user are commands we should send
Try sending them back to see if motors respond
"""
import serial
import time
import sys

# Your captured messages - try sending them as commands
CAPTURED_MESSAGES = {
    1: "41542007e80c0800c40000000000000d0a",
    3: "41542007e81c0800c40000000000000d0a",
    7: "41542007e83c0800c40000000000000d0a",
    9: "41542007e84c0800c40000000000000d0a",
    11: "41540007e89c01000d0a",
    14: "41542007e8740800c40000000000000d0a",
}

def test_captured_as_commands(port='COM6', baudrate=921600):
    """Test sending captured messages as commands"""
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print("="*70)
        print("Testing Captured Messages as Commands")
        print("="*70)
        print(f"Port: {port} at {baudrate} baud")
        print()
        
        # Initialize
        print("Initializing adapter...")
        init_cmd = bytes.fromhex("41542b41540d0a")
        ser.write(init_cmd)
        time.sleep(0.5)
        ser.read(200)
        print("  [OK] Initialized")
        print()
        
        # Send device read (like Motor Studio does)
        print("Sending device read (AT+A)...")
        read_cmd = bytes.fromhex("41542b41000d0a")
        ser.write(read_cmd)
        time.sleep(0.5)
        ser.read(200)
        print("  [OK] Device read sent")
        print()
        
        # Try sending each captured message as a command
        print("Testing captured messages as commands:")
        print("-" * 70)
        
        for motor_id in sorted(CAPTURED_MESSAGES.keys()):
            msg_hex = CAPTURED_MESSAGES[motor_id]
            cmd_bytes = bytes.fromhex(msg_hex)
            
            print(f"\nMotor {motor_id}:")
            print(f"  Sending: {msg_hex[:60]}...")
            
            ser.reset_input_buffer()
            ser.write(cmd_bytes)
            
            # Collect responses for 1 second
            responses = bytearray()
            start_time = time.time()
            while time.time() - start_time < 1.0:
                if ser.in_waiting > 0:
                    responses.extend(ser.read(ser.in_waiting))
                time.sleep(0.05)
            
            if len(responses) > 0:
                response_hex = responses.hex()
                print(f"  Response ({len(responses)} bytes): {response_hex[:80]}...")
                
                # Check if we got a motor response
                if len(response_hex) > 20 and response_hex != "4f4b0d0a":
                    print(f"  [OK] Got response from Motor {motor_id}!")
                else:
                    print(f"  [INFO] Got short response (might be ACK)")
            else:
                print(f"  [X] No response")
            
            time.sleep(0.3)
        
        ser.close()
        
        print()
        print("="*70)
        print("TEST COMPLETE")
        print("="*70)
        
        return True
        
    except serial.SerialException as e:
        print(f"[X] Cannot open {port}: {e}")
        print("\nMake sure:")
        print("  - Port is not in use by another program")
        print("  - Motor Studio is closed")
        print("  - All motors are connected")
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
    print("Testing if captured messages are commands we should send...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    test_captured_as_commands(port)

