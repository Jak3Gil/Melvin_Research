#!/usr/bin/env python3
"""
Verify all 15 motors found
Tests each motor individually
"""

import serial
import time

def test_motor(ser, can_id):
    """Test a specific motor"""
    try:
        # Activate
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.15)
        resp1 = ser.read(100)
        
        # Load params
        cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.15)
        resp2 = ser.read(100)
        
        has_response = (len(resp1) > 4) or (len(resp2) > 4)
        
        return has_response, resp1, resp2
    except Exception as e:
        return False, b"", b""

# All motor IDs found
all_motor_ids = [
    # Original 6 motors
    8, 20, 31, 32, 64, 72,
    # Newly found 9 motors
    13, 29, 41, 53, 69, 81, 97, 109, 121
]

print("="*70)
print("VERIFYING ALL 15 MOTORS")
print("="*70)
print()

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print(f"✓ Connected to {port} at {baud} baud\n")
    
    results = []
    
    for i, can_id in enumerate(sorted(all_motor_ids), 1):
        print(f"Motor {i:2d} (CAN ID {can_id:3d})...", end=" ")
        
        has_response, resp1, resp2 = test_motor(ser, can_id)
        
        if has_response:
            print("✓ RESPONDS")
            if resp1 and len(resp1) > 10:
                sig = resp1[4:14].hex(' ')
                print(f"           Signature: {sig}")
            results.append({'num': i, 'id': can_id, 'status': 'OK'})
        else:
            print("✗ NO RESPONSE")
            results.append({'num': i, 'id': can_id, 'status': 'FAIL'})
        
        time.sleep(0.2)
    
    ser.close()
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    working = [r for r in results if r['status'] == 'OK']
    failed = [r for r in results if r['status'] == 'FAIL']
    
    print(f"✓ Working motors: {len(working)}/15")
    if working:
        print(f"  IDs: {[r['id'] for r in working]}")
    
    if failed:
        print(f"\n✗ Failed motors: {len(failed)}/15")
        print(f"  IDs: {[r['id'] for r in failed]}")
    
    print(f"\n{'='*70}")
    if len(working) == 15:
        print("🎉 SUCCESS! All 15 motors found and responding!")
    elif len(working) >= 10:
        print(f"✓ Good! Found {len(working)} motors")
    else:
        print(f"⚠️  Only {len(working)} motors responding")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n✗ Error: {e}\n")

