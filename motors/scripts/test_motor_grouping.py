#!/usr/bin/env python3
"""
Test Motor Grouping Behavior
Determines if motors are configured in groups and how the grouping works
"""

import serial
import sys
import time
import argparse

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

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

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd, timeout=0.3):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.05)  # Reduced wait
        response = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.01)  # Faster polling
        return len(response) > 4
    except:
        return False

def test_1_power_cycle_behavior(ser):
    """Test 1: Does grouping persist after commands stop?"""
    print("="*70)
    print("TEST 1: Grouping Persistence")
    print("="*70)
    print("Testing if motor groups persist after deactivating...")
    
    # First, establish known state with activation sequence
    print("Step 1: Run activation sequence...")
    for can_id in range(1, 32):
        send_command(ser, build_activate_cmd(can_id), timeout=0.2)
        time.sleep(0.01)
    time.sleep(0.2)
    
    for can_id in range(1, 32):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.2)
        time.sleep(0.01)
    time.sleep(0.2)
    
    print("Step 2: Test which IDs respond...")
    responding_before = []
    for can_id in range(1, 32):
        if send_command(ser, build_activate_cmd(can_id), timeout=0.2):
            responding_before.append(can_id)
        time.sleep(0.05)
    
    print(f"  IDs responding: {responding_before}")
    
    # Deactivate all
    print("Step 3: Deactivate all motors...")
    for can_id in range(1, 32):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.5)  # Reduced wait
    
    # Test again
    print("Step 4: Test again after deactivation...")
    responding_after = []
    for can_id in range(1, 32):
        if send_command(ser, build_activate_cmd(can_id), timeout=0.2):
            responding_after.append(can_id)
        time.sleep(0.05)
    
    print(f"  IDs responding: {responding_after}")
    
    if responding_before == responding_after:
        print("\n[RESULT] Grouping PERSISTS after deactivation")
    else:
        print("\n[RESULT] Grouping CHANGES after deactivation")
    
    return responding_before, responding_after

def test_2_selective_activation(ser):
    """Test 2: Can we activate only specific ID ranges?"""
    print("\n" + "="*70)
    print("TEST 2: Selective Activation")
    print("="*70)
    print("Testing if activating only specific ID ranges changes grouping...")
    
    # Deactivate all first
    print("Deactivating all...")
    for can_id in range(1, 100):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.005)
    time.sleep(0.3)
    
    # Test A: Activate only IDs 8-15 (Motor 1 range)
    print("\nTest A: Activate only IDs 8-15...")
    for can_id in range(8, 16):
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    for can_id in range(8, 16):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    responding_a = []
    for can_id in range(1, 32):
        if send_command(ser, build_activate_cmd(can_id), timeout=0.2):
            responding_a.append(can_id)
        time.sleep(0.05)
    
    print(f"  IDs responding: {responding_a}")
    
    # Test B: Activate only IDs 16-20 (Motor 2 range)
    print("\nTest B: Activate only IDs 16-20...")
    for can_id in range(1, 100):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.005)
    time.sleep(0.3)
    
    for can_id in range(16, 21):
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    for can_id in range(16, 21):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    responding_b = []
    for can_id in range(1, 32):
        if send_command(ser, build_activate_cmd(can_id), timeout=0.2):
            responding_b.append(can_id)
        time.sleep(0.05)
    
    print(f"  IDs responding: {responding_b}")
    
    if responding_a != responding_b:
        print("\n[RESULT] Selective activation changes grouping")
    else:
        print("\n[RESULT] Selective activation produces same grouping")
    
    return responding_a, responding_b

def test_3_sequential_vs_simultaneous(ser):
    """Test 3: Does order of activation matter?"""
    print("\n" + "="*70)
    print("TEST 3: Sequential vs Simultaneous Activation")
    print("="*70)
    
    # Deactivate all
    print("Deactivating all...")
    for can_id in range(1, 100):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.005)
    time.sleep(0.3)
    
    # Test A: Activate sequentially (one at a time with delays)
    print("\nTest A: Sequential activation (slow)...")
    for can_id in range(1, 32):
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.1)  # Medium delay
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.1)
    
    time.sleep(0.2)
    
    responding_sequential = []
    for can_id in range(1, 32):
        if send_command(ser, build_activate_cmd(can_id), timeout=0.2):
            responding_sequential.append(can_id)
        time.sleep(0.05)
    
    print(f"  IDs responding: {responding_sequential}")
    
    # Test B: Activate rapidly (like successful sequence)
    print("\nTest B: Rapid activation (fast)...")
    for can_id in range(1, 100):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.005)
    time.sleep(0.3)
    
    for can_id in range(1, 32):
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    for can_id in range(1, 32):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    responding_rapid = []
    for can_id in range(1, 32):
        if send_command(ser, build_activate_cmd(can_id), timeout=0.2):
            responding_rapid.append(can_id)
        time.sleep(0.05)
    
    print(f"  IDs responding: {responding_rapid}")
    
    if responding_sequential != responding_rapid:
        print("\n[RESULT] Activation speed MATTERS")
    else:
        print("\n[RESULT] Activation speed doesn't matter")
    
    return responding_sequential, responding_rapid

