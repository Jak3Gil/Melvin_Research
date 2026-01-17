#!/usr/bin/env python3
"""
Configure All Motors with Unique CAN IDs
Since action commands aren't reaching motors, try software configuration
"""

import serial
import sys
import time

def send_command(ser, cmd, wait_response=True):
    """Send L91 command and optionally read response"""
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.2)
        
        if wait_response:
            response = b""
            start_time = time.time()
            while time.time() - start_time < 0.5:
                if ser.in_waiting > 0:
                    response += ser.read(ser.in_waiting)
                time.sleep(0.01)
            return response
        return b""
    except Exception as e:
        print(f"  Error: {e}")
        return b""

def build_activate_cmd(can_id):
    """AT 00 07 e8 <id> 01 00 0d 0a"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0):
    """AT 90 07 e8 <id> 08 05 70 00 00 07 <flag> <speed> 0d 0a"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = int(0x8000 + (speed * 3283.0))
    else:
        speed_val = int(0x7fff + (speed * 3283.0))
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, 1])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def try_config_command(ser, source_id, target_id, cmd_byte, description):
    """
    Try a configuration command format
    Format: AT <cmd_byte> 0x07 0xe8 <source_id> <data_with_target_id> 0x0d 0x0a
    """
    # Try different data formats with target_id
    formats = [
        # Format 1: Simple - target ID as single byte
        bytes([0x41, 0x54, cmd_byte, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x0d, 0x0a]),
        # Format 2: With length byte before target ID
        bytes([0x41, 0x54, cmd_byte, 0x07, 0xe8, source_id, 0x01, target_id, 0x00, 0x00, 0x0d, 0x0a]),
        # Format 3: With 0x02 length
        bytes([0x41, 0x54, cmd_byte, 0x07, 0xe8, source_id, 0x02, target_id, 0x00, 0x00, 0x0d, 0x0a]),
        # Format 4: Extended (8 bytes like load params)
        bytes([0x41, 0x54, cmd_byte, 0x07, 0xe8, source_id, 0x08, 0x00, 0x01, target_id, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a]),
        # Format 5: Extended with target in different position
        bytes([0x41, 0x54, cmd_byte, 0x07, 0xe8, source_id, 0x08, 0x00, target_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a]),
    ]
    
    for i, cmd in enumerate(formats):
        print(f"    Format {i+1}: {cmd.hex(' ').upper()}")
        response = send_command(ser, cmd)
        if response:
            print(f"      Response: {response.hex(' ').upper()}")
        time.sleep(0.2)

def configure_motor_id(ser, source_id, target_id):
    """Try to configure motor from source_id to target_id"""
    print(f"\n{'='*70}")
    print(f"Configuring: Source ID {source_id} (0x{source_id:02X}) -> Target ID {target_id} (0x{target_id:02X})")
    print(f"{'='*70}")
    
    # Try various command bytes that might be configuration commands
    config_commands = [
        (0x10, "Parameter/Config"),
        (0x11, "ID Configuration"),
        (0x12, "Address Config"),
        (0x30, "Config Command"),
        (0x31, "ID Set"),
        (0x32, "Set ID"),
        (0x33, "Address Set"),
        (0x40, "Extended Config"),
        (0x41, "ID Config Extended"),
        (0x50, "Settings"),
        (0x51, "ID Settings"),
    ]
    
    for cmd_byte, desc in config_commands:
        print(f"\n  Trying 0x{cmd_byte:02X}: {desc}")
        try_config_command(ser, source_id, target_id, cmd_byte, desc)
        time.sleep(0.3)
    
    print(f"\n  Configuration attempts complete for ID {target_id}")

def test_motor_response(ser, can_id):
    """Test if motor responds to a CAN ID"""
    print(f"\n  Testing CAN ID {can_id} (0x{can_id:02X})...")
    
    # Activate
    send_command(ser, build_activate_cmd(can_id), wait_response=False)
    time.sleep(0.3)
    
    # Try movement
    send_command(ser, build_move_jog_cmd(can_id, 0.03), wait_response=False)
    time.sleep(0.6)
    send_command(ser, build_move_jog_cmd(can_id, 0.0), wait_response=False)
    time.sleep(0.2)

