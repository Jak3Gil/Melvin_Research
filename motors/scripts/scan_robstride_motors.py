#!/usr/bin/env python3
"""
Scan for Robstride Motors using L91 Protocol over USB-to-CAN
Based on: https://github.com/Jak3Gil/Melvin_november

Usage:
    python scan_robstride_motors.py [COM_PORT] [BAUD_RATE]
    
Example:
    python scan_robstride_motors.py COM3 921600
"""

import serial
import sys
import time
import argparse

# L91 Protocol Constants
L91_DETECT_CMD = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])  # AT+AT\r\n

# Motor activation command format: AT 00 07 e8 <can_id> 01 00 0d 0a
def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

# Motor deactivate command format: AT 00 07 e8 <can_id> 00 00 0d 0a
def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

# Load parameters command: AT 20 07 e8 <can_id> 08 00 c4 00 00 00 00 00 00 0d 0a
def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

# Move jog command: AT 90 07 e8 <can_id> 08 05 70 00 00 07 <flag> <speed_bytes> 0d 0a
def build_move_jog_cmd(can_id, speed=0.0, flag=1):
    speed_val = int(0x7fff + (speed * 3283.0)) if speed != 0.0 else 0x7fff
    if speed > 0.0:
        speed_val = int(0x8000 + (speed * 3283.0))
    elif speed < 0.0:
        speed_val = int(0x7fff + (speed * 3283.0))
    else:
        speed_val = 0x7fff
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, flag])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd, description="Command", show_response=True):
    """Send L91 command and read response"""
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.15)  # Wait 150ms for response
        
        # Try to read response (non-blocking)
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:  # 250ms timeout
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        
        if response and show_response:
            print(f"  Response: {response.hex(' ')}")
        return response
    except Exception as e:
        if show_response:
            print(f"  Error: {e}")
        return b""

def detect_motors(ser):
    """Send AT+AT command to detect motors"""
    print("\n" + "="*50)
    print("Step 1: Detecting motors (AT+AT command)")
    print("="*50)
    
    print("Sending: AT+AT\\r\\n")
    print(f"  Hex: {L91_DETECT_CMD.hex(' ')}")
    
    response = send_command(ser, L91_DETECT_CMD, "Detect")
    if response:
        print("[OK] Detection command sent")
        time.sleep(0.5)
        return True
    else:
        print("[FAIL] Detection command failed")
        return False

def scan_motor_ids(ser, motor_ids):
    """Scan specific motor IDs to see which respond"""
    print("\n" + "="*50)
    print("Step 2: Scanning Motor IDs")
    print("="*50)
    print("Note: Motors are only marked as found if they respond")
    print("="*50)
    
    found_motors = []
    
    for can_id in motor_ids:
        print(f"\nTesting Motor ID 0x{can_id:02X} ({can_id})...")
        
        # Try to activate
        print(f"  Sending activate command...")
        cmd = build_activate_cmd(can_id)
        print(f"  Hex: {cmd.hex(' ')}")
        
        response = send_command(ser, cmd)
        time.sleep(0.2)
        
        # Check if we got a response (motors that exist respond with data)
        # Responses typically start with "AT" (0x41 0x54) or contain data
        has_response = len(response) > 4  # Real responses are longer than just ACK
        
        if has_response:
            # Try to load params to confirm motor is active
            print(f"  Sending load params command...")
            cmd = build_load_params_cmd(can_id)
            response2 = send_command(ser, cmd)
            time.sleep(0.2)
            
            # Check if we got a response to load params too
            has_response2 = len(response2) > 4
            
            # Deactivate to be safe
            cmd = build_deactivate_cmd(can_id)
            send_command(ser, cmd, show_response=False)
            time.sleep(0.1)
            
            if has_response2:
                print(f"  [OK] Motor ID 0x{can_id:02X} RESPONDED (found!)")
                found_motors.append(can_id)
            else:
                print(f"  [MAYBE] Motor ID 0x{can_id:02X} activated but no params response")
        else:
            print(f"  [NO RESPONSE] Motor ID 0x{can_id:02X} did not respond")
    
    return found_motors