def test_4_id_range_boundaries(ser):
    """Test 4: Find exact boundaries of motor ID ranges"""
    print("\n" + "="*70)
    print("TEST 4: ID Range Boundaries")
    print("="*70)
    print("Finding exact boundaries where motors change...")
    
    # Use rapid activation sequence
    print("Activating IDs 1-100...")
    for can_id in range(1, 100):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.005)
    time.sleep(0.2)
    
    for can_id in range(1, 100):
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    for can_id in range(1, 100):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    # Test each ID to see which respond
    print("Testing IDs 1-100...")
    responding_ids = []
    
    for can_id in range(1, 101):
        if send_command(ser, build_activate_cmd(can_id), timeout=0.2):
            responding_ids.append(can_id)
        time.sleep(0.03)
    
    print(f"  Found {len(responding_ids)} responding IDs")
    
    # Group into ranges
    ranges = []
    if responding_ids:
        range_start = responding_ids[0]
        range_end = responding_ids[0]
        
        for can_id in responding_ids[1:]:
            if can_id == range_end + 1:
                range_end = can_id
            else:
                ranges.append((range_start, range_end))
                range_start = can_id
                range_end = can_id
        ranges.append((range_start, range_end))
    
    print(f"\n  ID ranges found: {len(ranges)}")
    for start, end in ranges:
        count = end - start + 1
        print(f"    IDs {start}-{end} ({count} IDs)")
    
    return ranges

def main():
    parser = argparse.ArgumentParser(description='Test Motor Grouping Behavior')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('baud', type=int, nargs='?', default=921600, help='Baud rate')
    parser.add_argument('--test', type=int, help='Run specific test (1-4), or all if not specified')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Motor Grouping Behavior Analysis")
    print("="*70)
    print(f"\nPort: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print("\nThis will test various scenarios to determine if motors are grouped:")
    print("  1. Does grouping persist after deactivation?")
    print("  2. Can selective activation change grouping?")
    print("  3. Does activation speed/order matter?")
    print("  4. What are the exact ID range boundaries?")
    print("="*70)
    
    ser = serial.Serial(args.port, args.baud, timeout=0.1)
    time.sleep(0.5)
    print("\n[OK] Serial port opened\n")
    
    results = {}
    
    if not args.test or args.test == 1:
        results['persistence'] = test_1_power_cycle_behavior(ser)
    
    if not args.test or args.test == 2:
        results['selective'] = test_2_selective_activation(ser)
    
    if not args.test or args.test == 3:
        results['timing'] = test_3_sequential_vs_simultaneous(ser)
    
    if not args.test or args.test == 4:
        results['boundaries'] = test_4_id_range_boundaries(ser)
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY & CONCLUSIONS")
    print("="*70)
    
    if 'persistence' in results:
        before, after = results['persistence']
        if before == after:
            print("\n✓ Grouping is STABLE (persists after deactivation)")
        else:
            print("\n✗ Grouping is VOLATILE (changes after deactivation)")
    
    if 'selective' in results:
        a, b = results['selective']
        if a != b:
            print("\n✓ Grouping is SEQUENCE-DEPENDENT")
        else:
            print("\n✗ Grouping is NOT sequence-dependent")
    
    if 'timing' in results:
        seq, rapid = results['timing']
        if seq != rapid:
            print("\n✓ Grouping is TIMING-DEPENDENT (rapid vs slow matters)")
        else:
            print("\n✗ Grouping is NOT timing-dependent")
    
    if 'boundaries' in results:
        ranges = results['boundaries']
        print(f"\n✓ Found {len(ranges)} ID range(s)")
        for start, end in ranges:
            print(f"  Range: IDs {start}-{end} ({end-start+1} IDs)")
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    # Provide recommendations based on results
    if 'persistence' in results and 'timing' in results:
        before, after = results['persistence']
        seq, rapid = results['timing']
        
        if before == after and seq == rapid:
            print("\nMotors appear to be PRE-CONFIGURED in groups")
            print("  - Grouping is stable and not sequence-dependent")
            print("  - Motors likely have hardware/EEPROM configuration")
            print("  - Need to reconfigure each motor individually")
        elif before != after or seq != rapid:
            print("\nMotors appear to be STATE-DEPENDENT")
            print("  - Grouping changes based on activation sequence")
            print("  - This is software/firmware behavior, not hardware config")
            print("  - Rapid activation sequence creates the grouping")
    
    ser.close()
    print("\n[OK] Analysis complete")

if __name__ == '__main__':
    main()

