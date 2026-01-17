#!/usr/bin/env python3
"""
Find Motors Starting from CAN ID 31+
Uses the same activation sequence that worked for Motors 1-3
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

def send_command(ser, cmd, show_response=False):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.05)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.3:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        
        if show_response and response:
            return response.hex(' ')
        return len(response) > 4
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description='Find Motors Starting from ID 31')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('baud', type=int, nargs='?', default=921600, help='Baud rate')
    parser.add_argument('--start', type=int, default=31, help='Start CAN ID (default: 31)')
    parser.add_argument('--end', type=int, default=200, help='End CAN ID (default: 200)')
    
    args = parser.parse_args()
    
    port = args.port
    baud = args.baud
    start_id = args.start
    end_id = args.end
    
    print("="*70)
    print("Find Motors Starting from CAN ID 31+")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud Rate: {baud}")
    print(f"Testing CAN IDs: {start_id} to {end_id}")
    print(f"\nUsing the same activation sequence that worked for Motors 1-3")
    print("="*70)
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("\n[OK] Serial port opened\n")
    
    # STEP 1: Rapidly activate ALL IDs in the range
    print("="*70)
    print(f"STEP 1: Rapidly Activating ALL CAN IDs ({start_id} to {end_id})")
    print("="*70)
    print(f"Activating IDs {start_id}-{end_id} rapidly (0.05s delays)...\n")
    
    for can_id in range(start_id, end_id + 1):
        send_command(ser, build_activate_cmd(can_id))
        time.sleep(0.05)
        if (can_id - start_id + 1) % 20 == 0:
            print(f"  Activated IDs {start_id}-{can_id}...")
    
    print(f"\n[STEP 1 COMPLETE] Activated {end_id - start_id + 1} IDs")
    time.sleep(1.0)
    
    # STEP 2: Load params on ALL IDs
    print("\n" + "="*70)
    print(f"STEP 2: Loading Parameters on ALL CAN IDs ({start_id} to {end_id})")
    print("="*70)
    print(f"Loading params on IDs {start_id}-{end_id}...\n")
    
    for can_id in range(start_id, end_id + 1):
        send_command(ser, build_load_params_cmd(can_id))
        time.sleep(0.05)
        if (can_id - start_id + 1) % 20 == 0:
            print(f"  Loaded params on IDs {start_id}-{can_id}...")
    
    print(f"\n[STEP 2 COMPLETE]")
    time.sleep(1.0)
    
    # STEP 3: Test each ID individually
    print("\n" + "="*70)
    print(f"STEP 3: Testing Each CAN ID Individually ({start_id} to {end_id})")
    print("="*70)
    print("Testing each ID with movement...\n")
    
    responding_ids = []
    print(f"Starting tests in 2 seconds...\n")
    time.sleep(2.0)
    
    for can_id in range(start_id, end_id + 1):
        print(f"Testing CAN ID {can_id:3d} (0x{can_id:03X})...", end='', flush=True)
        
        # Send activate
        has_response = send_command(ser, build_activate_cmd(can_id))
        time.sleep(0.2)
        
        if has_response:
            # Load params
            send_command(ser, build_load_params_cmd(can_id))
            time.sleep(0.2)
            
            # Small forward movement
            send_command(ser, build_move_jog_cmd(can_id, 0.08))
            time.sleep(0.6)
            
            # Stop
            send_command(ser, build_move_jog_cmd(can_id, 0.0))
            time.sleep(0.3)
            
            # Small backward movement
            send_command(ser, build_move_jog_cmd(can_id, -0.08))
            time.sleep(0.6)
            
            # Stop
            send_command(ser, build_move_jog_cmd(can_id, 0.0))
            time.sleep(0.3)
            
            responding_ids.append(can_id)
            print(" ✓ Motor responded")
        else:
            print(" -")
        
        time.sleep(0.1)
    
    # Cleanup
    print("\n" + "="*70)
    print("CLEANUP: Deactivating All Motors")
    print("="*70)
    for can_id in range(start_id, end_id + 1):
        send_command(ser, build_deactivate_cmd(can_id))
        time.sleep(0.01)
    
    # Results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\nCAN IDs that responded: {len(responding_ids)}")
    if responding_ids:
        print(f"Responding IDs: {responding_ids}")
        
        # Group by ranges
        print("\nGrouped by ranges:")
        if responding_ids:
            ranges = []
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
            
            for start, end in ranges:
                if start == end:
                    print(f"  ID {start} (0x{start:03X})")
                else:
                    print(f"  IDs {start}-{end} (0x{start:03X}-0x{end:03X}) - {end-start+1} IDs")
    else:
        print("No motors responded in this range")
    
    ser.close()
    print("\n[OK] Test complete")
    print("\nWatch which physical motors moved and note which ID ranges they respond to!")

if __name__ == '__main__':
    main()

