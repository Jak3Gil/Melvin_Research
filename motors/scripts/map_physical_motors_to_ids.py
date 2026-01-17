#!/usr/bin/env python3
"""
Map Physical Motor Positions to ID Ranges
Uses unique movement patterns to identify which physical motor responds to which ID range
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

def send_command(ser, cmd, timeout=0.3):
    try:
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
        return len(response) > 4
    except:
        return False

def rapid_activation_sequence(ser, max_id=100):
    """Run rapid activation sequence"""
    for can_id in range(1, max_id + 1):
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    for can_id in range(1, max_id + 1):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)

def test_id_range_movement(ser, can_id, pattern_name, speed=0.1, duration=2.0):
    """Test movement on a specific ID and return if motor moved"""
    print(f"\n  Testing ID {can_id:3d}: Pattern '{pattern_name}'", end='', flush=True)
    
    # Send move command
    send_command(ser, build_move_jog_cmd(can_id, speed, 1), timeout=0.1)
    time.sleep(duration)
    
    # Stop
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0), timeout=0.1)
    time.sleep(0.3)
    
    print(" [Sent]")

def map_physical_motors(ser):
    """Map physical motors to ID ranges using movement patterns"""
    print("="*70)
    print("Physical Motor to ID Range Mapping")
    print("="*70)
    print("\nThis will test different ID ranges with unique movement patterns.")
    print("Observe which PHYSICAL MOTOR moves for each ID range.")
    print("\n[IMPORTANT] Watch the motors carefully and note which physical")
    print("            motor moves for each ID range.\n")
    
    # Known ID ranges from previous tests
    id_ranges = [
        (1, 15, "Motor 1 range"),
        (16, 20, "Motor 2 range"),
        (21, 30, "Motor 3 range"),
        (31, 39, "Motor 4 range"),
        (64, 79, "Motor 8+ range"),
    ]
    
    # Deactivate all first
    print("Deactivating all motors...")
    for can_id in range(1, 100):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.005)
    time.sleep(0.5)
    
    # Run rapid activation
    print("Running rapid activation sequence...")
    rapid_activation_sequence(ser, 100)
    print("  [OK] Activation complete\n")
    
    # Test each range with unique patterns
    patterns = [
        ("Forward", 0.1),
        ("Backward", -0.1),
        ("Slow Forward", 0.05),
        ("Fast Forward", 0.2),
    ]
    
    mapping = {}
    
    for range_start, range_end, range_name in id_ranges:
        print(f"\n{'='*70}")
        print(f"Testing: {range_name} (IDs {range_start}-{range_end})")
        print(f"{'='*70}")
        
        # Use middle ID of range
        test_id = (range_start + range_end) // 2
        
        for pattern_name, speed in patterns:
            test_id_range_movement(ser, test_id, pattern_name, speed, 1.5)
            time.sleep(0.5)
            
            # Note: User must observe and record which physical motor moved
            print(f"    → Which physical motor moved? (Note it down)")
            time.sleep(2.0)  # Give time to observe
        
        mapping[range_name] = {
            'range': (range_start, range_end),
            'test_id': test_id,
        }
    
    return mapping

def test_specific_id_ranges(ser, test_ids):
    """Test specific IDs to see if they control different physical motors"""
    print("\n" + "="*70)
    print("Testing Specific IDs for Overlap")
    print("="*70)
    print("\nTesting IDs that might overlap to see if same motor moves...\n")
    
    rapid_activation_sequence(ser, 100)
    
    # Test IDs that might overlap
    test_cases = [
        (8, "Motor 1 typical ID"),
        (15, "Motor 1 end"),
        (16, "Motor 2 start"),
        (21, "Motor 3 start"),
        (31, "Motor 4 start (overlaps Motor 1 end?)"),
        (64, "Motor 8 start"),
        (73, "Motor 8/9 overlap"),
    ]
    
    for can_id, description in test_cases:
        print(f"\nTesting ID {can_id:3d} ({description}):")
        print(f"  Moving forward at 0.1 speed for 1 second...", end='', flush=True)
        
        send_command(ser, build_move_jog_cmd(can_id, 0.1, 1), timeout=0.1)
        time.sleep(1.0)
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0), timeout=0.1)
        time.sleep(0.5)
        
        print(" [Done]")
        print(f"  → Which physical motor moved? Note it down.")
        time.sleep(2.0)

def find_unique_motor_ids(ser):
    """Test individual IDs to find which ones trigger unique physical motors"""
    print("\n" + "="*70)
    print("Finding IDs That Trigger Unique Motors")
    print("="*70)
    print("\nTesting IDs one by one to find unique motor responses...\n")
    
    rapid_activation_sequence(ser, 100)
    
    # Test IDs in known ranges
    test_ids = list(range(1, 40)) + [64, 67, 73, 79]
    
    unique_motors = {}
    last_motor = None
    
    for can_id in test_ids:
        print(f"  Testing ID {can_id:3d}...", end='', flush=True)
        
        # Small movement
        send_command(ser, build_move_jog_cmd(can_id, 0.08, 1), timeout=0.1)
        time.sleep(0.8)
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0), timeout=0.1)
        time.sleep(0.3)
        
        print(" [Sent]")
        print(f"    → Same motor as ID {last_motor}? (y/n/new motor number)")
        
        # Note: Would need user input, but for now just log
        # In practice, user would observe and tell us
        
    return unique_motors

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("Physical Motor to ID Range Mapping Tool")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud Rate: {baud}")
    print("\n[NOTE] This script sends movement commands.")
    print("       Watch the motors carefully to identify which physical")
    print("       motor responds to which ID range.\n")
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("[OK] Serial port opened\n")
    
    # Run mapping tests
    mapping = map_physical_motors(ser)
    
    # Test for overlaps
    test_specific_id_ranges(ser, None)
    
    # Summary
    print("\n" + "="*70)
    print("MAPPING SUMMARY")
    print("="*70)
    print("\nBased on your observations, record which physical motor")
    print("corresponds to each ID range:\n")
    
    for range_name, info in mapping.items():
        start, end = info['range']
        print(f"{range_name:20} (IDs {start:3d}-{end:3d}): Physical Motor __?")
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    print("""
1. Record which physical motor moves for each ID range
2. Check if overlapping IDs (like 31) control same or different motors
3. Note if multiple IDs in a range control the SAME physical motor
4. Determine if you can use ID ranges to control individual motors

Since motors respond to ranges, you may be able to:
- Use ID 8-15 to control Motor 1
- Use ID 16-20 to control Motor 2
- Use ID 21-30 to control Motor 3
- etc.

Even though it's not individual IDs, range-based control might work for your needs.
    """)
    
    ser.close()
    print("\n[OK] Mapping complete")

if __name__ == '__main__':
    main()

