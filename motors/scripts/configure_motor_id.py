#!/usr/bin/env python3
"""
Configure Motor CAN ID
This script attempts to configure a motor's CAN ID using L91 protocol

NOTE: This may require specific configuration commands that vary by motor type.
Check your motor documentation for the exact configuration method.
"""

import serial
import sys
import time

def build_command(base_cmd, can_id, data):
    """Build L91 command - format may vary for configuration"""
    cmd = bytearray([0x41, 0x54])  # AT
    cmd.extend(base_cmd)
    cmd.extend([0x07, 0xe8])  # Address
    cmd.append(can_id)
    cmd.extend(data)
    cmd.extend([0x0d, 0x0a])  # \r\n
    return bytes(cmd)

def send_command(ser, cmd):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.2)
        
        # Read response
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.3:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
            time.sleep(0.01)
        
        return response
    except Exception as e:
        print(f"Error: {e}")
        return b""

def configure_motor_id(ser, old_can_id, new_can_id):
    """
    Attempt to configure motor CAN ID
    WARNING: This is a template - actual command format depends on motor type
    """
    print(f"\nAttempting to configure Motor from CAN ID {old_can_id} to {new_can_id}...")
    print("NOTE: This command format may need adjustment based on your motor documentation")
    
    # Method 1: Try configuration command (format varies by motor)
    # This is a template - check your motor documentation
    config_cmd = build_command(
        [0x30],  # Configuration command (may vary)
        old_can_id,
        [0x01, new_can_id, 0x00, 0x00, 0x00]  # Data: set ID to new_can_id
    )
    
    print(f"Sending configuration command...")
    print(f"Hex: {config_cmd.hex(' ')}")
    response = send_command(ser, config_cmd)
    
    if response:
        print(f"Response: {response.hex(' ')}")
    else:
        print("No response")
    
    time.sleep(0.5)
    
    # Method 2: Some motors use different configuration methods
    # You may need to:
    # - Use motor configuration software
    # - Use DIP switches/jumpers
    # - Use specific configuration commands from motor manual
    
    print("\nIMPORTANT: Check your motor documentation for CAN ID configuration method!")
    print("Common methods:")
    print("  1. Motor configuration software (Robstride Motor Studio, etc.)")
    print("  2. DIP switches or jumpers on motor controller")
    print("  3. Specific configuration commands (check manual)")
    print("  4. Boot/configuration mode with specific commands")

def main():
    if len(sys.argv) < 3:
        print("Usage: python configure_motor_id.py <old_can_id> <new_can_id>")
        print("Example: python configure_motor_id.py 8 16")
        print("\nWARNING: This is a template script.")
        print("Actual configuration method depends on your motor type.")
        print("Check motor documentation for correct configuration commands.")
        sys.exit(1)
    
    old_id = int(sys.argv[1])
    new_id = int(sys.argv[2])
    port = "COM3"
    baud = 921600
    
    if new_id < 1 or new_id > 31:
        print("ERROR: CAN ID must be between 1 and 31")
        sys.exit(1)
    
    print("="*60)
    print("MOTOR CAN ID CONFIGURATION")
    print("="*60)
    print(f"\nOld CAN ID: {old_id} (0x{old_id:02X})")
    print(f"New CAN ID: {new_id} (0x{new_id:02X})")
    print("\nWARNING: This may not work - check motor documentation!")
    
    confirm = input("\nContinue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled")
        sys.exit(0)
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened")
        
        configure_motor_id(ser, old_id, new_id)
        
        print("\n" + "="*60)
        print("Configuration attempt complete")
        print("="*60)
        print("\nTo verify:")
        print(f"  1. Run scan: python scan_robstride_motors.py COM3 921600")
        print(f"  2. Test new ID: python test_single_motor.py {new_id}")
        print(f"  3. Check if motor responds to new ID")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

