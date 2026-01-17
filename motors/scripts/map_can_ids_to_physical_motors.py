#!/usr/bin/env python3
"""
Map CAN IDs to Physical Motors
Tests each CAN ID individually to determine which physical motors they control.

Usage:
    python3 map_can_ids_to_physical_motors.py [PORT] [BAUD]
    python3 map_can_ids_to_physical_motors.py /dev/ttyUSB0 921600
"""

import serial
import sys
import time
import argparse

# L91 Protocol Constants
def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0, flag=1):
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = int(0x8000 + (speed * 3283.0))
    else:
        speed_val = int(0x7fff + (speed * 3283.0))
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, flag])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd, description="Command", show_response=False):
    """Send L91 command and read response"""
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.15)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:
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

def test_motor_movement(ser, can_id):
    """Test a motor with small movement and return True if motor responded"""
    # Activate
    response1 = send_command(ser, build_activate_cmd(can_id), show_response=False)
    time.sleep(0.2)
    
    # Load params
    response2 = send_command(ser, build_load_params_cmd(can_id), show_response=False)
    time.sleep(0.2)
    
    # Check if we got responses (motors that exist respond)
    has_response = len(response1) > 4 and len(response2) > 4
    
    if not has_response:
        return False
    
    # Small forward movement
    send_command(ser, build_move_jog_cmd(can_id, 0.1, 1), show_response=False)
    time.sleep(1.0)
    
    # Stop
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0), show_response=False)
    time.sleep(0.5)
    
    # Small backward movement
    send_command(ser, build_move_jog_cmd(can_id, -0.1, 1), show_response=False)
    time.sleep(1.0)
    
    # Stop
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0), show_response=False)
    time.sleep(0.5)
    
    # Deactivate
    send_command(ser, build_deactivate_cmd(can_id), show_response=False)
    time.sleep(0.2)
    
    return True

def map_can_ids_to_motors(ser, can_ids):
    """Map each CAN ID to physical motors"""
    print("\n" + "="*70)
    print("CAN ID to Physical Motor Mapping")
    print("="*70)
    print("\nFor each CAN ID, watch carefully which physical motor(s) move.")
    print("If multiple motors move, note all of them.")
    print("\nEach test will:")
    print("  1. Move forward for 1 second")
    print("  2. Stop")
    print("  3. Move backward for 1 second")
    print("  4. Stop")
    print("\n" + "-"*70)
    
    mapping = {}  # {can_id: [list of physical motor numbers]}
    
    for can_id in can_ids:
        print(f"\n{'='*70}")
        print(f"Testing CAN ID 0x{can_id:02X} ({can_id})")
        print(f"{'='*70}")
        
        input(f"\nPress Enter to test CAN ID {can_id} (watch which motor moves)...")
        
        # Test the motor
        has_response = test_motor_movement(ser, can_id)
        
        if not has_response:
            print(f"[NO RESPONSE] CAN ID {can_id} did not respond")
            mapping[can_id] = []
            continue
        
        print(f"\nCAN ID {can_id} responded and moved.")
        print("\nWhich physical motor(s) moved?")
        print("(Enter physical motor number, e.g., '1' for Motor 1)")
        print("(If multiple motors moved, enter numbers separated by commas, e.g., '1,2')")
        print("(If unsure which motor, enter '?' to skip)")
        
        response = input("Physical motor(s): ").strip()
        
        if response.lower() == '?':
            print(f"[SKIPPED] CAN ID {can_id} - motor identification skipped")
            mapping[can_id] = []
        else:
            try:
                motor_nums = [int(x.strip()) for x in response.split(',') if x.strip()]
                if motor_nums:
                    mapping[can_id] = motor_nums
                    print(f"[OK] CAN ID {can_id} controls physical motor(s): {motor_nums}")
                else:
                    mapping[can_id] = []
                    print(f"[SKIPPED] No motors entered for CAN ID {can_id}")
            except ValueError:
                print(f"[ERROR] Invalid input for CAN ID {can_id}")
                mapping[can_id] = []
        
        time.sleep(0.5)
    
    return mapping

def main():
    parser = argparse.ArgumentParser(description='Map CAN IDs to Physical Motors')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', help='Serial port (default: /dev/ttyUSB0)')
    parser.add_argument('baud', type=int, nargs='?', default=921600, help='Baud rate (default: 921600)')
    parser.add_argument('--ids', type=str, help='Comma-separated list of CAN IDs to test (e.g., 8,9,10,11,12,13,14,15)')
    
    args = parser.parse_args()
    
    # Parse CAN IDs
    if args.ids:
        try:
            can_ids = [int(x.strip()) for x in args.ids.split(',')]
        except ValueError:
            print("[ERROR] Invalid CAN IDs format. Use comma-separated numbers (e.g., 8,9,10)")
            sys.exit(1)
    else:
        # Default: test IDs 8-15 (the ones that responded in scan)
        can_ids = list(range(8, 16))
    
    print("="*70)
    print("CAN ID to Physical Motor Mapper")
    print("="*70)
    print(f"\nPort: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print(f"Testing CAN IDs: {can_ids}")
    print()
    
    try:
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
        time.sleep(0.5)
        print("[OK] Serial port opened\n")
        
        # Map CAN IDs to physical motors
        mapping = map_can_ids_to_motors(ser, can_ids)
        
        # Print summary
        print("\n" + "="*70)
        print("MAPPING SUMMARY")
        print("="*70)
        
        # Group by physical motor
        motor_to_can_ids = {}
        for can_id, motors in mapping.items():
            for motor in motors:
                if motor not in motor_to_can_ids:
                    motor_to_can_ids[motor] = []
                motor_to_can_ids[motor].append(can_id)
        
        print("\nBy Physical Motor:")
        print("-"*70)
        if motor_to_can_ids:
            for motor in sorted(motor_to_can_ids.keys()):
                can_id_list = sorted(motor_to_can_ids[motor])
                print(f"  Physical Motor {motor}: CAN IDs {can_id_list} (0x{[f'{x:02X}' for x in can_id_list]})")
        else:
            print("  No motors mapped")
        
        print("\nBy CAN ID:")
        print("-"*70)
        for can_id in sorted(mapping.keys()):
            motors = mapping[can_id]
            if motors:
                print(f"  CAN ID 0x{can_id:02X} ({can_id:2d}): Physical Motor(s) {motors}")
            else:
                print(f"  CAN ID 0x{can_id:02X} ({can_id:2d}): No motor mapped")
        
        # Find unique physical motors
        unique_motors = sorted(set([m for motors in mapping.values() for m in motors]))
        print(f"\nTotal unique physical motors found: {len(unique_motors)}")
        if unique_motors:
            print(f"Physical motors: {unique_motors}")
        
        ser.close()
        print("\n[OK] Mapping complete")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        print(f"\nMake sure:")
        print(f"  1. Port {args.port} exists")
        print(f"  2. No other program is using the port")
        print(f"  3. You have permission to access the port (check groups/dialout)")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if 'ser' in locals():
            ser.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

