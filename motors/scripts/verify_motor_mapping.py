#!/usr/bin/env python3
"""
Verify Motor Mapping - Test which IDs control the same physical motors
This script tests IDs 8-15 to see if they all control the same motor or different motors
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

def test_motor_with_pattern(ser, can_id, num_pulses):
    """
    Move motor with a unique pattern (number of pulses)
    This helps identify which physical motor is moving
    """
    print(f"\n{'='*60}")
    print(f"Testing CAN ID {can_id} (0x{can_id:02X})")
    print(f"Pattern: {num_pulses} pulse(s)")
    print(f"{'='*60}")
    print("\nWatch the motors carefully!")
    print("Note which physical motor moves and how many times it pulses.")
    
    input("\nPress Enter to start the test...")
    
    # Activate
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    # Execute pattern (num_pulses pulses)
    for i in range(num_pulses):
        print(f"  Pulse {i+1}/{num_pulses}...")
        send_command(ser, build_move_jog_cmd(can_id, 0.08, 1))
        time.sleep(0.4)
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.3)
    
    # Deactivate
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.2)
    
    print("\nTest complete.")
    
    # Ask user which motor moved
    response = input("\nWhich physical motor moved? (Enter motor number, or 'same' if same as previous): ")
    return response.strip()

def main():
    parser = argparse.ArgumentParser(description='Verify Motor ID Mapping')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', 
                       help='Serial port (default: /dev/ttyUSB0)')
    parser.add_argument('baud', type=int, nargs='?', default=921600, 
                       help='Baud rate (default: 921600)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  Motor Mapping Verification Tool")
    print("="*70)
    print()
    print(f"Port: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print()
    print("This script will test each CAN ID with a unique movement pattern.")
    print("Watch carefully and note which physical motor moves.")
    print()
    
    # Test IDs 8-15 (found in scan)
    test_ids = [8, 9, 10, 11, 12, 13, 14, 15]
    
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
        
        # Store results
        motor_mapping = {}
        
        # Test each ID with unique pattern
        for idx, can_id in enumerate(test_ids):
            num_pulses = idx + 1  # 1 pulse for ID 8, 2 for ID 9, etc.
            
            motor_num = test_motor_with_pattern(ser, can_id, num_pulses)
            motor_mapping[can_id] = motor_num
            
            # Short break between tests
            time.sleep(0.5)
        
        # Display results
        print("\n" + "="*70)
        print("MAPPING RESULTS")
        print("="*70)
        
        # Group by physical motor
        physical_motors = {}
        for can_id, motor_num in motor_mapping.items():
            if motor_num not in physical_motors:
                physical_motors[motor_num] = []
            physical_motors[motor_num].append(can_id)
        
        print("\nPhysical Motor → CAN IDs:")
        for motor_num in sorted(physical_motors.keys()):
            ids = physical_motors[motor_num]
            print(f"  Motor {motor_num}: CAN IDs {ids}")
            if len(ids) > 1:
                print(f"    ⚠️  WARNING: Multiple IDs control the same motor!")
        
        print("\nCAN ID → Physical Motor:")
        for can_id in sorted(motor_mapping.keys()):
            motor_num = motor_mapping[can_id]
            print(f"  CAN ID {can_id:2d} (0x{can_id:02X}) → Motor {motor_num}")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        num_physical_motors = len(physical_motors)
        num_can_ids = len(motor_mapping)
        
        print(f"Physical Motors Found: {num_physical_motors}")
        print(f"CAN IDs Tested: {num_can_ids}")
        
        if num_physical_motors < num_can_ids:
            print("\n⚠️  ISSUE DETECTED:")
            print(f"   {num_can_ids} CAN IDs are controlling only {num_physical_motors} motor(s)")
            print("   Multiple IDs are mapped to the same physical motor.")
            print("\n   This means motors are NOT configured with unique CAN IDs.")
            print("   Each motor should respond to only ONE CAN ID.")
            print("\n   SOLUTION: Configure each motor with a unique CAN ID")
            print("   (requires manufacturer software or configuration commands)")
        else:
            print("\n✅ All CAN IDs control different motors!")
        
        ser.close()
        
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
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

