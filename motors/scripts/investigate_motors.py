#!/usr/bin/env python3
"""
Comprehensive Motor Investigation
Systematically test and diagnose why only 2 motors are responding
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
        time.sleep(0.05)
        return True
    except:
        return False

def test_can_id_movement(ser, can_id):
    """Test if a CAN ID produces movement"""
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    send_command(ser, build_move_jog_cmd(can_id, 0.05, 1))
    time.sleep(0.5)
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
    time.sleep(0.2)
    
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.2)

def quick_scan(ser):
    """Quick scan of all IDs to see response patterns"""
    print("\n" + "="*70)
    print("QUICK SCAN - Testing all CAN IDs 1-31")
    print("="*70)
    print("\nThis will quickly test all IDs. Watch for ANY motor movements.")
    print("Note which physical motor(s) move for each ID range.\n")
    
    input("Press Enter to start quick scan...")
    
    results = {}
    
    # Test in ranges to see patterns
    ranges = [
        (1, 7, "IDs 1-7"),
        (8, 15, "IDs 8-15"),
        (16, 22, "IDs 16-22"),
        (23, 31, "IDs 23-31"),
    ]
    
    for start, end, desc in ranges:
        print(f"\n{'='*70}")
        print(f"Testing {desc}")
        print(f"{'='*70}")
        
        for can_id in range(start, end + 1):
            print(f"  Testing ID {can_id:2d} (0x{can_id:02X})...", end=' ', flush=True)
            test_can_id_movement(ser, can_id)
            time.sleep(0.2)
        
        print(f"\n  Which physical motor(s) moved in range {desc}?")
        motor_input = input("  Enter motor number(s) or 'none': ").strip()
        results[desc] = motor_input
    
    return results

def detailed_test(ser, can_id_range):
    """Detailed test of a specific ID range"""
    print(f"\n{'='*70}")
    print(f"Detailed Test of CAN IDs {can_id_range[0]}-{can_id_range[1]}")
    print(f"{'='*70}")
    
    motor_responses = {}
    
    for can_id in range(can_id_range[0], can_id_range[1] + 1):
        print(f"\nTesting CAN ID {can_id} (0x{can_id:02X})...")
        print("Watch which physical motor moves...")
        input("Press Enter to test...")
        
        test_can_id_movement(ser, can_id)
        
        motor_num = input("Which physical motor moved? (1-15, 'none', or 'same'): ").strip().lower()
        if motor_num and motor_num != 'none':
            if motor_num == 'same' and motor_responses:
                motor_num = list(motor_responses.values())[-1]
            motor_responses[can_id] = motor_num
    
    return motor_responses

def test_all_motors_simultaneously(ser):
    """Test if multiple motors can be activated simultaneously"""
    print("\n" + "="*70)
    print("SIMULTANEOUS ACTIVATION TEST")
    print("="*70)
    print("\nTesting if we can activate multiple motors at the same time")
    print("to see if more motors become active when addressed together.")
    
    input("\nPress Enter to start...")
    
    # Try activating multiple IDs at once
    print("\nActivating IDs 8, 9, 10 simultaneously...")
    send_command(ser, build_activate_cmd(8))
    send_command(ser, build_activate_cmd(9))
    send_command(ser, build_activate_cmd(10))
    time.sleep(0.3)
    
    send_command(ser, build_load_params_cmd(8))
    send_command(ser, build_load_params_cmd(9))
    send_command(ser, build_load_params_cmd(10))
    time.sleep(0.3)
    
    print("Moving all three...")
    send_command(ser, build_move_jog_cmd(8, 0.05, 1))
    send_command(ser, build_move_jog_cmd(9, 0.05, 1))
    send_command(ser, build_move_jog_cmd(10, 0.05, 1))
    time.sleep(1.0)
    
    send_command(ser, build_move_jog_cmd(8, 0.0, 0))
    send_command(ser, build_move_jog_cmd(9, 0.0, 0))
    send_command(ser, build_move_jog_cmd(10, 0.0, 0))
    
    send_command(ser, build_deactivate_cmd(8))
    send_command(ser, build_deactivate_cmd(9))
    send_command(ser, build_deactivate_cmd(10))
    
    response = input("\nHow many different physical motors moved? (1, 2, 3, etc.): ")
    return response

def diagnostic_summary(quick_results, detailed_results, simultaneous_result):
    """Provide diagnostic summary and recommendations"""
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    print("\nQuick Scan Results:")
    for range_desc, motor_info in quick_results.items():
        print(f"  {range_desc}: {motor_info}")
    
    if detailed_results:
        print("\nDetailed Test Results:")
        by_motor = {}
        for can_id, motor_num in detailed_results.items():
            if motor_num not in by_motor:
                by_motor[motor_num] = []
            by_motor[motor_num].append(can_id)
        
        for motor_num in sorted(by_motor.keys()):
            can_ids = sorted(by_motor[motor_num])
            print(f"  Physical Motor {motor_num}: CAN IDs {can_ids}")
        
        print(f"\n  Total motors responding: {len(by_motor)}")
    
    if simultaneous_result:
        print(f"\nSimultaneous activation: {simultaneous_result} motor(s) moved")
    
    print("\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)
    
    print("\nPossible reasons only 2 motors respond:")
    print("\n1. POWER/ELECTRICAL:")
    print("   - Only 2 motors are powered on")
    print("   - Other motors don't have power")
    print("   - Power supply issue")
    print("\n2. CAN BUS CONNECTION:")
    print("   - Only 2 motors connected to CAN bus")
    print("   - Other motors not wired to CAN-H/CAN-L")
    print("   - CAN bus wiring issue")
    print("   - Missing termination resistors")
    print("\n3. MOTOR CONFIGURATION:")
    print("   - Other motors need to be enabled/activated")
    print("   - Motors in sleep/standby mode")
    print("   - Motors need initialization")
    print("\n4. CAN BUS SEGMENTS:")
    print("   - Motors on different CAN bus segments")
    print("   - CAN bus router/switch configuration")
    print("   - Multiple CAN buses")
    print("\n5. ADDRESSING SCHEME:")
    print("   - Motors use different addressing (extended IDs, etc.)")
    print("   - Motors on different base addresses")
    print("   - Motor grouping/pairing")
    
    print("\n" + "="*70)
    print("RECOMMENDED ACTIONS")
    print("="*70)
    print("\n1. PHYSICAL CHECK:")
    print("   - Verify all 15 motors have power LEDs on")
    print("   - Check CAN bus connections (CAN-H, CAN-L, GND) for all motors")
    print("   - Verify termination resistors (120Ω at both ends)")
    print("\n2. TEST INDIVIDUAL MOTORS:")
    print("   - Disconnect motors one at a time to isolate issues")
    print("   - Test motors individually")
    print("\n3. CHECK MOTOR DOCUMENTATION:")
    print("   - Do motors need activation/enabling commands?")
    print("   - Are motors in a specific mode/state?")
    print("   - Do motors need initialization sequence?")
    print("\n4. CAN BUS DIAGNOSTICS:")
    print("   - Check CAN bus voltage levels")
    print("   - Verify CAN bus bitrate matches motors")
    print("   - Check for CAN bus errors")

def main():
    port = "COM3"
    baud = 921600
    
    print("="*70)
    print("COMPREHENSIVE MOTOR INVESTIGATION")
    print("="*70)
    print("\nThis tool will help diagnose why only 2 motors are responding")
    print("when you expect 15 motors to be active.")
    print("\nTests included:")
    print("  1. Quick scan of all CAN IDs")
    print("  2. Detailed test of specific ranges")
    print("  3. Simultaneous activation test")
    print("  4. Diagnostic analysis")
    
    input("\nPress Enter to start investigation...")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened")
        
        quick_results = {}
        detailed_results = {}
        simultaneous_result = None
        
        # Test 1: Quick scan
        quick_results = quick_scan(ser)
        
        # Test 2: Detailed test of known ranges
        print("\n" + "="*70)
        print("Would you like to do a detailed test of specific ID ranges?")
        response = input("(y/n): ").strip().lower()
        
        if response == 'y':
            print("\nWhich range to test in detail?")
            print("  1. IDs 8-15 (currently Motor 1)")
            print("  2. IDs 16-22 (currently Motor 2)")
            print("  3. IDs 1-7 (unknown)")
            print("  4. IDs 23-31 (unknown)")
            choice = input("Enter choice (1-4): ").strip()
            
            ranges = {
                '1': (8, 15),
                '2': (16, 22),
                '3': (1, 7),
                '4': (23, 31),
            }
            
            if choice in ranges:
                detailed_results = detailed_test(ser, ranges[choice])
        
        # Test 3: Simultaneous activation
        print("\n" + "="*70)
        response = input("Test simultaneous activation? (y/n): ").strip().lower()
        if response == 'y':
            simultaneous_result = test_all_motors_simultaneously(ser)
        
        # Summary and diagnosis
        diagnostic_summary(quick_results, detailed_results, simultaneous_result)
        
        ser.close()
        print("\n[OK] Investigation complete")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

