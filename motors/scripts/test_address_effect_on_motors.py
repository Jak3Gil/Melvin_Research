#!/usr/bin/env python3
"""
Test if Different Addresses Affect Motor Response
See if using different addresses changes which motors respond or their behavior
"""

import serial
import sys
import time

def build_activate_cmd_with_address(can_id, addr_high, addr_low):
    return bytes([0x41, 0x54, 0x00, addr_high, addr_low, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_load_params_cmd_with_address(can_id, addr_high, addr_low):
    return bytes([0x41, 0x54, 0x20, addr_high, addr_low, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd, timeout=0.3):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.1)
        response = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        return len(response) > 4
    except:
        return False

def test_can_id_with_address(ser, can_id, addr_high, addr_low):
    """Test if a CAN ID responds with a specific address"""
    # Activate
    response1 = send_command(ser, build_activate_cmd_with_address(can_id, addr_high, addr_low))
    time.sleep(0.2)
    # Load params
    response2 = send_command(ser, build_load_params_cmd_with_address(can_id, addr_high, addr_low))
    return response1 or response2

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    # Test addresses that worked
    test_addresses = [
        (0x07, 0xE8, "Original 0x07 0xE8"),
        (0x00, 0x00, "0x00 0x00"),
        (0x01, 0x00, "0x01 0x00"),
        (0x7E, 0x08, "0x7E 0x08"),
    ]
    
    # Test CAN IDs we know work
    test_can_ids = [8, 16, 21, 64]  # Known to control different motors
    
    print("="*70)
    print("Test Address Effect on Motor Response")
    print("="*70)
    print(f"\nTesting if different addresses change which motors respond")
    print(f"Testing CAN IDs: {test_can_ids}")
    print(f"Testing {len(test_addresses)} address combinations\n")
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("[OK] Serial port opened\n")
    
    results = {}
    
    for addr_high, addr_low, addr_name in test_addresses:
        print(f"\n{'='*70}")
        print(f"Testing Address: {addr_name} (0x{addr_high:02X} 0x{addr_low:02X})")
        print(f"{'='*70}")
        
        responding_ids = []
        
        for can_id in test_can_ids:
            print(f"  Testing CAN ID {can_id:3d} (0x{can_id:02X})...", end='', flush=True)
            
            if test_can_id_with_address(ser, can_id, addr_high, addr_low):
                responding_ids.append(can_id)
                print(" ✓")
            else:
                print(" -")
            
            time.sleep(0.2)
        
        results[addr_name] = responding_ids
        print(f"\n  Address {addr_name}: IDs {responding_ids} respond")
    
    # Compare results
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    
    baseline = results.get("Original 0x07 0xE8", [])
    print(f"\nBaseline (0x07 0xE8): IDs {baseline} respond")
    
    for addr_name, ids in results.items():
        if addr_name != "Original 0x07 0xE8":
            ids_str = str(ids)
            if ids == baseline:
                print(f"{addr_name:20}: IDs {ids_str:20} - SAME as baseline")
            else:
                print(f"{addr_name:20}: IDs {ids_str:20} - DIFFERENT!")
                if set(ids) != set(baseline):
                    print(f"                         Difference: {set(baseline) ^ set(ids)}")
    
    # Check if address matters
    all_same = all(ids == baseline for ids in results.values())
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    
    if all_same:
        print("\n[RESULT] All addresses produce the same motor responses")
        print("  - Address bytes don't affect which motors respond")
        print("  - Address is likely for the USB-to-CAN adapter")
        print("  - Motors respond based on CAN ID only, not address")
    else:
        print("\n[RESULT] Different addresses produce different responses!")
        print("  - Address bytes DO affect motor responses")
        print("  - Different addresses might target different motor groups")
        print("  - Need to find the correct address for individual motor control")
    
    ser.close()
    print("\n[OK] Test complete")

if __name__ == '__main__':
    main()

