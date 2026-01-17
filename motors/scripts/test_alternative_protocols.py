#!/usr/bin/env python3
"""
Test Alternative Protocols and Command Formats
Tests if missing motors respond to different command formats
"""

import serial
import sys
import time

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
        return len(response) > 4, response
    except:
        return False, b""

def test_various_command_formats(ser, can_id):
    """Test different command formats for a single ID"""
    results = {}
    
    # Standard format
    standard = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    has_resp, resp = send_command(ser, standard, timeout=0.2)
    results['standard'] = has_resp
    
    # Try different address bytes
    for addr_high, addr_low in [(0x00, 0x00), (0x01, 0x01), (0xFF, 0xFF)]:
        cmd = bytes([0x41, 0x54, 0x00, addr_high, addr_low, can_id, 0x01, 0x00, 0x0d, 0x0a])
        has_resp, _ = send_command(ser, cmd, timeout=0.2)
        results[f'addr_{addr_high:02x}_{addr_low:02x}'] = has_resp
        time.sleep(0.05)
    
    # Try different command bytes
    for cmd_byte in [0x01, 0x02, 0x10, 0x11, 0x20, 0x21]:
        cmd = bytes([0x41, 0x54, cmd_byte, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
        has_resp, _ = send_command(ser, cmd, timeout=0.2)
        results[f'cmd_{cmd_byte:02x}'] = has_resp
        time.sleep(0.05)
    
    return results

def test_missing_id_ranges(ser):
    """Test missing ID ranges with various formats"""
    print("="*70)
    print("Testing Missing ID Ranges with Alternative Formats")
    print("="*70)
    
    missing_ranges = [
        (0, 7, "IDs 0-7"),
        (40, 63, "IDs 40-63"),
        (80, 99, "IDs 80-99"),
        (100, 127, "IDs 100-127"),
        (128, 255, "IDs 128-255"),
    ]
    
    found_any = False
    
    for start, end, desc in missing_ranges:
        print(f"\n{desc}...")
        found_in_range = []
        
        for can_id in range(start, end + 1):
            results = test_various_command_formats(ser, can_id)
            
            # Check if any format worked
            if any(results.values()):
                found_in_range.append(can_id)
                print(f"  ID {can_id:3d}: ✓ (working format: {[k for k,v in results.items() if v]})")
                found_any = True
            
            time.sleep(0.05)
            
            if can_id % 20 == 0:
                print(f"    Progress: {can_id}/{end}")
        
        if found_in_range:
            print(f"  Found {len(found_in_range)} IDs in this range: {found_in_range}")
        else:
            print(f"  No IDs found in this range")
    
    return found_any

def test_extended_can_ids(ser):
    """Test if motors might use extended CAN IDs (beyond 8-bit)"""
    print("\n" + "="*70)
    print("Testing Extended CAN ID Hypothesis")
    print("="*70)
    print("\nNOTE: L91 protocol uses 8-bit IDs, but motors might expect extended IDs")
    print("Testing if different ID encoding reveals motors...\n")
    
    # Try treating ID as high byte + low byte
    found = []
    
    for motor_num in range(1, 16):
        # Try different ID encodings
        encodings = [
            motor_num,                    # Direct
            motor_num << 1,               # Shifted
            motor_num << 4,               # Shifted more
            0x100 + motor_num,            # Extended format
            0x200 + motor_num,            # Control frame format
        ]
        
        for can_id in encodings:
            if can_id > 255:
                continue  # Skip if beyond 8-bit
            
            cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
            has_resp, _ = send_command(ser, cmd, timeout=0.15)
            
            if has_resp:
                found.append((motor_num, can_id))
                print(f"  Motor {motor_num} responds to ID {can_id}")
                break
        
        time.sleep(0.05)
    
    return found

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("Alternative Protocol Testing")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}\n")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("[OK] Serial port opened\n")
    except Exception as e:
        print(f"[ERROR] Failed to open port: {e}")
        return
    
    # Test missing ranges
    found_ranges = test_missing_id_ranges(ser)
    
    # Test extended IDs
    found_extended = test_extended_can_ids(ser)
    
    ser.close()
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\nFound in missing ranges: {'Yes' if found_ranges else 'No'}")
    print(f"Found with extended IDs: {len(found_extended)}")
    if found_extended:
        print(f"  {found_extended}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()

