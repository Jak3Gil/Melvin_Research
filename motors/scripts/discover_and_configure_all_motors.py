#!/usr/bin/env python3
"""
Discover and Configure All Motors
This script attempts to:
1. Discover motors with no IDs or default IDs using broadcast commands
2. Configure each motor with a unique CAN ID (1-15)
3. Verify configuration worked

Theory: If motors are daisy-chained and 5 work, all 15 are electrically connected.
The 10 missing motors are likely at default/unconfigured state (ID 0 or responding to all IDs).
"""

import serial
import sys
import time

# Command builders
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

def build_config_cmd(source_id, target_id, method=1):
    """
    Build configuration command to set motor CAN ID
    Multiple methods to try different command formats
    """
    cmd = bytearray([0x41, 0x54])  # AT
    
    if method == 1:
        # Method 1: 0x30 command
        cmd.extend([0x30, 0x07, 0xe8, source_id, 0x01, target_id, 0x00, 0x00, 0x00, 0x00])
    elif method == 2:
        # Method 2: 0x31 command
        cmd.extend([0x31, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x00, 0x00])
    elif method == 3:
        # Method 3: 0x32 command
        cmd.extend([0x32, 0x07, 0xe8, source_id, 0x00, target_id, 0x00, 0x00, 0x00, 0x00])
    elif method == 4:
        # Method 4: 0x40 command
        cmd.extend([0x40, 0x07, 0xe8, source_id, 0x02, target_id, 0x00, 0x00, 0x00, 0x00])
    elif method == 5:
        # Method 5: 0x50 command (config mode?)
        cmd.extend([0x50, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x00, 0x00])
    elif method == 6:
        # Method 6: 0x70 command (broadcast config?)
        cmd.extend([0x70, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    cmd.extend([0x0d, 0x0a])  # \r\n
    return bytes(cmd)

def send_command(ser, cmd):
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.05)

def send_command_with_response(ser, cmd, timeout=0.3):
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.05)
    
    response = b""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
        time.sleep(0.01)
    return response

def test_motor_responds(ser, can_id):
    """Test if a motor responds to a specific CAN ID"""
    response = send_command_with_response(ser, build_activate_cmd(can_id))
    if len(response) > 4:
        response2 = send_command_with_response(ser, build_load_params_cmd(can_id))
        send_command(ser, build_deactivate_cmd(can_id))
        return len(response2) > 4
    return False

def move_motor_test(ser, can_id, pulses=2):
    """Move motor to visually identify it"""
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    for i in range(pulses):
        send_command(ser, build_move_jog_cmd(can_id, 0.08, 1))
        time.sleep(0.4)
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.3)
    
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.2)

def discover_motors_broadcast(ser):
    """
    Try to discover motors using broadcast/default IDs
    Theory: Unconfigured motors might respond to ID 0 or 255
    """
    print("="*70)
    print("STEP 1: Discovering Motors via Broadcast")
    print("="*70)
    print()
    
    # Try broadcast IDs
    broadcast_ids = [0, 255]
    
    for bid in broadcast_ids:
        print(f"Trying broadcast ID {bid} (0x{bid:02X})...")
        
        # Send broadcast activate
        cmd = build_activate_cmd(bid)
        print(f"  Sending: {cmd.hex(' ')}")
        response = send_command_with_response(ser, cmd, timeout=0.5)
        
        if response:
            print(f"  Response: {response.hex(' ')}")
            print(f"  [OK] Got response from broadcast ID {bid}")
        else:
            print(f"  [NO RESPONSE]")
        
        time.sleep(0.3)
    
    print()
    print("Broadcast commands sent. Now scanning all IDs to see if any new motors respond...")
    print()
    
    # After broadcast, scan all IDs 1-127
    found_motors = []
    for can_id in range(1, 128):
        if test_motor_responds(ser, can_id):
            if can_id not in [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79]:
                print(f"  [NEW!] Found motor at CAN ID {can_id} (0x{can_id:02X})")
                found_motors.append(can_id)
    
    if found_motors:
        print(f"\n✓ Found {len(found_motors)} NEW motor(s) after broadcast!")
    else:
        print("\n✗ No new motors found after broadcast")
    
    return found_motors