def test_motor_movement(ser, can_id):
    """Test a motor with small movement"""
    print(f"\n" + "="*50)
    print(f"Step 3: Testing Motor ID 0x{can_id:02X} movement")
    print("="*50)
    
    print("[WARNING] Motor will move! Watch carefully!")
    input("Press Enter to continue...")
    
    # Activate
    print(f"\nActivating motor 0x{can_id:02X}...")
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.3)
    
    # Load params
    print("Loading parameters...")
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.3)
    
    # Small forward movement
    print("\nMoving forward (small speed = 0.05)...")
    send_command(ser, build_move_jog_cmd(can_id, 0.05, 1))
    time.sleep(2)
    
    # Stop
    print("Stopping...")
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
    time.sleep(0.5)
    
    # Small backward movement
    print("\nMoving backward (small speed = -0.05)...")
    send_command(ser, build_move_jog_cmd(can_id, -0.05, 1))
    time.sleep(2)
    
    # Stop
    print("Stopping...")
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
    time.sleep(0.5)
    
    # Deactivate
    print("\nDeactivating motor...")
    send_command(ser, build_deactivate_cmd(can_id))
    
    response = input("\nDid you see the motor move? (y/n): ")
    return response.lower() == 'y'

def main():
    parser = argparse.ArgumentParser(description='Scan for Robstride Motors using L91 Protocol')
    parser.add_argument('port', nargs='?', default='COM3', help='Serial port (default: COM3)')
    parser.add_argument('baud', type=int, nargs='?', default=921600, help='Baud rate (default: 921600)')
    parser.add_argument('--scan-all', action='store_true', help='Scan all possible motor IDs (1-14)')
    parser.add_argument('--test', type=int, metavar='CAN_ID', help='Test specific motor ID (e.g., 12 for 0x0C)')
    
    args = parser.parse_args()
    
    print("=======================================================")
    print("  Robstride Motor Scanner (L91 Protocol)")
    print("  Based on: https://github.com/Jak3Gil/Melvin_november")
    print("=======================================================")
    print()
    print(f"Port: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print()
    
    # Common Robstride motor IDs to check
    default_motor_ids = [0x0C, 0x0D, 0x0E]  # Motors 12, 13, 14
    
    if args.scan_all:
        motor_ids = list(range(1, 16))  # Scan IDs 1-15
    elif args.test:
        motor_ids = [args.test]
    else:
        motor_ids = default_motor_ids
    
    try:
        # Open serial port
        print(f"Opening serial port {args.port} at {args.baud} baud...")
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            write_timeout=1.0
        )
        time.sleep(0.5)  # Wait for port to stabilize
        print("[OK] Serial port opened\n")
        
        # Detect motors
        detect_motors(ser)
        time.sleep(0.5)
        
        # Scan motor IDs
        found_motors = scan_motor_ids(ser, motor_ids)
        
        print("\n" + "="*50)
        print("Scan Results")
        print("="*50)
        if found_motors:
            print(f"\n[OK] Found {len(found_motors)} motor(s):")
            for can_id in found_motors:
                print(f"  - Motor ID 0x{can_id:02X} ({can_id})")
            
            if not args.test:
                print("\nTo test a motor, run:")
                for can_id in found_motors:
                    print(f"  python scan_robstride_motors.py {args.port} {args.baud} --test {can_id}")
        else:
            print("\n[FAIL] No motors found")
            print("\nTroubleshooting:")
            print("  1. Check USB-to-CAN adapter is connected")
            print("  2. Verify motors are powered on")
            print("  3. Check CAN bus connections (CAN-H, CAN-L)")
            print("  4. Verify baud rate (try 115200 if 921600 doesn't work)")
        
        # Test specific motor if requested
        if args.test:
            if args.test in found_motors or args.test in motor_ids:
                test_motor_movement(ser, args.test)
            else:
                print(f"\n[WARNING] Motor ID 0x{args.test:02X} was not found in scan")
        
        ser.close()
        print("\n[OK] Scan complete")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        print(f"\nMake sure:")
        print(f"  1. Port {args.port} exists")
        print(f"  2. No other program is using the port")
        print(f"  3. Drivers are installed (CH340/CP2102)")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if 'ser' in locals():
            ser.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

