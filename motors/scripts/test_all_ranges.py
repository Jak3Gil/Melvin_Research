#!/usr/bin/env python3
"""
Test All CAN ID Ranges with Visual Identification
Tests one representative ID from each range with small movements
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
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.05)

def test_motor_range(ser, can_id, range_name, num_pulses=3, speed=0.08):
    """Test a motor with visible pulses"""
    print(f"\n{'='*70}")
    print(f"Testing: {range_name}")
    print(f"CAN ID: {can_id} (0x{can_id:02X})")
    print(f"Pattern: {num_pulses} pulse(s)")
    print(f"{'='*70}")
    print("\n👀 WATCH YOUR MOTORS! Which one moves?\n")
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"Starting in {i}...", flush=True)
        time.sleep(1)
    
    print("\n🔄 MOVING NOW!\n")
    
    # Activate
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    # Execute pattern with visible pulses
    for i in range(num_pulses):
        print(f"  💫 Pulse {i+1}/{num_pulses}...", flush=True)
        send_command(ser, build_move_jog_cmd(can_id, speed, 1))
        time.sleep(0.5)
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.4)
    
    # Deactivate
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.2)
    
    print("\n✅ Test complete.")
    print(f"Did you see a motor move {num_pulses} times?")
    
    # Wait for user to note which motor moved
    time.sleep(2)

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("  Visual Motor Range Identification")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}")
    print("\n" + "="*70)
    print("INSTRUCTIONS")
    print("="*70)
    print("This script will test each CAN ID range one at a time.")
    print("Each test will:")
    print("  1. Show which CAN ID is being tested")
    print("  2. Count down 3 seconds")
    print("  3. Make the motor pulse multiple times")
    print("  4. Wait for you to note which motor moved")
    print("\nWatch carefully and write down which physical motor moves!")
    print("The number of pulses helps identify which test is running.")
    print("="*70)
    
    # Define test ranges based on scan results
    test_ranges = [
        {'id': 8,  'name': 'Range 1: IDs 8-15 (Motor 1?)', 'pulses': 1},
        {'id': 16, 'name': 'Range 2: IDs 16-20 (Motor 2?)', 'pulses': 2},
        {'id': 21, 'name': 'Range 3: IDs 21-30 (Motor 3 - known)', 'pulses': 3},
        {'id': 31, 'name': 'Range 4: IDs 31-39 (Motor 4?)', 'pulses': 4},
        {'id': 64, 'name': 'Range 5: IDs 64-71 (Motor 8 - known)', 'pulses': 5},
        {'id': 72, 'name': 'Range 6: IDs 72-79 (Motor 9 - known)', 'pulses': 6},
    ]
    
    print(f"\nWill test {len(test_ranges)} ranges:")
    for i, test in enumerate(test_ranges, 1):
        print(f"  {i}. {test['name']} - ID {test['id']} ({test['pulses']} pulses)")
    
    print("\n" + "="*70)
    input("\nPress Enter to start testing...")
    
    try:
        # Open serial port
        print(f"\nOpening serial port {port}...")
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("[OK] Serial port opened\n")
        
        # Send detection command
        print("Sending detection command...")
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        ser.flush()
        time.sleep(0.5)
        print("[OK] Ready to test\n")
        
        # Test each range
        for i, test in enumerate(test_ranges, 1):
            print(f"\n{'#'*70}")
            print(f"# TEST {i}/{len(test_ranges)}")
            print(f"{'#'*70}")
            
            test_motor_range(ser, test['id'], test['name'], test['pulses'])
            
            # Pause between tests
            if i < len(test_ranges):
                print(f"\n⏸️  Pausing 3 seconds before next test...")
                time.sleep(3)
        
        # Final summary
        print("\n" + "="*70)
        print("ALL TESTS COMPLETE")
        print("="*70)
        print("\nSummary of tests:")
        for i, test in enumerate(test_ranges, 1):
            print(f"  {i}. CAN ID {test['id']:2d} ({test['pulses']} pulses) - {test['name']}")
        
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. Review your notes on which motors moved")
        print("2. Create a mapping of CAN ID → Physical Motor")
        print("3. If motors are missing, scan higher ranges:")
        print("   python3 scan_all_motors_wide.py /dev/ttyUSB0 921600 --start 80 --end 127")
        print("\n4. To test individual IDs:")
        print("   python3 quick_motor_test.py /dev/ttyUSB0 921600 <CAN_ID>")
        
        ser.close()
        print("\n[OK] Testing complete")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        if 'ser' in locals():
            # Emergency stop - deactivate all tested IDs
            print("Sending deactivate commands...")
            for test in test_ranges:
                try:
                    ser.write(build_deactivate_cmd(test['id']))
                    ser.flush()
                    time.sleep(0.05)
                except:
                    pass
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

