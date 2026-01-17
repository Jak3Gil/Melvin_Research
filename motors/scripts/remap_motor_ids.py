#!/usr/bin/env python3
"""
Remap Motor CAN IDs with verification
This script attempts to configure motors with unique CAN IDs and verifies
that different motors are responding to different IDs (not just one motor)
"""

import serial
import sys
import time

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
        time.sleep(0.1)
        return True
    except:
        return False

def move_motor_pattern(ser, can_id, pattern_number):
    """Move motor with a unique pattern to identify which physical motor it is"""
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    # Move pattern_number times to create unique identifier
    for i in range(pattern_number):
        send_command(ser, build_move_jog_cmd(can_id, 0.04, 1))
        time.sleep(0.3)
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.2)
    
    send_command(ser, build_deactivate_cmd(can_id))

def test_motor_response(ser, can_id):
    """Test if a motor responds to a specific CAN ID"""
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    # Try a small movement
    send_command(ser, build_move_jog_cmd(can_id, 0.03, 1))
    time.sleep(0.5)
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
    time.sleep(0.2)
    
    send_command(ser, build_deactivate_cmd(can_id))
    return True

def try_configure_can_id(ser, current_id, new_id):
    """
    Try different methods to configure CAN ID
    Returns True if configuration command was sent (not verified)
    """
    print(f"\nAttempting to configure CAN ID {current_id} -> {new_id}...")
    
    # Method 1: Try configuration command format (common patterns)
    config_methods = [
        # Format: AT <cmd> <addr> <current_id> <data_with_new_id>
        ([0x30, 0x07, 0xe8, current_id, 0x01, new_id, 0x00, 0x00, 0x00, 0x00]),
        ([0x31, 0x07, 0xe8, current_id, new_id, 0x00, 0x00, 0x00, 0x00, 0x00]),
        ([0x32, 0x07, 0xe8, current_id, 0x00, new_id, 0x00, 0x00, 0x00, 0x00]),
        # Alternative format
        ([0x40, 0x07, 0xe8, current_id, 0x02, new_id, 0x00, 0x00, 0x00, 0x00]),
    ]
    
    for method_idx, data in enumerate(config_methods):
        cmd = bytearray([0x41, 0x54])  # AT
        cmd.extend(data)
        cmd.extend([0x0d, 0x0a])  # \r\n
        
        print(f"  Trying method {method_idx + 1}: {cmd.hex(' ')}")
        send_command(ser, bytes(cmd))
        time.sleep(0.3)
    
    print(f"  Configuration commands sent (verification needed)")
    return True

def verify_unique_responses(ser, configured_mappings):
    """
    Verify that different CAN IDs are controlling different motors
    Returns True if motors appear to be responding uniquely
    """
    print("\n" + "="*60)
    print("VERIFICATION: Testing if motors respond uniquely")
    print("="*60)
    
    print("\nCRITICAL: Watch which PHYSICAL motor moves for each CAN ID.")
    print("If the SAME motor moves for all IDs, configuration failed.")
    print("If DIFFERENT motors move for different IDs, configuration succeeded!")
    print("\nPress Enter to start verification...")
    input()
    
    results = {}
    motor_positions = {}  # Track which motor position moved for each ID
    
    for new_id in sorted(configured_mappings.keys()):
        print(f"\n{'='*60}")
        print(f"Testing CAN ID {new_id} (0x{new_id:02X})")
        print(f"{'='*60}")
        print("Watch which PHYSICAL motor moves...")
        input("Press Enter to move this ID...")
        
        send_command(ser, build_activate_cmd(new_id))
        time.sleep(0.2)
        send_command(ser, build_load_params_cmd(new_id))
        time.sleep(0.2)
        
        print("Moving FORWARD...")
        send_command(ser, build_move_jog_cmd(new_id, 0.05, 1))
        time.sleep(1.0)
        send_command(ser, build_move_jog_cmd(new_id, 0.0, 0))
        time.sleep(0.5)
        
        send_command(ser, build_deactivate_cmd(new_id))
        time.sleep(0.3)
        
        # Ask user which physical motor moved
        print(f"\nWhich PHYSICAL motor moved? (Enter motor number 1-15, or 'same' if same as previous)")
        motor_pos = input("Physical motor number: ").strip().lower()
        
        if motor_pos == 'same':
            results[new_id] = False
            motor_positions[new_id] = motor_positions.get(list(results.keys())[-1] if results else new_id, 'unknown')
        else:
            try:
                motor_num = int(motor_pos)
                motor_positions[new_id] = motor_num
                # Check if this motor position was used before
                if motor_num in motor_positions.values() and list(motor_positions.values()).count(motor_num) > 1:
                    # This motor position was already used
                    prev_id = [id for id, pos in motor_positions.items() if pos == motor_num and id != new_id][0]
                    print(f"  WARNING: Motor {motor_num} also responded to CAN ID {prev_id}")
                    results[new_id] = False
                else:
                    results[new_id] = True
            except:
                results[new_id] = False
                motor_positions[new_id] = 'unknown'
    
    print("\n" + "="*60)
    print("VERIFICATION RESULTS")
    print("="*60)
    
    # Show mapping
    print("\nCAN ID -> Physical Motor mapping:")
    for can_id, motor_pos in motor_positions.items():
        status = "✓ UNIQUE" if results.get(can_id, False) else "✗ DUPLICATE"
        print(f"  CAN ID {can_id:2d} (0x{can_id:02X}) -> Physical Motor {motor_pos} {status}")
    
    unique_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    print(f"\nMotors responding uniquely: {unique_count} of {total_count}")
    
    if unique_count == total_count and total_count > 0:
        print("\n[SUCCESS] All motors are responding to unique CAN IDs!")
        print("Configuration appears to have worked!")
    elif unique_count > 0:
        print(f"\n[PARTIAL SUCCESS] {unique_count} motors are responding uniquely")
        print(f"                {total_count - unique_count} motors share IDs with others")
        print("Some motors may need to be reconfigured")
    else:
        print("\n[FAILED] All motors are still responding to the same ID(s)")
        print("Configuration commands did not work.")
        print("\nPossible reasons:")
        print("  - Motors don't support software CAN ID configuration")
        print("  - Configuration command format is incorrect")
        print("  - Need to use motor configuration software")
        print("  - Need to configure motors one at a time (disconnect others)")
    
    return unique_count == total_count and total_count > 0

