#!/usr/bin/env python3
"""
Try CAN ID Configuration Commands
Attempt various configuration command formats to set motor CAN IDs
"""

import serial
import sys
import time

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
    except:
        return b""

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0):
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

def try_configure_id(ser, current_id, new_id):
    """Try different configuration command formats"""
    
    config_commands = [
        # Format 1: AT <cmd> <addr_h> <addr_l> <current_id> <data...>
        {
            'name': 'Method 1: ID config byte 0x30',
            'cmd': bytes([0x41, 0x54, 0x30, 0x07, 0xe8, current_id, 0x01, new_id, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': 'Method 2: ID config byte 0x31',
            'cmd': bytes([0x41, 0x54, 0x31, 0x07, 0xe8, current_id, new_id, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': 'Method 3: ID config byte 0x32',
            'cmd': bytes([0x41, 0x54, 0x32, 0x07, 0xe8, current_id, 0x00, new_id, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': 'Method 4: ID config byte 0x40',
            'cmd': bytes([0x41, 0x54, 0x40, 0x07, 0xe8, current_id, 0x02, new_id, 0x00, 0x00, 0x0d, 0x0a])
        },
        {
            'name': 'Method 5: Extended format',
            'cmd': bytes([0x41, 0x54, 0x50, 0x07, 0xe8, current_id, 0x08, 0x00, 0x01, new_id, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        },
        # Try configuration mode first, then set ID
        {
            'name': 'Method 6: Enter config mode then set ID',
            'cmd': bytes([0x41, 0x54, 0x35, 0x07, 0xe8, current_id, 0x01, 0x00, 0x0d, 0x0a])  # Enter config
        },
    ]
    
    print(f"\nTrying to configure motor from ID {current_id} to {new_id}...")
    
    for method in config_commands:
        print(f"\n  {method['name']}")
        print(f"  Command: {method['cmd'].hex(' ')}")
        response = send_command(ser, method['cmd'])
        if response:
            print(f"  Response: {response.hex(' ')}")
        else:
            print(f"  No response")
        time.sleep(0.3)
    
    # If Method 6 was used, send ID setting command
    print(f"\n  Sending ID setting command...")
    id_set_cmd = bytes([0x41, 0x54, 0x30, 0x07, 0xe8, current_id, 0x02, new_id, 0x00, 0x00, 0x0d, 0x0a])
    print(f"  Command: {id_set_cmd.hex(' ')}")
    response = send_command(ser, id_set_cmd)
    if response:
        print(f"  Response: {response.hex(' ')}")

def test_id_after_config(ser, test_id):
    """Test if motor responds to new ID"""
    print(f"\nTesting if motor now responds to ID {test_id}...")
    
    send_command(ser, build_activate_cmd(test_id))
    time.sleep(0.2)
    
    send_command(ser, build_move_jog_cmd(test_id, 0.04))
    time.sleep(0.6)
    send_command(ser, build_move_jog_cmd(test_id, 0.0))
    
    return test_id

def main():
    port = "COM3"
    baud = 921600
    
    print("="*70)
    print("CAN ID Configuration Command Attempts")
    print("="*70)
    print("\nWARNING: Configuration command format is motor-specific.")
    print("These are common formats - your motors may use different commands.")
    print("\nThis script will try various configuration command formats.")
    print("Check motor documentation for correct format if these don't work.")
    
    input("\nPress Enter to continue...")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened")
        
        print("\n" + "="*70)
        print("CONFIGURATION ATTEMPT")
        print("="*70)
        print("\nSince only 2 motors are working, we need to configure the others.")
        print("\nIMPORTANT: Configuration commands typically need to:")
        print("  1. Be sent to motors one at a time (disconnect others)")
        print("  2. Use the correct command format (check documentation)")
        print("  3. Put motor in configuration mode first (if required)")
        
        print("\nFor now, we'll try to configure a motor that's not responding.")
        print("We'll use ID 0 (default) as source and try to set it to ID 1.")
        
        input("\nPress Enter to try configuration commands...")
        
        # Try configuring from default ID (0) to ID 1
        try_configure_id(ser, 0, 1)
        
        # Try configuring from default ID (0) to ID 2
        time.sleep(0.5)
        try_configure_id(ser, 0, 2)
        
        print("\n" + "="*70)
        print("TESTING AFTER CONFIGURATION")
        print("="*70)
        print("\nTesting if motors now respond to new IDs...")
        input("Press Enter to test...")
        
        # Test if any motors respond to new IDs
        for test_id in [1, 2, 3]:
            test_id_after_config(ser, test_id)
            response = input(f"\nDid any motor move when testing ID {test_id}? (y/n): ")
            if response.lower() == 'y':
                print(f"[SUCCESS] Motor responds to ID {test_id}!")
                break
        
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        print("\nIf configuration commands worked, motors should respond to new IDs.")
        print("If not, you need:")
        print("  1. Motor documentation with correct command format")
        print("  2. Motor configuration software")
        print("  3. Hardware configuration (DIP switches/jumpers)")
        print("  4. Configure motors one at a time (disconnect others)")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