def main():
    port = "COM3"
    baud = 921600
    
    print("="*70)
    print("L91 Motor CAN ID Configuration")
    print("="*70)
    print("\nThis script attempts to configure motors with unique CAN IDs")
    print("using software configuration commands.")
    print("\nKnown status:")
    print("  - Motor 1 responds to IDs 8-15")
    print("  - Motor 2 responds to IDs 16-22")
    print("  - Other 13 motors not responding")
    print("\nThis script will try to configure motors with unique IDs.")
    
    input("\nPress Enter to start configuration...")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened")
        
        # Configuration strategy:
        # Since we know IDs 8-15 control Motor 1 and 16-22 control Motor 2,
        # we'll try configuring:
        # 1. From ID 0 (default) to target IDs 1-7
        # 2. From ID 0 to target IDs 23-31
        # 3. Maybe also try from ID 8/16 to other IDs
        
        print("\n" + "="*70)
        print("CONFIGURATION STRATEGY")
        print("="*70)
        print("\nTrying to configure motors from default ID 0 to unique IDs")
        print("Target IDs: 1-7, 23-31 (avoiding 8-22 which are in use)")
        
        target_ids = list(range(1, 8)) + list(range(23, 32))  # IDs 1-7, 23-31
        
        for target_id in target_ids:
            print(f"\n{'#'*70}")
            print(f"CONFIGURING MOTOR TO ID {target_id}")
            print(f"{'#'*70}")
            
            # Try configuring from ID 0 (default/unconfigured)
            configure_motor_id(ser, 0, target_id)
            
            # Also try from ID 8 (currently Motor 1) - in case we need to change it
            if target_id != 8:
                configure_motor_id(ser, 8, target_id)
            
            # Also try from ID 16 (currently Motor 2)
            if target_id != 16:
                configure_motor_id(ser, 16, target_id)
            
            print(f"\n  Completed configuration attempts for ID {target_id}")
            time.sleep(0.5)
        
        print("\n" + "="*70)
        print("TESTING CONFIGURED MOTORS")
        print("="*70)
        print("\nTesting if motors now respond to new IDs...")
        print("Watch which physical motors move for each ID.")
        input("\nPress Enter to start testing...")
        
        test_results = {}
        
        for test_id in range(1, 32):
            test_motor_response(ser, test_id)
            
            response = input(f"\n  Which physical motor moved for ID {test_id}? (1-15, 'none', 'same'): ").strip().lower()
            test_results[test_id] = response
        
        # Summary
        print("\n" + "="*70)
        print("CONFIGURATION RESULTS")
        print("="*70)
        
        # Group by motor
        by_motor = {}
        for can_id, motor_info in test_results.items():
            if motor_info and motor_info != 'none' and motor_info != 'same':
                try:
                    motor_num = int(motor_info)
                    if motor_num not in by_motor:
                        by_motor[motor_num] = []
                    by_motor[motor_num].append(can_id)
                except:
                    pass
        
        print("\nCAN ID -> Physical Motor mapping:")
        for can_id in sorted(test_results.keys()):
            motor_info = test_results[can_id]
            print(f"  CAN ID {can_id:2d} (0x{can_id:02X}): Physical Motor {motor_info}")
        
        print(f"\nUnique motors responding: {len(by_motor)}")
        if by_motor:
            print("\nPhysical motors and their CAN IDs:")
            for motor_num in sorted(by_motor.keys()):
                can_ids = sorted(by_motor[motor_num])
                print(f"  Motor {motor_num}: CAN IDs {can_ids}")
        
        if len(by_motor) > 2:
            print("\n[SUCCESS] More motors are responding!")
        elif len(by_motor) == 2:
            print("\n[NO CHANGE] Still only 2 motors responding")
            print("Configuration commands may not have worked")
        else:
            print("\n[WARNING] Fewer motors responding than before")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

