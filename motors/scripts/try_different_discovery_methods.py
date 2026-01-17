#!/usr/bin/env python3
"""
Try different discovery methods Motor Studio might use
Since motors 7, 9, 11 send ZERO bytes, they may need:
- Broadcast discovery queries
- Different command format
- Activation/enable first
- Different timing
"""
import serial
import time
import sys

def try_discovery_methods(port='COM6', baudrate=921600):
    """Try every possible discovery method"""
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Trying Different Discovery Methods for Motors 7, 9, 11")
        print("="*70)
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        # Method 1: Broadcast query (maybe Motor Studio queries all at once)
        print("METHOD 1: Broadcast query to all motors")
        print("-" * 70)
        
        # Try sending all queries rapidly
        motor_queries = {
            7: bytes.fromhex("41542007e83c0800c40000000000000d0a"),
            9: bytes.fromhex("41542007e84c0800c40000000000000d0a"),
            11: bytes.fromhex("41540007e89c01000d0a"),
        }
        
        print("Sending queries to motors 7, 9, 11 in rapid succession...")
        ser.reset_input_buffer()
        
        for motor_id, cmd in motor_queries.items():
            ser.write(cmd)
            time.sleep(0.1)  # Very short delay
        
        # Collect all responses
        time.sleep(2.0)
        responses = bytearray()
        start = time.time()
        while time.time() - start < 3.0:
            if ser.in_waiting > 0:
                responses.extend(ser.read(ser.in_waiting))
            time.sleep(0.1)
        
        if len(responses) > 0:
            print(f"  Got {len(responses)} bytes: {responses.hex()[:80]}...")
        else:
            print(f"  [X] No responses")
        print()
        
        # Method 2: Try activating motors 7, 9, 11 first, then query
        print("METHOD 2: Activate motors 7, 9, 11 first, then query")
        print("-" * 70)
        
        # Activate command: AT 00 07 e8 <byte> 01 00
        activate_bytes = {7: 0x3c, 9: 0x4c, 11: 0x9c}
        
        for motor_id, byte_val in activate_bytes.items():
            print(f"Activating Motor {motor_id}...")
            activate_cmd = bytearray([0x41, 0x54, 0x20, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
            ser.write(bytes(activate_cmd))
            time.sleep(0.5)
            ser.read(200)
        
        time.sleep(1.0)
        
        # Now query them
        for motor_id, cmd in motor_queries.items():
            print(f"Querying Motor {motor_id} after activation...")
            ser.reset_input_buffer()
            ser.write(cmd)
            time.sleep(1.5)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 0:
                print(f"  [OK] Got response: {response.hex()[:60]}...")
            else:
                print(f"  [X] No response")
        
        print()
        
        # Method 3: Try querying working motors first, then missing ones
        print("METHOD 3: Query working motors (1,3,14) first, then missing (7,9,11)")
        print("-" * 70)
        
        working_queries = {
            1: bytes.fromhex("41542007e80c0800c40000000000000d0a"),
            3: bytes.fromhex("41542007e81c0800c40000000000000d0a"),
            14: bytes.fromhex("41542007e8740800c40000000000000d0a"),
        }
        
        print("Querying working motors first...")
        for motor_id, cmd in working_queries.items():
            ser.reset_input_buffer()
            ser.write(cmd)
            time.sleep(0.5)
            ser.read(200)
        
        time.sleep(1.0)
        print("Now querying missing motors...")
        
        for motor_id, cmd in motor_queries.items():
            print(f"Querying Motor {motor_id}...")
            ser.reset_input_buffer()
            ser.write(cmd)
            time.sleep(1.5)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.5:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 0:
                print(f"  [OK] Got response: {response.hex()[:60]}...")
            else:
                print(f"  [X] No response")
        
        print()
        
        # Method 4: Try CanOPEN node guarding/heartbeat for motors 7, 9, 11
        print("METHOD 4: CanOPEN Node Guarding for motors 7, 9, 11")
        print("-" * 70)
        
        # CanOPEN Node Guard Request: COB-ID = 0x700 + node_id
        for motor_id in [7, 9, 11]:
            node_guard_id = 0x700 + motor_id
            # Format: AT + command + CAN ID
            guard_cmd = bytearray([0x41, 0x54, 0x20])
            guard_cmd.extend([(node_guard_id >> 8) & 0xFF, node_guard_id & 0xFF])
            guard_cmd.extend([0x00, 0x0d, 0x0a])
            
            print(f"Node Guard request for Motor {motor_id} (COB-ID 0x{node_guard_id:03X})...")
            ser.reset_input_buffer()
            ser.write(bytes(guard_cmd))
            time.sleep(1.0)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 0:
                print(f"  [OK] Got response: {response.hex()[:60]}...")
            else:
                print(f"  [X] No response")
        
        ser.close()
        
        print()
        print("="*70)
        print("If none of these methods found motors 7, 9, 11:")
        print("  - They may not be powered")
        print("  - They may need different command format")
        print("  - Motor Studio may use a proprietary discovery protocol")
        print("  - They may respond only to specific broadcast messages")
        print("="*70)
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print()
    print("Trying different discovery methods for motors 7, 9, 11...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    try_discovery_methods(port)

