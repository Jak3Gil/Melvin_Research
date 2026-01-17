#!/usr/bin/env python3
"""
Automated Test - Cycle through all CAN IDs sequentially
This script will test each CAN ID in sequence with a clear pattern
so you can observe which physical motors respond to each ID.

Usage:
    python3 test_all_motors_sequence.py [PORT] [BAUD]
    python3 test_all_motors_sequence.py /dev/ttyUSB0 921600
"""

import serial
import sys
import time
import argparse

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
        time.sleep(0.15)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        
        return len(response) > 4  # Motor responded if response length > 4
    except:
        return False

def test_can_id(ser, can_id, movement_count):
    """Test a CAN ID with a unique movement pattern"""
    print(f"\n{'='*70}")
    print(f"Testing CAN ID {can_id} (0x{can_id:02X}) - Watch for {movement_count} movements!")
    print(f"{'='*70}")
    
    # Activate
    if not send_command(ser, build_activate_cmd(can_id)):
        print(f"  [NO RESPONSE] CAN ID {can_id} did not respond")
        return False
    
    time.sleep(0.3)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.3)
    
    # Create unique movement pattern (move forward/back movement_count times)
    for i in range(movement_count):
        print(f"  Movement {i+1}/{movement_count}...")
        
        # Forward
        send_command(ser, build_move_jog_cmd(can_id, 0.15, 1))
        time.sleep(0.6)
        
        # Stop
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.4)
        
        # Backward
        send_command(ser, build_move_jog_cmd(can_id, -0.15, 1))
        time.sleep(0.6)
        
        # Stop
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.4)
    
    # Deactivate
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.2)
    
    print(f"  [DONE] CAN ID {can_id} test complete")
    return True

def main():
    parser = argparse.ArgumentParser(description='Automated motor sequence test')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('baud', type=int, nargs='?', default=921600, help='Baud rate')
    parser.add_argument('--ids', type=str, help='Comma-separated CAN IDs (default: 8-15)')
    parser.add_argument('--delay', type=float, default=3.0, help='Delay between tests in seconds (default: 3.0)')
    
    args = parser.parse_args()
    
    if args.ids:
        try:
            can_ids = [int(x.strip()) for x in args.ids.split(',')]
        except ValueError:
            print("[ERROR] Invalid CAN IDs format")
            sys.exit(1)
    else:
        can_ids = list(range(8, 16))
    
    print("="*70)
    print("Automated Motor Sequence Test")
    print("="*70)
    print(f"\nPort: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print(f"Testing CAN IDs: {can_ids}")
    print(f"Delay between tests: {args.delay} seconds")
    print("\n" + "="*70)
    print("AUTOMATED TEST - Starting in 2 seconds...")
    print("="*70)
    print("Each CAN ID will have a unique movement pattern:")
    print("  CAN ID 8 = 1 movement, CAN ID 9 = 2 movements, etc.")
    print("="*70)
    
    time.sleep(2)  # Brief delay to allow observation
    
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
        
        # Test each CAN ID with unique movement count
        for idx, can_id in enumerate(can_ids, start=1):
            movement_count = idx  # CAN ID 8 = 1 movement, 9 = 2 movements, etc.
            test_can_id(ser, can_id, movement_count)
            
            if idx < len(can_ids):
                print(f"\nWaiting {args.delay} seconds before next test...")
                time.sleep(args.delay)
        
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)
        print("\nWhich physical motors did you observe moving?")
        print("\nBased on movement patterns:")
        for idx, can_id in enumerate(can_ids, start=1):
            print(f"  CAN ID {can_id} (0x{can_id:02X}) - {idx} movement(s)")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
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

