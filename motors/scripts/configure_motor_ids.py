#!/usr/bin/env python3
"""
Motor ID Configuration Tool
Configure RobStride motor CAN IDs without Motor Studio
"""
import sys
sys.path.insert(0, '/home/melvin')

from jetson_motor_interface import JetsonMotorController
import serial
import time

def send_id_change_command(ser, old_id, new_id):
    """
    Attempt to change motor CAN ID
    
    This tries several known command formats for RobStride motors
    """
    print(f"\nAttempting to change motor ID {old_id} → {new_id}...")
    
    # Method 1: Standard ID change command (0x30)
    print("  Trying method 1 (0x30 command)...")
    cmd = bytes([0x41, 0x54, 0x30, 0x07, 0xe8, old_id, 0x08, 0x00,
                 new_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.5)
    response = ser.read(100)
    if len(response) > 0:
        print(f"    Response: {response.hex()}")
    
    # Method 2: Configuration mode command (0x40)
    print("  Trying method 2 (0x40 command)...")
    cmd = bytes([0x41, 0x54, 0x40, 0x07, 0xe8, old_id, 0x08, 0x00,
                 0x01, new_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.5)
    response = ser.read(100)
    if len(response) > 0:
        print(f"    Response: {response.hex()}")
    
    # Method 3: Write parameter command (0x20 with ID parameter)
    print("  Trying method 3 (parameter write)...")
    cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, old_id, 0x08, 0x00,
                 0x01, new_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.5)
    response = ser.read(100)
    if len(response) > 0:
        print(f"    Response: {response.hex()}")
    
    return True

def verify_motor_id(ser, motor_id):
    """Check if motor responds at given ID"""
    cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.2)
    response = ser.read(100)
    return len(response) > 4

def main():
    print("="*70)
    print("  MOTOR ID CONFIGURATION TOOL")
    print("="*70)
    print()
    print("⚠️  WARNING: This tool attempts to change motor CAN IDs")
    print("   Make sure you understand what you're doing!")
    print()
    print("Note: RobStride motors may require Motor Studio for ID changes.")
    print("This script tries several methods, but success is not guaranteed.")
    print()
    
    cont = input("Continue? (yes/no): ").strip().lower()
    if cont != 'yes':
        print("Aborted.")
        return
    
    print()
    
    # Open serial connection
    PORT = '/dev/ttyUSB1'
    BAUD = 921600
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"✓ Connected to {PORT} at {BAUD} baud")
        print()
    except Exception as e:
        print(f"✗ Failed to open serial port: {e}")
        return
    
    # Scan for motors
    print("Scanning for motors...")
    with JetsonMotorController() as controller:
        motors = controller.scan_motors(start_id=1, end_id=127)
    
    if not motors:
        print("✗ No motors found!")
        ser.close()
        return
    
    print(f"\n✓ Found {len(motors)} motor IDs: {motors}")
    print()
    
    # Interactive configuration
    while True:
        print("="*70)
        print("  CONFIGURE MOTOR ID")
        print("="*70)
        print()
        print(f"Available motor IDs: {motors}")
        print()
        print("Enter 'scan' to rescan")
        print("Enter 'test ID' to test a motor (e.g., 'test 21')")
        print("Enter 'quit' to exit")
        print()
        
        old_id = input("Enter current motor ID to reconfigure: ").strip()
        
        if old_id.lower() == 'quit':
            break
        elif old_id.lower() == 'scan':
            print("\nRescanning...")
            with JetsonMotorController() as controller:
                motors = controller.scan_motors(start_id=1, end_id=127)
            print(f"Found {len(motors)} motor IDs: {motors}")
            continue
        elif old_id.lower().startswith('test '):
            test_id = int(old_id.split()[1])
            print(f"\nTesting motor {test_id}...")
            with JetsonMotorController() as controller:
                controller.pulse_motor(test_id, pulses=3)
            continue
        
        try:
            old_id = int(old_id)
        except ValueError:
            print("✗ Invalid ID")
            continue
        
        if old_id not in motors:
            print(f"✗ Motor ID {old_id} not found in scan")
            cont = input("Continue anyway? (y/n): ").strip().lower()
            if cont != 'y':
                continue
        
        new_id = input(f"Enter NEW motor ID for motor {old_id}: ").strip()
        try:
            new_id = int(new_id)
        except ValueError:
            print("✗ Invalid ID")
            continue
        
        if new_id < 1 or new_id > 127:
            print("✗ ID must be between 1 and 127")
            continue
        
        print()
        print(f"Will attempt to change motor {old_id} → {new_id}")
        confirm = input("Confirm? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled")
            continue
        
        # Attempt ID change
        send_id_change_command(ser, old_id, new_id)
        
        print()
        print("Waiting 2 seconds for motor to update...")
        time.sleep(2)
        
        # Verify
        print("\nVerifying new ID...")
        if verify_motor_id(ser, new_id):
            print(f"✓ Motor now responds at ID {new_id}!")
            
            # Update motor list
            if old_id in motors:
                motors.remove(old_id)
            if new_id not in motors:
                motors.append(new_id)
            motors.sort()
        else:
            print(f"✗ Motor does not respond at ID {new_id}")
            print("  The ID change may have failed.")
            print("  You may need to use RobStride Motor Studio.")
        
        print()
        input("Press Enter to continue...")
        print()
    
    ser.close()
    print()
    print("="*70)
    print("Configuration complete!")
    print("="*70)
    print()
    print("IMPORTANT:")
    print("- If ID changes didn't work, you'll need Motor Studio")
    print("- Power cycle motors after ID changes")
    print("- Run scan to verify new IDs")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

