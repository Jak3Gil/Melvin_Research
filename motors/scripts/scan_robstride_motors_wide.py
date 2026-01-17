#!/usr/bin/env python3
"""
Wide search for Robstride Motors using different ID formats and addressing
"""

import serial
import sys
import time

# L91 Protocol - try different base addresses
BASE_ADDRESSES = [
    (0x07, 0xe8),  # Standard (2024 decimal)
    (0x07, 0xd0),  # Alternative 1
    (0x08, 0x00),  # Alternative 2
    (0x01, 0x00),  # Alternative 3
]

def build_activate_cmd(can_id, base_high=0x07, base_low=0xe8):
    return bytes([0x41, 0x54, 0x00, base_high, base_low, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id, base_high=0x07, base_low=0xe8):
    return bytes([0x41, 0x54, 0x20, base_high, base_low, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd):
    """Send command and read response"""
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.2)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.3:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        
        return response
    except Exception as e:
        return b""

def test_motor_id(ser, can_id, base_high=0x07, base_low=0xe8, verbose=False):
    """Test if a motor ID responds with given base address"""
    cmd = build_activate_cmd(can_id, base_high, base_low)
    response = send_command(ser, cmd)
    
    # Check if we got a meaningful response (longer than just echo)
    has_response = len(response) > 6
    
    if verbose and has_response:
        print(f"    Response: {response.hex(' ')}")
    
    if has_response:
        # Try load params to confirm
        cmd2 = build_load_params_cmd(can_id, base_high, base_low)
        response2 = send_command(ser, cmd2)
        time.sleep(0.1)
        
        # Deactivate
        deactivate_cmd = bytes([0x41, 0x54, 0x00, base_high, base_low, can_id, 0x00, 0x00, 0x0d, 0x0a])
        send_command(ser, deactivate_cmd)
        
        return len(response2) > 6
    
    return False

def wide_scan(ser):
    """Wide search for motors using different addressing schemes"""
    print("="*70)
    print("WIDE MOTOR SCAN - Testing Different ID Formats and Addresses")
    print("="*70)
    print()
    
    found_motors = []
    
    # Test 1: Standard addressing (0x07e8) with IDs 1-31
    print("Test 1: Standard base address (0x07e8) with IDs 1-31")
    print("-"*70)
    for can_id in range(1, 32):
        if test_motor_id(ser, can_id, 0x07, 0xe8):
            found_motors.append(("0x07e8", can_id))
            print(f"  [FOUND] Base 0x07e8, Motor ID {can_id} (0x{can_id:02X})")
    
    print()
    
    # Test 2: Try different base addresses for IDs 1-7
    print("Test 2: Different base addresses for IDs 1-7")
    print("-"*70)
    for base_high, base_low in BASE_ADDRESSES:
        base_val = (base_high << 8) | base_low
        if base_val == 0x07e8:
            continue  # Already tested
        
        print(f"  Testing base address 0x{base_high:02X}{base_low:02X} ({base_val})...")
        for can_id in range(1, 8):
            if test_motor_id(ser, can_id, base_high, base_low):
                found_motors.append((f"0x{base_high:02X}{base_low:02X}", can_id))
                print(f"    [FOUND] Base 0x{base_high:02X}{base_low:02X}, Motor ID {can_id} (0x{can_id:02X})")
    
    print()
    
    # Test 3: Maybe motors 1-7 are actually at IDs 16-22? (offset)
    print("Test 3: Checking if motors 1-7 are at IDs 16-22 (offset)")
    print("-"*70)
    for offset_id in range(16, 23):
        if test_motor_id(ser, offset_id, 0x07, 0xe8):
            found_motors.append(("0x07e8", offset_id))
            print(f"  [FOUND] Base 0x07e8, Motor ID {offset_id} (0x{offset_id:02X}) - might be physical motor {offset_id-15}")
    
    print()
    
    # Test 4: Extended addressing - try IDs with high bit set
    print("Test 4: Extended addressing (IDs 128-143)")
    print("-"*70)
    for ext_id in range(128, 144):
        if ext_id <= 255:  # Valid single byte
            if test_motor_id(ser, ext_id, 0x07, 0xe8):
                found_motors.append(("0x07e8", ext_id))
                print(f"  [FOUND] Base 0x07e8, Extended Motor ID {ext_id} (0x{ext_id:02X})")
    
    print()
    
    return found_motors

def main():
    port = "COM3"
    baud = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baud = int(sys.argv[2])
    
    print("="*70)
    print("Robstride Motor Wide Scanner")
    print("="*70)
    print(f"Port: {port}")
    print(f"Baud Rate: {baud}")
    print()
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            write_timeout=1.0
        )
        time.sleep(0.5)
        print("[OK] Serial port opened\n")
        
        found_motors = wide_scan(ser)
        
        print("="*70)
        print("SCAN RESULTS")
        print("="*70)
        
        if found_motors:
            # Group by base address, remove duplicates
            by_base = {}
            seen = set()
            for base, motor_id in found_motors:
                key = (base, motor_id)
                if key not in seen:
                    seen.add(key)
                    if base not in by_base:
                        by_base[base] = []
                    by_base[base].append(motor_id)
            
            for base in sorted(by_base.keys()):
                motor_ids = sorted(set(by_base[base]))  # Remove duplicates
                print(f"\nBase Address {base}: {len(motor_ids)} motor(s)")
                for mid in motor_ids:
                    print(f"  - Motor ID {mid} (0x{mid:02X})")
                
                # If we found IDs 16-22, suggest they might be physical motors 1-7
                if base == "0x07e8" and 16 in motor_ids and 22 in motor_ids:
                    print(f"\n  NOTE: IDs 16-22 might be physical motors 1-7")
                    print(f"        IDs 8-15 might be physical motors 8-15")
        else:
            print("\n[NO MOTORS FOUND]")
        
        print()
        ser.close()
        print("[OK] Scan complete")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

