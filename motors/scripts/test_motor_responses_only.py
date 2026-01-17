#!/usr/bin/env python3
"""
Test Motor Responses Only - NO MOVEMENT
This script tests motor communication (responses) without moving motors
Safe for testing - only sends enable/disable/query commands
"""
import serial
import time

PORT = '/dev/ttyUSB0'
BAUD = 921600

def build_activate_cmd(can_id):
    """Build L91 activate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    """Build L91 deactivate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    """Build L91 load params command"""
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd, timeout=0.25):
    """Send L91 command and get response"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.15)
    
    response = b""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
        time.sleep(0.02)
    
    return response

def test_motor_response(ser, motor_id):
    """
    Test motor response (NO MOVEMENT)
    Only tests communication - enable/disable/query
    """
    print(f"\nMotor ID {motor_id:3d} (0x{motor_id:02X}):")
    print("  " + "-"*60)
    
    # Test 1: Activate (enable)
    print("  Test 1: Enable motor...")
    cmd = build_activate_cmd(motor_id)
    response = send_command(ser, cmd, timeout=0.3)
    if len(response) > 4:
        print(f"    ✓ Responds: {len(response)} bytes")
        print(f"    Response hex: {response.hex(' ')[:80]}...")
    else:
        print(f"    ✗ No response")
        return False
    
    time.sleep(0.1)
    
    # Test 2: Load parameters (query)
    print("  Test 2: Load parameters (query)...")
    cmd = build_load_params_cmd(motor_id)
    response = send_command(ser, cmd, timeout=0.3)
    if len(response) > 4:
        print(f"    ✓ Responds: {len(response)} bytes")
        print(f"    Response hex: {response.hex(' ')[:80]}...")
    else:
        print(f"    ✗ No response")
    
    time.sleep(0.1)
    
    # Test 3: Deactivate (disable)
    print("  Test 3: Disable motor...")
    cmd = build_deactivate_cmd(motor_id)
    response = send_command(ser, cmd, timeout=0.3)
    if len(response) > 4:
        print(f"    ✓ Responds: {len(response)} bytes")
        print(f"    Response hex: {response.hex(' ')[:80]}...")
    else:
        print(f"    ✗ No response")
    
    print("  " + "-"*60)
    return True

def scan_and_test_responses(ser, start_id=1, end_id=127):
    """Scan for motors and test their responses (NO MOVEMENT)"""
    print(f"\nScanning for motors (IDs {start_id}-{end_id})...")
    print("NOTE: Only testing responses - NO MOVEMENT COMMANDS")
    print()
    
    found = []
    
    for motor_id in range(start_id, end_id + 1):
        # Quick enable test
        cmd = build_activate_cmd(motor_id)
        response = send_command(ser, cmd, timeout=0.2)
        
        if len(response) > 4:
            # Verify with load params
            cmd2 = build_load_params_cmd(motor_id)
            response2 = send_command(ser, cmd2, timeout=0.2)
            
            # Disable
            send_command(ser, build_deactivate_cmd(motor_id), timeout=0.1)
            time.sleep(0.05)
            
            if len(response2) > 4:
                found.append(motor_id)
                print(f"  ✓ Found motor at ID {motor_id:3d} (0x{motor_id:02X})")
    
    return found

def main():
    print("="*70)
    print("  TEST MOTOR RESPONSES ONLY - NO MOVEMENT")
    print("="*70)
    print()
    print("This script only tests motor communication (responses)")
    print("NO movement commands will be sent!")
    print()
    print(f"Port: {PORT}")
    print(f"Baud: {BAUD}")
    print()
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"✓ Connected to {PORT}")
        print()
    except Exception as e:
        print(f"✗ Failed to open port: {e}")
        print(f"\nMake sure USB-to-CAN adapter is connected to Jetson")
        print(f"Check port: ls -la /dev/ttyUSB*")
        return
    
    # Step 1: Quick scan
    print("="*70)
    print("  STEP 1: QUICK SCAN")
    print("="*70)
    
    motor_ids = scan_and_test_responses(ser, 1, 127)
    
    if not motor_ids:
        print("\n✗ No motors found!")
        ser.close()
        return
    
    print(f"\n✓ Found {len(motor_ids)} motor ID(s)")
    
    # Step 2: Detailed response testing
    print()
    print("="*70)
    print("  STEP 2: DETAILED RESPONSE TESTING")
    print("="*70)
    print()
    print("Testing detailed responses for each motor...")
    print("NOTE: Only enable/disable/query commands - NO MOVEMENT")
    print()
    
    # Test primary IDs (first ID from each group)
    # Group consecutive IDs
    if motor_ids:
        groups = []
        current_group = [motor_ids[0]]
        for i in range(1, len(motor_ids)):
            if motor_ids[i] == motor_ids[i-1] + 1:
                current_group.append(motor_ids[i])
            else:
                groups.append(current_group)
                current_group = [motor_ids[i]]
        groups.append(current_group)
        
        # Test primary ID from each group
        for i, group in enumerate(groups, 1):
            primary_id = group[0]
            print(f"\nMotor Group {i} (Primary ID: {primary_id}):")
            test_motor_response(ser, primary_id)
            time.sleep(0.2)
    
    print()
    print("="*70)
    print("  SUMMARY")
    print("="*70)
    print()
    print(f"✓ Tested {len(motor_ids)} motor ID(s)")
    print(f"✓ All tests were communication-only (NO MOVEMENT)")
    print(f"✓ Motors were enabled and disabled (no movement commands)")
    print()
    print("Safe testing complete!")
    print()
    
    ser.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