def main():
    port = "COM3"
    baud = 921600
    
    print("="*60)
    print("MOTOR CAN ID REMAPPING TOOL")
    print("="*60)
    print("\nThis tool will:")
    print("  1. Identify motors using movement patterns")
    print("  2. Attempt to configure unique CAN IDs")
    print("  3. Verify that different motors respond to different IDs")
    print("\nWARNING: Configuration method depends on motor type.")
    print("This tool tries common formats but may not work for all motors.")
    
    input("\nPress Enter to continue...")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened")
        
        # Step 1: Identify motors with patterns
        print("\n" + "="*60)
        print("STEP 1: Identify Motors")
        print("="*60)
        print("\nEach motor will move with a unique pattern.")
        print("Watch carefully to identify which physical motor is which.")
        
        configured_mappings = {}  # new_can_id -> pattern_number
        
        # We'll configure motors 1-7 to IDs 16-22, and 8-15 to IDs 8-15
        # But since we can't distinguish motors yet, we'll try a different approach:
        # Disconnect motors one at a time, or use a systematic method
        
        print("\nIMPORTANT: Since all motors respond to all IDs, we need a way to")
        print("configure them individually. Options:")
        print("  1. Disconnect motors one at a time (leave only one connected)")
        print("  2. Use motor configuration software")
        print("  3. Use hardware configuration (DIP switches/jumpers)")
        print("  4. Try configuration commands (experimental)")
        
        response = input("\nDo you want to try configuration commands? (y/n): ")
        if response.lower() != 'y':
            print("\nPlease use motor configuration software or hardware method.")
            print("See CONFIGURE_MOTOR_IDS.md for details.")
            ser.close()
            return
        
        # Try to configure motors systematically
        # Since all respond, we'll configure them one at a time and verify
        target_ids = list(range(16, 23)) + list(range(8, 16))  # IDs 16-22, then 8-15
        pattern_numbers = list(range(1, 8)) + list(range(8, 16))  # Patterns to identify
        
        print("\nSince all motors respond to all IDs, we'll try a systematic approach:")
        print("1. Send configuration commands for each target ID")
        print("2. Verify that motors respond differently after configuration")
        print("\nNOTE: This may not work if motors don't support software configuration.")
        
        input("\nPress Enter to start configuration attempts...")
        
        # Try configuring motors - since we can't isolate them, we'll configure
        # all of them and hope the configuration commands work
        for target_id in target_ids[:15]:  # Configure first 15 IDs
            print(f"\nConfiguring to CAN ID {target_id}...")
            # Use ID 8 as source (since all respond to it)
            try_configure_can_id(ser, 8, target_id)
            configured_mappings[target_id] = target_id  # Store mapping
            time.sleep(0.5)
        
        # Step 2: Verify unique responses
        if configured_mappings:
            print("\n" + "="*60)
            print("STEP 2: Verification")
            print("="*60)
            verify_unique_responses(ser, configured_mappings)
        else:
            print("\nNo motors were configured.")
        
        ser.close()
        print("\n[OK] Process complete")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

