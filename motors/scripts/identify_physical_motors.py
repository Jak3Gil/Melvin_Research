#!/usr/bin/env python3
"""
Identify Physical Motors by Testing Representative IDs
Tests specific IDs from each range to determine which physical motor they control
"""

import serial
import sys
import time
import argparse

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

def send_command(ser, cmd):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.05)
        return True
    except:
        return False

def test_motor_with_pattern(ser, can_id, num_pulses, speed=0.08):
    """
    Move motor with a unique pattern (number of pulses)
    Returns True if test completed
    """
    # Activate
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    # Execute pattern
    for i in range(num_pulses):
        send_command(ser, build_move_jog_cmd(can_id, speed, 1))
        time.sleep(0.4)
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.3)
    
    # Deactivate
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.2)
    return True

def main():
    parser = argparse.ArgumentParser(description='Identify Physical Motors')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', 
                       help='Serial port (default: /dev/ttyUSB0)')
    parser.add_argument('baud', type=int, nargs='?', default=921600, 
                       help='Baud rate (default: 921600)')
    parser.add_argument('--auto', action='store_true',
                       help='Auto-test all representative IDs')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  Physical Motor Identification Tool")
    print("="*70)
    print()
    print(f"Port: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print()
    
    # Define test IDs based on scan results
    # Testing one ID from each suspected motor range
    test_groups = [
        {
            'name': 'Group 1 (IDs 8-15)',
            'test_ids': [8, 9, 10, 11, 12, 13, 14, 15],
            'description': 'Testing if IDs 8-15 control same motor or different motors'
        },
        {
            'name': 'Group 2 (IDs 16-20)',
            'test_ids': [16, 17, 18, 19, 20],
            'description': 'Testing IDs 16-20'
        },
        {
            'name': 'Group 3 (IDs 21-30)',
            'test_ids': [21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
            'description': 'Motor 3 range (per your info)'
        },
        {
            'name': 'Group 4 (IDs 31-39)',
            'test_ids': [31, 32, 33, 34, 35, 36, 37, 38, 39],
            'description': 'Testing IDs 31-39'
        },
        {
            'name': 'Group 5 (IDs 64-71)',
            'test_ids': [64, 65, 66, 67, 68, 69, 70, 71],
            'description': 'Motor 8 at ID 64 (per your info)'
        },
        {
            'name': 'Group 6 (IDs 72-79)',
            'test_ids': [72, 73, 74, 75, 76, 77, 78, 79],
            'description': 'Motor 9 at ID 73 (per your info)'
        }
    ]
    
    try:
        # Open serial port
        print(f"Opening serial port {args.port}...")
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
        
        # Send detection command
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        ser.flush()
        time.sleep(0.5)
        
        motor_mapping = {}
        
        print("="*70)
        print("INSTRUCTIONS")
        print("="*70)
        print("Watch your motors carefully!")
        print("For each test, note:")
        print("  1. Which physical motor moved")
        print("  2. How many pulses (movements) you saw")
        print()
        print("The number of pulses helps identify which ID is being tested.")
        print("="*70)
        print()
        
        if not args.auto:
            input("Press Enter to start testing...")
        
        # Test each group
        for group_idx, group in enumerate(test_groups):
            print(f"\n{'='*70}")
            print(f"{group['name']}")
            print(f"{group['description']}")
            print(f"{'='*70}")
            
            # Test first ID from group with unique pattern
            first_id = group['test_ids'][0]
            num_pulses = group_idx + 1
            
            print(f"\nTesting CAN ID {first_id} (0x{first_id:02X}) with {num_pulses} pulse(s)...")
            print("Watch which motor moves!")
            
            if not args.auto:
                input("Press Enter to test...")
            
            test_motor_with_pattern(ser, first_id, num_pulses)
            
            print(f"\nTest complete for ID {first_id}")
            
            # Ask which motor moved
            motor_num = input(f"Which physical motor moved? (enter motor number, or 'skip'): ").strip()
            
            if motor_num.lower() != 'skip':
                motor_mapping[first_id] = motor_num
                
                # Ask if user wants to test other IDs in this group
                test_more = input(f"Test other IDs in this group ({len(group['test_ids'])-1} more)? (y/n): ").strip().lower()
                
                if test_more == 'y':
                    for test_id in group['test_ids'][1:]:
                        print(f"\nTesting CAN ID {test_id} (0x{test_id:02X}) with 2 pulses...")
                        input("Press Enter to test...")
                        
                        test_motor_with_pattern(ser, test_id, 2)
                        
                        response = input(f"Same motor as ID {first_id}? (y/n/motor_number): ").strip()
                        
                        if response.lower() == 'y':
                            motor_mapping[test_id] = motor_num
                        elif response.lower() != 'n':
                            motor_mapping[test_id] = response
            
            time.sleep(0.5)
        
        # Display results
        print("\n" + "="*70)
        print("MAPPING RESULTS")
        print("="*70)
        
        if motor_mapping:
            # Group by physical motor
            physical_motors = {}
            for can_id, motor_num in motor_mapping.items():
                if motor_num not in physical_motors:
                    physical_motors[motor_num] = []
                physical_motors[motor_num].append(can_id)
            
            print("\nPhysical Motor → CAN IDs:")
            for motor_num in sorted(physical_motors.keys(), key=lambda x: (x.isdigit(), int(x) if x.isdigit() else 0)):
                ids = sorted(physical_motors[motor_num])
                print(f"\n  Motor {motor_num}:")
                print(f"    CAN IDs: {ids}")
                
                # Determine range
                if len(ids) > 1:
                    ranges = []
                    start = ids[0]
                    end = ids[0]
                    for i in range(1, len(ids)):
                        if ids[i] == end + 1:
                            end = ids[i]
                        else:
                            ranges.append((start, end))
                            start = ids[i]
                            end = ids[i]
                    ranges.append((start, end))
                    
                    print(f"    Ranges: ", end='')
                    range_strs = []
                    for start, end in ranges:
                        if start == end:
                            range_strs.append(f"{start}")
                        else:
                            range_strs.append(f"{start}-{end}")
                    print(", ".join(range_strs))
            
            # Summary
            print("\n" + "="*70)
            print("SUMMARY")
            print("="*70)
            print(f"Physical Motors Identified: {len(physical_motors)}")
            print(f"CAN IDs Tested: {len(motor_mapping)}")
            
            print("\n⚠️  Multiple CAN IDs per motor detected!")
            print("Each motor should have only ONE unique CAN ID.")
            print("\nTo fix this, motors need to be reconfigured with unique IDs.")
        else:
            print("\nNo mapping data collected.")
        
        ser.close()
        print("\n[OK] Identification complete")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
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

