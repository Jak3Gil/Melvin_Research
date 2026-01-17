#!/usr/bin/env python3
"""
Test All CAN ID Ranges AUTOMATICALLY with Visual Identification
Tests one representative ID from each range with small movements
NO user input required - runs automatically
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
    
    # Short countdown
    print("Starting in 2 seconds...", flush=True)
    time.sleep(2)
    
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

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("  AUTOMATIC Motor Range Identification")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}")
    print("\n" + "="*70)
    print("WATCH YOUR MOTORS!")
    print("="*70)
    print("Each range will be tested automatically with unique pulse patterns:")
    print("  - Range 1 (ID 8):  1 pulse")
    print("  - Range 2 (ID 16): 2 pulses")
    print("  - Range 3 (ID 21): 3 pulses  [Motor 3]")
    print("  - Range 4 (ID 31): 4 pulses")
    print("  - Range 5 (ID 64): 5 pulses  [Motor 8]")
    print("  - Range 6 (ID 72): 6 pulses  [Motor 9]")
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
    
    print(f"\nStarting automatic test in 3 seconds...")
    time.sleep(3)
    
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
        
        # Test each range automatically
        for i, test in enumerate(test_ranges, 1):
            print(f"\n{'#'*70}")
            print(f"# TEST {i}/{len(test_ranges)}")
            print(f"{'#'*70}")
            
            test_motor_range(ser, test['id'], test['name'], test['pulses'])
            
            # Pause between tests
            if i < len(test_ranges):
                print(f"\n⏸️  Pausing 2 seconds before next test...\n")
                time.sleep(2)
        
        # Final summary
        print("\n" + "="*70)
        print("ALL TESTS COMPLETE")
        print("="*70)
        print("\nSummary of tests:")
        for i, test in enumerate(test_ranges, 1):
            print(f"  {i}. CAN ID {test['id']:2d} ({test['pulses']} pulses) - {test['name']}")
        
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        print("\nBased on the pulse patterns you saw, you should now know:")
        print("  - Which physical motor corresponds to each CAN ID range")
        print("  - How many unique physical motors are responding")
        print("\nIf you need to test specific IDs again:")
        print("  python3 quick_motor_test.py /dev/ttyUSB0 921600 <CAN_ID>")
        print("\nTo scan for more motors in higher ranges:")
        print("  python3 scan_all_motors_wide.py /dev/ttyUSB0 921600 --start 80 --end 127")
        
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

