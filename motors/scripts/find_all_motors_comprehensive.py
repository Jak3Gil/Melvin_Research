#!/usr/bin/env python3
"""
Comprehensive Motor Discovery Script
Tests all methods to find and activate all 15 motors:

1. Test ALL CAN IDs (1-31) with extended timeouts
2. Try broadcast/universal commands
3. Try activation sequences on all IDs
4. Try wake/enable commands
5. Test with different command formats
"""

import serial
import sys
import time
import argparse

# L91 Protocol Constants
L91_DETECT_CMD = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])  # AT+AT\r\n

def build_activate_cmd(can_id):
    """AT 00 07 e8 <can_id> 01 00 0d 0a"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    """AT 00 07 e8 <can_id> 00 00 0d 0a"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    """AT 20 07 e8 <can_id> 08 00 c4 00 00 00 00 00 00 0d 0a"""
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_broadcast_activate():
    """Try broadcast activate (ID 0 or 0xFF)"""
    # Try CAN ID 0 (broadcast)
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00, 0x01, 0x00, 0x0d, 0x0a])

def build_wake_command():
    """Try wake/enable command (various formats)"""
    # Format 1: Wake all
    return bytes([0x41, 0x54, 0xFF, 0x07, 0xe8, 0x00, 0x01, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd, description="Command", timeout=0.5, show_response=True):
    """Send L91 command and read response with extended timeout"""
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.2)  # Wait for command to be sent
        
        # Extended timeout for responses
        response = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.05)  # Longer delay between reads
            else:
                time.sleep(0.05)
        
        if response and show_response:
            print(f"    Response: {response.hex(' ')}")
        return response
    except Exception as e:
        if show_response:
            print(f"    Error: {e}")
        return b""

def test_can_id_comprehensive(ser, can_id):
    """Comprehensive test for a CAN ID"""
    print(f"  Testing CAN ID {can_id} (0x{can_id:02X})...")
    
    # Test 1: Activate
    response1 = send_command(ser, build_activate_cmd(can_id), timeout=0.8, show_response=False)
    time.sleep(0.3)
    
    # Test 2: Load params
    response2 = send_command(ser, build_load_params_cmd(can_id), timeout=0.8, show_response=False)
    time.sleep(0.3)
    
    # Check if we got meaningful responses
    has_response = (len(response1) > 4) or (len(response2) > 4)
    
    if has_response:
        # Try a small movement to verify motor is active
        print(f"    [RESPONSE] Motor responded! Testing movement...")
        # Build move command
        speed_val = int(0x8000 + (0.05 * 3283.0))  # Small forward movement
        move_cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                              0x00, 0x00, 0x07, 1])
        move_cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
        send_command(ser, bytes(move_cmd), timeout=0.5, show_response=False)
        time.sleep(0.5)
        # Stop
        speed_val = 0x7fff
        stop_cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                              0x00, 0x00, 0x07, 0])
        stop_cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
        send_command(ser, bytes(stop_cmd), timeout=0.5, show_response=False)
        time.sleep(0.2)
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.5, show_response=False)
        return True
    else:
        return False

def method_1_test_all_ids(ser, start_id=1, end_id=31):
    """Method 1: Test ALL CAN IDs systematically"""
    print("\n" + "="*70)
    print("METHOD 1: Testing ALL CAN IDs (1-31) with Extended Timeouts")
    print("="*70)
    
    found = []
    for can_id in range(start_id, end_id + 1):
        if test_can_id_comprehensive(ser, can_id):
            found.append(can_id)
            print(f"    ✓ Found motor at CAN ID {can_id}")
        time.sleep(0.2)
    
    return found

def method_2_broadcast_commands(ser):
    """Method 2: Try broadcast/universal commands"""
    print("\n" + "="*70)
    print("METHOD 2: Trying Broadcast/Universal Commands")
    print("="*70)
    
    print("  Attempting broadcast activate (CAN ID 0)...")
    response = send_command(ser, build_broadcast_activate(), timeout=1.0)
    
    print("  Attempting wake command...")
    response2 = send_command(ser, build_wake_command(), timeout=1.0)
    
    # After broadcast, test all IDs again
    print("\n  Testing all IDs again after broadcast commands...")
    time.sleep(0.5)
    found = []
    for can_id in range(1, 32):
        if test_can_id_comprehensive(ser, can_id):
            found.append(can_id)
        time.sleep(0.1)
    
    return found

def method_3_activation_sequence(ser):
    """Method 3: Try activation sequence on all IDs"""
    print("\n" + "="*70)
    print("METHOD 3: Activation Sequence on All IDs")
    print("="*70)
    print("  Activating all IDs 1-31, then testing for responses...")
    
    # Step 1: Activate all IDs
    for can_id in range(1, 32):
        send_command(ser, build_activate_cmd(can_id), timeout=0.3, show_response=False)
        time.sleep(0.05)  # Small delay between activations
    
    time.sleep(0.5)
    
    # Step 2: Load params on all IDs
    for can_id in range(1, 32):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.3, show_response=False)
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    # Step 3: Test all IDs for responses
    found = []
    for can_id in range(1, 32):
        # Quick test - just check for response
        response = send_command(ser, build_activate_cmd(can_id), timeout=0.5, show_response=False)
        if len(response) > 4:
            found.append(can_id)
        time.sleep(0.1)
    
    # Cleanup - deactivate all
    for can_id in range(1, 32):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.2, show_response=False)
        time.sleep(0.02)
    
    return found

def method_4_detect_command(ser):
    """Method 4: Use AT+AT detect command and analyze response"""
    print("\n" + "="*70)
    print("METHOD 4: Analyzing AT+AT Detection Command Response")
    print("="*70)
    
    print("  Sending AT+AT detection command...")
    response = send_command(ser, L91_DETECT_CMD, timeout=1.0)
    
    if response:
        print(f"  Detection response: {response.hex(' ')}")
        print(f"  Response length: {len(response)} bytes")
        
        # Try to parse response for motor information
        # Response might contain motor count or IDs
        print("  Analyzing response for motor information...")
    
    # After detect, test all IDs
    print("\n  Testing all IDs after detection command...")
    found = []
    for can_id in range(1, 32):
        if test_can_id_comprehensive(ser, can_id):
            found.append(can_id)
        time.sleep(0.1)
    
    return found

def method_5_alternative_formats(ser):
    """Method 5: Try alternative command formats"""
    print("\n" + "="*70)
    print("METHOD 5: Testing Alternative Command Formats")
    print("="*70)
    
    found = []
    
    # Try different activate command formats
    print("  Trying alternative activate formats...")
    for can_id in range(1, 32):
        # Format variations
        formats = [
            # Standard format
            bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a]),
            # With extended data
            bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x08, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a]),
            # Alternative format
            bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x01, 0x00, 0x0d, 0x0a]),
        ]
        
        for fmt_cmd in formats:
            response = send_command(ser, fmt_cmd, timeout=0.5, show_response=False)
            if len(response) > 4:
                found.append(can_id)
                print(f"    ✓ Found motor at CAN ID {can_id} with alternative format")
                break
        time.sleep(0.05)
    
    return found

def main():
    parser = argparse.ArgumentParser(description='Comprehensive Motor Discovery')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('baud', type=int, nargs='?', default=921600, help='Baud rate')
    parser.add_argument('--skip-methods', type=str, help='Comma-separated list of methods to skip (1-5)')
    
    args = parser.parse_args()
    
    skip_methods = []
    if args.skip_methods:
        skip_methods = [int(x.strip()) for x in args.skip_methods.split(',')]
    
    print("="*70)
    print("COMPREHENSIVE MOTOR DISCOVERY")
    print("="*70)
    print(f"\nPort: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print(f"\nThis will test all methods to find all 15 motors:")
    print("  1. Test ALL CAN IDs (1-31) with extended timeouts")
    print("  2. Try broadcast/universal commands")
    print("  3. Try activation sequence on all IDs")
    print("  4. Analyze AT+AT detection command")
    print("  5. Try alternative command formats")
    print("="*70)
    
    try:
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
        print("\n[OK] Serial port opened\n")
        
        all_found = set()
        
        # Method 1: Test all IDs
        if 1 not in skip_methods:
            found1 = method_1_test_all_ids(ser)
            all_found.update(found1)
            print(f"\n[Method 1] Found {len(found1)} motor(s): {sorted(found1)}")
        
        # Method 2: Broadcast commands
        if 2 not in skip_methods:
            found2 = method_2_broadcast_commands(ser)
            all_found.update(found2)
            print(f"\n[Method 2] Found {len(found2)} motor(s): {sorted(found2)}")
        
        # Method 3: Activation sequence
        if 3 not in skip_methods:
            found3 = method_3_activation_sequence(ser)
            all_found.update(found3)
            print(f"\n[Method 3] Found {len(found3)} motor(s): {sorted(found3)}")
        
        # Method 4: Detect command
        if 4 not in skip_methods:
            found4 = method_4_detect_command(ser)
            all_found.update(found4)
            print(f"\n[Method 4] Found {len(found4)} motor(s): {sorted(found4)}")
        
        # Method 5: Alternative formats
        if 5 not in skip_methods:
            found5 = method_5_alternative_formats(ser)
            all_found.update(found5)
            print(f"\n[Method 5] Found {len(found5)} motor(s): {sorted(found5)}")
        
        # Final summary
        print("\n" + "="*70)
        print("FINAL RESULTS")
        print("="*70)
        all_found_list = sorted(list(all_found))
        print(f"\nTotal unique motors found: {len(all_found_list)}")
        print(f"CAN IDs responding: {all_found_list}")
        
        if len(all_found_list) >= 15:
            print("\n[SUCCESS] All 15 motors found!")
        elif len(all_found_list) > 2:
            print(f"\n[PROGRESS] Found {len(all_found_list)} motors (expected 15)")
            print(f"Still missing {15 - len(all_found_list)} motors")
        else:
            print(f"\n[LIMITED] Only found {len(all_found_list)} motors")
            print("Motors may need configuration or different approach")
        
        ser.close()
        print("\n[OK] Discovery complete")
        
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

