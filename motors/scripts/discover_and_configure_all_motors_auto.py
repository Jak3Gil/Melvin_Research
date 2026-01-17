#!/usr/bin/env python3
"""
Discover and Configure All Motors - AUTOMATIC VERSION
This script automatically:
1. Discovers motors with no IDs or default IDs using broadcast commands
2. Attempts to configure each motor with a unique CAN ID (1-15)
3. Verifies configuration worked

NO USER INPUT REQUIRED - Runs completely automatically
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

def build_config_cmd(source_id, target_id, method=1):
    """Build configuration command to set motor CAN ID"""
    cmd = bytearray([0x41, 0x54])  # AT
    
    if method == 1:
        cmd.extend([0x30, 0x07, 0xe8, source_id, 0x01, target_id, 0x00, 0x00, 0x00, 0x00])
    elif method == 2:
        cmd.extend([0x31, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x00, 0x00])
    elif method == 3:
        cmd.extend([0x32, 0x07, 0xe8, source_id, 0x00, target_id, 0x00, 0x00, 0x00, 0x00])
    elif method == 4:
        cmd.extend([0x40, 0x07, 0xe8, source_id, 0x02, target_id, 0x00, 0x00, 0x00, 0x00])
    elif method == 5:
        cmd.extend([0x50, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x00, 0x00])
    elif method == 6:
        cmd.extend([0x70, 0x07, 0xe8, source_id, target_id, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    cmd.extend([0x0d, 0x0a])
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

def discover_motors_broadcast(ser):
    """Try to discover motors using broadcast/default IDs"""
    print("="*70)
    print("STEP 1: Discovering Motors via Broadcast")
    print("="*70)
    print()
    
    # Try broadcast IDs
    broadcast_ids = [0, 255]
    
    for bid in broadcast_ids:
        print(f"Trying broadcast ID {bid} (0x{bid:02X})...")
        cmd = build_activate_cmd(bid)
        response = send_command_with_response(ser, cmd, timeout=0.5)
        
        if response:
            print(f"  ✓ Got response: {response.hex(' ')}")
        else:
            print(f"  - No response")
        time.sleep(0.3)
    
    print("\nScanning for new motors after broadcast...")
    
    # Known motors to skip
    known_ids = set(range(8, 40)) | set(range(64, 80))
    
    # Scan all IDs 1-127
    found_motors = []
    for can_id in range(1, 128):
        if can_id not in known_ids:
            if test_motor_responds(ser, can_id):
                print(f"  ✓ NEW motor found at CAN ID {can_id}")
                found_motors.append(can_id)
    
    if found_motors:
        print(f"\n✓ Found {len(found_motors)} NEW motor(s)!")
    else:
        print("\n- No new motors found after broadcast")
    
    return found_motors

def configure_motor_id(ser, source_id, target_id):
    """Attempt to configure a motor from source_id to target_id"""
    print(f"\nConfiguring: CAN ID {source_id} → {target_id}")
    
    # Try all configuration methods
    for method in range(1, 7):
        cmd = build_config_cmd(source_id, target_id, method)
        send_command_with_response(ser, cmd, timeout=0.3)
        time.sleep(0.1)
    
    time.sleep(0.5)
    
    # Verify
    if test_motor_responds(ser, target_id):
        # Check if it still responds to old ID
        if source_id != target_id and test_motor_responds(ser, source_id):
            print(f"  ⚠️  Still responds to old ID {source_id}")
            return False
        else:
            print(f"  ✓ Successfully configured to ID {target_id}")
            return True
    else:
        print(f"  ✗ Does not respond to new ID {target_id}")
        return False

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("  Discover and Configure All Motors (AUTOMATIC)")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}")
    print("\nStarting in 2 seconds...\n")
    time.sleep(2)
    
    try:
        # Open serial port
        print(f"Opening serial port {port}...")
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("✓ Serial port opened\n")
        
        # Send detection command
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        ser.flush()
        time.sleep(0.5)
        
        # Step 1: Discover motors via broadcast
        new_motors = discover_motors_broadcast(ser)
        
        # Step 2: Configure known motor ranges to unique IDs
        print("\n" + "="*70)
        print("STEP 2: Configuring Motors with Unique IDs")
        print("="*70)
        print()
        
        # Known responding ID ranges
        known_ranges = [
            (8, 15, "Motor 1"),
            (16, 20, "Motor 2"),
            (21, 30, "Motor 3"),
            (31, 39, "Motor 4"),
            (64, 71, "Motor 8"),
            (72, 79, "Motor 9")
        ]
        
        configured_count = 0
        
        for idx, (start_id, end_id, name) in enumerate(known_ranges, 1):
            target_id = idx
            print(f"\n[{idx}/6] {name} (IDs {start_id}-{end_id}) → Target ID {target_id}")
            
            success = configure_motor_id(ser, start_id, target_id)
            if success:
                configured_count += 1
            
            time.sleep(0.3)
        
        # Step 3: Final verification
        print("\n" + "="*70)
        print("STEP 3: Final Verification - Scanning IDs 1-15")
        print("="*70)
        print()
        
        final_motors = []
        for can_id in range(1, 16):
            if test_motor_responds(ser, can_id):
                final_motors.append(can_id)
                print(f"  ✓ Motor responds at CAN ID {can_id}")
        
        # Step 4: Check if old ranges still respond
        print("\n" + "="*70)
        print("STEP 4: Checking Old ID Ranges")
        print("="*70)
        print()
        
        old_ranges_still_active = []
        for start_id, end_id, name in known_ranges:
            if test_motor_responds(ser, start_id):
                print(f"  ⚠️  {name} still responds to old ID {start_id}")
                old_ranges_still_active.append(name)
            else:
                print(f"  ✓ {name} no longer responds to old ID {start_id}")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        print(f"\nConfiguration attempts: {configured_count}/6 reported success")
        print(f"Motors responding to IDs 1-15: {len(final_motors)}")
        if final_motors:
            print(f"  IDs: {final_motors}")
        
        print(f"\nOld ID ranges still active: {len(old_ranges_still_active)}")
        if old_ranges_still_active:
            print(f"  Motors: {', '.join(old_ranges_still_active)}")
        
        print("\n" + "="*70)
        
        if len(final_motors) >= 10:
            print("✓ SUCCESS! Found 10+ motors responding to unique IDs!")
            print("Configuration worked!")
        elif len(final_motors) > 5:
            print(f"⚠️  PARTIAL SUCCESS: Found {len(final_motors)} motors at IDs 1-15")
            print("Some configuration worked, but not all motors found yet.")
        else:
            print(f"✗ Configuration did not work")
            print(f"Only {len(final_motors)} motors responding to IDs 1-15")
            print("\nLikely reasons:")
            print("  1. Motors don't support software CAN ID configuration")
            print("  2. Need manufacturer software (RobStride Motor Studio)")
            print("  3. Need special configuration mode/procedure")
            print("  4. Motors have hardware ID switches")
            print("\nRecommendation:")
            print("  - Contact RobStride for CAN ID configuration method")
            print("  - Check motor documentation")
            print("  - Look for DIP switches/jumpers on motors")
        
        ser.close()
        print("\n[COMPLETE]")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if 'ser' in locals():
            ser.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

