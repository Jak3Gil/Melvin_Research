#!/usr/bin/env python3
"""
Find all 6 motors using the correct L91 command format
Based on L91_MOTOR_SETUP.md: AT <space> <command> e8 <can_id> <data> CRLF
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

def build_l91_command(command_bytes, can_id_byte, data_bytes):
    """
    Build L91 command: AT <space> <command> e8 <can_id_byte> <data> CRLF
    Format: 41 54 20 <cmd_bytes> e8 <can_id> <data> 0d 0a
    """
    cmd = bytearray([0x41, 0x54, 0x20])  # AT + space
    cmd.extend(command_bytes)              # Command bytes (e.g., 00 07)
    cmd.append(0xe8)                       # e8
    cmd.append(can_id_byte)                # CAN ID byte (the motor-specific byte)
    cmd.extend(data_bytes)                 # Data
    cmd.extend([0x0d, 0x0a])               # CRLF
    return bytes(cmd)

def find_all_motors_l91(port='COM6', baudrate=921600):
    """Find all motors using L91 format"""
    
    motors_found = defaultdict(list)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        print("="*70)
        print("Finding All 6 Motors - L91 Format")
        print("="*70)
        print(f"Port: {port} at {baudrate} baud")
        print()
        
        # Initialize
        print("Step 1: Initialize adapter...")
        ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
        time.sleep(0.5)
        ser.read(200)
        print("  [OK]")
        print()
        
        # Send device read
        print("Step 2: Send device read...")
        ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A
        time.sleep(0.5)
        ser.read(200)
        print("  [OK]")
        print()
        
        # Motor byte mappings from captured data
        motor_byte_map = {
            1: 0x0c,
            3: 0x1c,
            7: 0x3c,
            9: 0x4c,
            11: 0x9c,  # Uses short format
            14: 0x74
        }
        
        # Try different L91 commands for each motor
        print("Step 3: Testing motors with L91 commands...")
        print("-" * 70)
        
        # Command 1: Activate (AT 00 07 e8 <can_id> 01 00)
        print("\n  Command: Activate Motor")
        for motor_id in KNOWN_MOTORS:
            can_id_byte = motor_byte_map.get(motor_id)
            if can_id_byte is None:
                continue
            
            # Long format: AT 20 07 e8 <byte> 08 00 c4...
            # Short format: AT 00 07 e8 <byte> 01 00
            if motor_id in [11]:  # Short format
                cmd = build_l91_command([0x00, 0x07], can_id_byte, [0x01, 0x00])
            else:  # Long format  
                cmd = build_l91_command([0x00, 0x07], can_id_byte, [0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00])
            
            ser.reset_input_buffer()
            ser.write(cmd)
            time.sleep(0.4)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 0.8:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.05)
            
            if len(response) > 4:
                resp_hex = response.hex()
                detected_id = extract_motor_id(resp_hex)
                if detected_id == motor_id:
                    motors_found[motor_id].append(resp_hex)
                    print(f"    Motor {motor_id}: [OK] Responded!")
                elif detected_id:
                    print(f"    Motor {motor_id}: [?] Got Motor {detected_id} instead")
                else:
                    print(f"    Motor {motor_id}: [?] Response: {resp_hex[:40]}...")
        
        # Command 2: Load Parameters (AT 20 07 e8 <can_id> 08 00 c4...)
        print("\n  Command: Load Parameters")
        for motor_id in KNOWN_MOTORS:
            can_id_byte = motor_byte_map.get(motor_id)
            if can_id_byte is None:
                continue
            
            # Use the exact format from captured messages
            if motor_id == 11:
                # Short format
                cmd = bytes.fromhex("41540007e89c01000d0a")
            else:
                # Long format: AT 20 07 e8 <byte> 08 00 c4 00 00 00 00 00
                cmd = build_l91_command([0x20, 0x07], can_id_byte, [0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00])
            
            ser.reset_input_buffer()
            ser.write(cmd)
            time.sleep(0.4)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 0.8:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.05)
            
            if len(response) > 4:
                resp_hex = response.hex()
                detected_id = extract_motor_id(resp_hex)
                if detected_id == motor_id:
                    motors_found[motor_id].append(resp_hex)
                    print(f"    Motor {motor_id}: [OK] Responded!")
                elif detected_id:
                    print(f"    Motor {motor_id}: [?] Got Motor {detected_id} instead")
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("RESULTS")
        print("="*70)
        print()
        
        found = sorted(motors_found.keys())
        missing = [m for m in KNOWN_MOTORS if m not in found]
        
        print(f"Found: {len(found)} out of {len(KNOWN_MOTORS)} motors")
        print()
        
        if found:
            print("DETECTED MOTORS:")
            for motor_id in found:
                count = len(motors_found[motor_id])
                print(f"  Motor {motor_id}: {count} response(s)")
        
        if missing:
            print()
            print("MISSING MOTORS:")
            for motor_id in missing:
                print(f"  Motor {motor_id}")
        
        print()
        print("="*70)
        
        if len(found) == 4:
            print("\n[DIAGNOSIS] Found 4 out of 6 - matches your issue!")
            print(f"Missing: {missing}")
            print("\nThe 2 missing motors may need:")
            print("  - Different command format")
            print("  - Individual initialization")
            print("  - Different CAN ID encoding")
        
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
    
    print()
    print("Finding all 6 motors using correct L91 format...")
    print("Starting in 2 seconds...")
    time.sleep(2)
    print()
    
    motors = find_all_motors_l91(port)

