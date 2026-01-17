#!/usr/bin/env python3
"""
Quick scan for missing motors - tests every Nth ID to find ranges faster
"""

import serial
import sys
import time

def build_activate_cmd(can_id):
    # CAN ID must be 0-255 (single byte)
    if can_id > 255:
        can_id = can_id % 256
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd, timeout=0.2):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.03)
        response = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.01)
        return len(response) > 4
    except:
        return False

def quick_scan(ser, start, end, step=5):
    """Quick scan testing every Nth ID"""
    print(f"Quick scanning IDs {start}-{end} (step={step})...")
    
    # Rapid activation of all IDs first
    print("Activating all IDs...")
    for can_id in range(start, end + 1):
        send_command(ser, build_activate_cmd(can_id), timeout=0.05)
        if can_id % 50 == 0:
            print(f"  Progress: {can_id}/{end}")
        time.sleep(0.005)
    time.sleep(0.2)
    
    for can_id in range(start, end + 1):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.05)
        time.sleep(0.005)
    time.sleep(0.2)
    
    # Test every Nth ID
    print(f"\nTesting every {step}th ID...")
    responding = []
    
    for can_id in range(start, end + 1, step):
        if send_command(ser, build_activate_cmd(can_id), timeout=0.15):
            responding.append(can_id)
        time.sleep(0.05)
        
        if can_id % 100 == 0:
            print(f"  Progress: {can_id}/{end} ({len(responding)} found)")
    
    return responding

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("Quick Missing Motors Scan")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}")
    print("\nScanning higher ID ranges to find missing 10 motors...\n")
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("[OK] Serial port opened\n")
    
    # Test different ranges (CAN IDs limited to 0-255)
    ranges_to_test = [
        (40, 63, "Range 40-63 (gap between Motor 4 and Motor 8)"),
        (80, 100, "Range 80-100 (after Motor 8 range)"),
        (100, 150, "Range 100-150"),
        (150, 200, "Range 150-200"),
        (200, 255, "Range 200-255"),
        (0, 7, "Range 0-7 (before Motor 1)"),
    ]
    
    all_responding = []
    
    for start, end, name in ranges_to_test:
        print(f"\n{'='*70}")
        print(f"{name}")
        print(f"{'='*70}")
        
        responding = quick_scan(ser, start, end, step=3)
        all_responding.extend(responding)
        
        if responding:
            print(f"\n[FOUND] {len(responding)} responding IDs: {responding}")
        else:
            print(f"\n[NOT FOUND] No responding IDs in this range")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal responding IDs found: {len(all_responding)}")
    
    if all_responding:
        unique_ids = sorted(set(all_responding))
        print(f"Unique responding IDs: {unique_ids}")
        
        # Find ranges
        ranges = []
        if unique_ids:
            range_start = unique_ids[0]
            range_end = unique_ids[0]
            
            for can_id in unique_ids[1:]:
                if can_id <= range_end + 5:  # Allow gaps up to 5
                    range_end = can_id
                else:
                    ranges.append((range_start, range_end))
                    range_start = can_id
                    range_end = can_id
            ranges.append((range_start, range_end))
        
        print(f"\nPotential ID ranges: {len(ranges)}")
        for start, end in ranges:
            print(f"  IDs {start}-{end}")
    
    ser.close()
    print("\n[OK] Quick scan complete")

if __name__ == '__main__':
    main()

