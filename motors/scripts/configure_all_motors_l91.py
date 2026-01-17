#!/usr/bin/env python3
"""
Configure All Motors Using L91 Protocol
Uses the existing L91 communication line to configure motors
"""
import serial
import time
import struct
import sys

PORT = '/dev/ttyUSB0'
BAUD = 921600

def send_l91_command(ser, can_id, command_type, data_bytes):
    """
    Send L91 protocol command
    
    Format: AT + Command Type + CAN ID + Data + Terminator
    
    Args:
        ser: Serial port object
        can_id: CAN ID (motor ID)
        command_type: Command type byte (0x00, 0x20, 0x30, etc.)
        data_bytes: Data bytes (list or bytes)
    """
    cmd = bytearray([0x41, 0x54, command_type])  # AT header + command type
    
    # CAN ID (2 bytes)
    cmd.append((can_id >> 8) & 0xFF)
    cmd.append(can_id & 0xFF)
    
    # Data
    if isinstance(data_bytes, (list, tuple)):
        cmd.extend(data_bytes)
    else:
        cmd.extend(data_bytes)
    
    # Ensure length (pad or truncate to 8 bytes)
    while len(cmd) < 14:  # AT(2) + type(1) + ID(2) + data(8) + term(2) = 15?
        cmd.append(0x00)
    
    # Terminator
    if len(cmd) < 16:
        cmd = cmd[:14]
    cmd.extend([0x0D, 0x0A])
    
    ser.write(bytes(cmd))
    time.sleep(0.1)
    
    # Read response
    response = b""
    start_time = time.time()
    while time.time() - start_time < 0.3:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
            time.sleep(0.02)
    
    return response

def scan_motors_l91(ser, start_id=1, end_id=127):
    """Scan for motors using L91 protocol"""
    print(f"Scanning for motors (IDs {start_id}-{end_id})...")
    
    found = []
    
    for motor_id in range(start_id, end_id + 1):
        # Send enable command (0x01)
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xE8, motor_id, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0x0A])
        
        ser.reset_input_buffer()
        ser.write(cmd)
        time.sleep(0.15)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        
        if len(response) > 4:
            # Verify with load params
            cmd2 = bytes([0x41, 0x54, 0x20, 0x07, 0xE8, motor_id, 0x08, 0x00,
                         0xC4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0x0A])
            ser.reset_input_buffer()
            ser.write(cmd2)
            time.sleep(0.15)
            
            response2 = b""
            start_time = time.time()
            while time.time() - start_time < 0.25:
                if ser.in_waiting > 0:
                    response2 += ser.read(ser.in_waiting)
                    time.sleep(0.02)
            
            # Deactivate
            cmd3 = bytes([0x41, 0x54, 0x00, 0x07, 0xE8, motor_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0x0A])
            ser.write(cmd3)
            time.sleep(0.1)
            
            if len(response2) > 4:
                found.append(motor_id)
                print(f"  Found: ID {motor_id:3d} (0x{motor_id:02X})")
    
    return found

def configure_motor_id_l91(ser, old_id, new_id):
    """
    Configure motor to new ID using L91 protocol
    
    Based on typical RobStride L91 commands:
    - ID change command format may be: AT + 0x30 + old_id + new_id
    """
    print(f"\nAttempting to configure motor {old_id} → {new_id}...")
    
    # Method 1: Try ID change command (0x30)
    print("  Method 1: ID change command (0x30)...")
    cmd = bytes([0x41, 0x54, 0x30, 0x07, 0xE8, old_id, 0x08, 0x00,
                 new_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0x0A])
    
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.5)
    
    response = b""
    start_time = time.time()
    while time.time() - start_time < 0.5:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
            time.sleep(0.02)
    
    if len(response) > 4:
        print(f"    Response: {response.hex()}")
    
    # Method 2: Try configuration mode write
    print("  Method 2: Configuration write (0x40)...")
    cmd = bytes([0x41, 0x54, 0x40, 0x07, 0xE8, old_id, 0x08, 0x00,
                 0x01, new_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0x0A])
    
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.5)
    
    response2 = b""
    start_time = time.time()
    while time.time() - start_time < 0.5:
        if ser.in_waiting > 0:
            response2 += ser.read(ser.in_waiting)
            time.sleep(0.02)
    
    if len(response2) > 4:
        print(f"    Response: {response2.hex()}")
    
    # Wait for motor to update
    print("  Waiting 2 seconds for motor to update...")
    time.sleep(2.0)
    
    # Verify new ID
    print("  Verifying new ID...")
    cmd_verify = bytes([0x41, 0x54, 0x00, 0x07, 0xE8, new_id, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0x0A])
    ser.reset_input_buffer()
    ser.write(cmd_verify)
    time.sleep(0.2)
    
    verify_response = b""
    start_time = time.time()
    while time.time() - start_time < 0.3:
        if ser.in_waiting > 0:
            verify_response += ser.read(ser.in_waiting)
            time.sleep(0.02)
    
    if len(verify_response) > 4:
        print(f"    ✓ Motor responds at new ID {new_id}!")
        return True
    else:
        print(f"    ✗ Motor does not respond at new ID {new_id}")
        return False