def configure_motor_id(ser, source_id, target_id):
    """
    Attempt to configure a motor from source_id to target_id
    Tries multiple configuration command formats
    """
    print(f"\n{'='*70}")
    print(f"Configuring Motor: CAN ID {source_id} → {target_id}")
    print(f"{'='*70}")
    
    # Try all configuration methods
    for method in range(1, 7):
        cmd = build_config_cmd(source_id, target_id, method)
        print(f"  Method {method}: {cmd.hex(' ')}")
        response = send_command_with_response(ser, cmd, timeout=0.5)
        if response:
            print(f"    Response: {response.hex(' ')}")
        time.sleep(0.2)
    
    print(f"  [OK] Configuration commands sent")
    time.sleep(0.5)
    
    # Verify: Test if motor now responds to target_id
    print(f"\n  Verifying: Testing if motor responds to new ID {target_id}...")
    if test_motor_responds(ser, target_id):
        print(f"  ✓ Motor responds to new ID {target_id}")
        
        # Check if it still responds to old ID
        if source_id != target_id and test_motor_responds(ser, source_id):
            print(f"  ⚠️  Motor still responds to old ID {source_id} (configuration may not have worked)")
            return False
        else:
            print(f"  ✓ Motor no longer responds to old ID {source_id}")
            return True
    else:
        print(f"  ✗ Motor does NOT respond to new ID {target_id}")
        return False

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("  Discover and Configure All Motors")
    print("="*70)
    print()
    print(f"Port: {port}")
    print(f"Baud: {baud}")
    print()
    print("This script will:")
    print("  1. Try broadcast commands to discover unconfigured motors")
    print("  2. Attempt to configure motors with unique IDs (1-15)")
    print("  3. Verify configuration worked")
    print()
    print("="*70)
    
    input("\nPress Enter to start...")
    
    try:
        # Open serial port
        print(f"\nOpening serial port {port}...")
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("[OK] Serial port opened\n")
        
        # Send detection command
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        ser.flush()
        time.sleep(0.5)
        
        # Step 1: Discover motors via broadcast
        new_motors = discover_motors_broadcast(ser)
        
        # Step 2: Try to configure motors from their current IDs to unique IDs
        print("\n" + "="*70)
        print("STEP 2: Configuring Motors with Unique IDs")
        print("="*70)
        print()
        
        # Known responding ID ranges
        known_ranges = [
            (8, 15, "Motor 1"),
            (16, 20, "Motor 2"),
            (21, 30, "Motor 3"),
            (31, 39, "Motor 4?"),
            (64, 71, "Motor 8"),
            (72, 79, "Motor 9")
        ]
        
        print("Attempting to configure known motors to unique IDs...")
        print()
        
        # Try to configure each range to a single ID
        target_motor_num = 1
        configured_motors = {}
        
        for start_id, end_id, name in known_ranges:
            print(f"\n{'='*70}")
            print(f"Configuring {name} (currently responds to IDs {start_id}-{end_id})")
            print(f"Target: CAN ID {target_motor_num}")
            print(f"{'='*70}")
            
            # Try to configure from the first ID in the range
            success = configure_motor_id(ser, start_id, target_motor_num)
            
            if success:
                configured_motors[target_motor_num] = name
                print(f"\n✓ Successfully configured {name} to CAN ID {target_motor_num}")
            else:
                print(f"\n✗ Failed to configure {name} to CAN ID {target_motor_num}")
            
            target_motor_num += 1
            time.sleep(0.5)
        
        # Step 3: Final verification - scan all IDs 1-15
        print("\n" + "="*70)
        print("STEP 3: Final Verification")
        print("="*70)
        print()
        print("Scanning IDs 1-15 to see which motors respond...")
        print()
        
        final_motors = []
        for can_id in range(1, 16):
            if test_motor_responds(ser, can_id):
                final_motors.append(can_id)
                print(f"  ✓ Motor responds at CAN ID {can_id}")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        print(f"\nMotors responding to IDs 1-15: {len(final_motors)}")
        if final_motors:
            print(f"  IDs: {final_motors}")
        
        if len(final_motors) >= 10:
            print("\n✓ SUCCESS! Found 10+ motors responding to unique IDs!")
            print("Configuration appears to have worked!")
        elif len(final_motors) > 5:
            print(f"\n⚠️  PARTIAL SUCCESS: Found {len(final_motors)} motors")
            print("Some configuration worked, but not all motors found yet.")
        else:
            print(f"\n✗ Configuration did not work as expected")
            print(f"Only {len(final_motors)} motors responding to IDs 1-15")
            print("\nPossible reasons:")
            print("  1. Motors don't support software CAN ID configuration")
            print("  2. Configuration command format is incorrect")
            print("  3. Motors need manufacturer software to configure")
            print("  4. Motors need to be in special configuration mode")
            print("\nNext steps:")
            print("  - Check motor documentation for configuration method")
            print("  - Try RobStride Motor Studio software")
            print("  - Check for DIP switches/jumpers on motors")
        
        ser.close()
        print("\n[OK] Complete")
        
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

