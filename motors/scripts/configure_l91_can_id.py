#!/usr/bin/env python3
"""
L91 CAN ID Configuration Script
Attempts to configure CAN IDs using L91 protocol AT commands
Based on known L91 command format: AT <cmd> 0x07 0xe8 <id> <data...> 0x0d 0x0a
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
        print(f"Error: {e}")
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

def try_config_commands(ser, source_id, target_id):
    """
    Try various L91 command bytes that might configure CAN ID
    L91 format: AT <cmd_byte> 0x07 0xe8 <current_id> <data...> 0x0d 0x0a
    
    Known commands:
    - 0x00 = activate/deactivate
    - 0x20 = load params
    - 0x90 = move jog
    
    Trying these command bytes for configuration:
    - 0x10-0x1F = parameter/config range
    - 0x30-0x3F = configuration commands
    - 0x40-0x4F = extended config
    - 0x50-0x5F = settings
    """
    
    print(f"\n{'='*70}")
    print(f"Attempting to configure CAN ID: {source_id} -> {target_id}")
    print(f"{'='*70}")
    
    # Configuration command attempts
    # Format: AT <cmd> 0x07 0xe8 <source_id> <data_with_target_id> 0x0d 0x0a
    config_attempts = [
        # Single byte commands (6 bytes total after AT)
        {
            'name': '0x10: Config command',
            'cmd': bytes([0x41, 0x54, 0x10, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': '0x11: ID set command',
            'cmd': bytes([0x41, 0x54, 0x11, 0x07, 0xe8, source_id, 0x01, target_id, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': '0x12: Address config',
            'cmd': bytes([0x41, 0x54, 0x12, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        # Two-byte data commands
        {
            'name': '0x30: Config with length',
            'cmd': bytes([0x41, 0x54, 0x30, 0x07, 0xe8, source_id, 0x02, 0x00, target_id, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': '0x31: ID configuration',
            'cmd': bytes([0x41, 0x54, 0x31, 0x07, 0xe8, source_id, 0x01, target_id, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': '0x32: Set ID command',
            'cmd': bytes([0x41, 0x54, 0x32, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': '0x33: Address set',
            'cmd': bytes([0x41, 0x54, 0x33, 0x07, 0xe8, source_id, 0x01, target_id, 0x00, 0x00, 0x0d, 0x0a])
        },
        # Extended format (8 bytes data like load params)
        {
            'name': '0x40: Extended config format',
            'cmd': bytes([0x41, 0x54, 0x40, 0x07, 0xe8, source_id, 0x08, 0x00, 0x01, target_id, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': '0x41: ID config extended',
            'cmd': bytes([0x41, 0x54, 0x41, 0x07, 0xe8, source_id, 0x08, 0x00, target_id, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        # Try using address in different positions
        {
            'name': '0x50: Settings command',
            'cmd': bytes([0x41, 0x54, 0x50, 0x07, 0xe8, source_id, 0x08, 0x00, 0x02, target_id, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        # Try with 0x07e8 address format (might need to set ID in address field?)
        {
            'name': '0x60: Address in high byte',
            'cmd': bytes([0x41, 0x54, 0x60, target_id, 0xe8, source_id, 0x01, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        # Try broadcast to set ID (ID 0 or 0xFF)
        {
            'name': '0x70: Broadcast config',
            'cmd': bytes([0x41, 0x54, 0x70, 0x07, 0xe8, 0x00, 0x01, target_id, 0x00, 0x00, 0x0d, 0x0a])
        },
    ]
    
    responses = []
    
    for attempt in config_attempts:
        print(f"\nTrying: {attempt['name']}")
        print(f"Command: {attempt['cmd'].hex(' ').upper()}")
        
        response = send_command(ser, attempt['cmd'])
        
        if response:
            print(f"Response: {response.hex(' ').upper()}")
            responses.append((attempt['name'], response))
        else:
            print("No response")
        
        time.sleep(0.3)
    
    return responses

def test_motor_id(ser, test_id):
    """Test if a motor responds to a specific CAN ID"""
    print(f"\nTesting if motor responds to CAN ID {test_id}...")
    
    # Activate
    send_command(ser, build_activate_cmd(test_id), wait_response=False)
    time.sleep(0.3)
    
    # Try small movement
    send_command(ser, build_move_jog_cmd(test_id, 0.03), wait_response=False)
    time.sleep(0.6)
    send_command(ser, build_move_jog_cmd(test_id, 0.0), wait_response=False)
    
    return test_id

def main():
    port = "COM3"
    baud = 921600
    
    if len(sys.argv) >= 3:
        source_id = int(sys.argv[1])
        target_id = int(sys.argv[2])
    else:
        print("Usage: python configure_l91_can_id.py <source_id> <target_id>")
        print("Example: python configure_l91_can_id.py 0 1")
        print("\nThis will attempt to configure a motor from source_id to target_id")
        print("Common: Use source_id=0 (default/unconfigured) or source_id=8 (currently working)")
        sys.exit(1)
    
    if target_id < 1 or target_id > 31:
        print("ERROR: Target CAN ID must be between 1 and 31")
        sys.exit(1)
    
    print("="*70)
    print("L91 CAN ID Configuration Attempt")
    print("="*70)
    print(f"\nSource ID: {source_id} (0x{source_id:02X})")
    print(f"Target ID: {target_id} (0x{target_id:02X})")
    print("\nWARNING: This script tries various command formats.")
    print("Configuration may require:")
    print("  - Motors to be disconnected one at a time")
    print("  - Specific command format from motor documentation")
    print("  - Hardware configuration (DIP switches)")
    
    input("\nPress Enter to continue...")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened")
        
        # Try configuration commands
        responses = try_config_commands(ser, source_id, target_id)
        
        print("\n" + "="*70)
        print("Testing Configuration")
        print("="*70)
        print("\nTesting if motor now responds to target ID...")
        input("Press Enter to test...")
        
        test_motor_id(ser, target_id)
        
        response = input(f"\nDid any motor move when testing ID {target_id}? (y/n): ")
        
        if response.lower() == 'y':
            print(f"\n[SUCCESS] Motor appears to respond to ID {target_id}!")
            print("Configuration may have worked!")
        else:
            print(f"\n[FAILED] No motor responds to ID {target_id}")
            print("Configuration commands didn't work.")
            print("\nPossible reasons:")
            print("  1. Command format is incorrect")
            print("  2. Motors need to be configured one at a time (disconnect others)")
            print("  3. Motors require hardware configuration (DIP switches)")
            print("  4. Motors need different command format (check documentation)")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