def main():
    print("="*70)
    print("  CONFIGURE ALL MOTORS USING L91 PROTOCOL")
    print("="*70)
    print()
    print(f"Port: {PORT}")
    print(f"Baud: {BAUD}")
    print()
    print("This script uses the existing L91 communication line")
    print("to configure motors to single, unique IDs.")
    print()
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"✓ Connected to {PORT}")
        print()
    except Exception as e:
        print(f"✗ Failed to open port: {e}")
        print(f"\nMake sure USB-to-CAN adapter is connected to Jetson")
        return
    
    # Initialize adapter
    print("Initializing adapter...")
    ser.write(b'AT+AT\r\n')
    time.sleep(0.2)
    response = ser.read(100)
    if b'OK' in response:
        print("✓ Adapter responding")
    print()
    
    # Scan for motors
    print("="*70)
    print("  STEP 1: SCAN FOR MOTORS")
    print("="*70)
    print()
    
    motors = scan_motors_l91(ser, 1, 127)
    
    if not motors:
        print("✗ No motors found!")
        ser.close()
        return
    
    print(f"\n✓ Found {len(motors)} motor IDs")
    print()
    
    # Group motors by ranges
    groups = []
    if motors:
        current_group = [motors[0]]
        for i in range(1, len(motors)):
            if motors[i] == motors[i-1] + 1:
                current_group.append(motors[i])
            else:
                groups.append(current_group)
                current_group = [motors[i]]
        groups.append(current_group)
    
    print(f"Motor groups: {len(groups)}")
    print("(Each group likely represents one physical motor)")
    print()
    
    for i, group in enumerate(groups, 1):
        print(f"  Group {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
    
    print()
    print("="*70)
    print("  STEP 2: CONFIGURE MOTORS")
    print("="*70)
    print()
    print("⚠️  WARNING: This will attempt to change motor IDs!")
    print("Make sure you understand what you're doing.")
    print()
    print(f"Will configure {len(groups)} motor(s) to IDs 1-{len(groups)}")
    print()
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Aborted.")
        ser.close()
        return
    
    # Configure each motor group
    print()
    print("Configuring motors...")
    print()
    
    configuration_map = {}
    successful = 0
    failed = 0
    
    for i, group in enumerate(groups, 1):
        test_id = group[0]  # Use first ID from group
        new_id = i  # Sequential IDs: 1, 2, 3, ...
        
        print(f"Group {i}: Configuring ID {test_id} → {new_id}")
        
        if configure_motor_id_l91(ser, test_id, new_id):
            configuration_map[test_id] = new_id
            successful += 1
            print(f"  ✓ Success!")
        else:
            failed += 1
            print(f"  ✗ Failed (may need Motor Studio)")
        
        print()
        time.sleep(0.5)
    
    ser.close()
    
    # Summary
    print("="*70)
    print("  CONFIGURATION SUMMARY")
    print("="*70)
    print()
    print(f"Successful: {successful}/{len(groups)}")
    print(f"Failed: {failed}/{len(groups)}")
    print()
    
    if configuration_map:
        print("Configuration map:")
        for old_id, new_id in sorted(configuration_map.items()):
            print(f"  Old ID {old_id:3d} → New ID {new_id}")
        print()
        
        # Save to file
        with open('motor_configuration_map.txt', 'w') as f:
            f.write("Motor Configuration Map\n")
            f.write("="*50 + "\n\n")
            for old_id, new_id in sorted(configuration_map.items()):
                f.write(f"Old ID {old_id:3d} → New ID {new_id}\n")
        
        print("✓ Configuration map saved to: motor_configuration_map.txt")
    
    print()
    print("="*70)
    print("  NEXT STEPS")
    print("="*70)
    print()
    
    if failed > 0:
        print("Some motors failed to configure.")
        print("This is normal - L91 protocol may not support ID changes.")
        print()
        print("You may need to:")
        print("  1. Use Motor Studio to change IDs")
        print("  2. Or use motors with current IDs (works fine!)")
    else:
        print("✓ All motors configured successfully!")
        print()
        print("Test with:")
        print("  python3 scan_all_motors_wide.py /dev/ttyUSB0 921600 --start 1 --end 20")
    
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

