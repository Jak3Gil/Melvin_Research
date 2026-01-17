#!/usr/bin/env python3
"""
Analyze motor behavior - run multiple scans to see if IDs change
"""

import serial
import time

def scan_all_ids(ser, id_range):
    """Scan a range of IDs"""
    found = []
    for can_id in id_range:
        try:
            cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
            ser.reset_input_buffer()
            ser.write(cmd)
            ser.flush()
            time.sleep(0.12)
            resp = ser.read(100)
            
            if len(resp) > 4:
                found.append(can_id)
        except:
            pass
        time.sleep(0.05)
    
    return found

port = '/dev/ttyUSB0'
baud = 921600

print("="*70)
print("MOTOR BEHAVIOR ANALYSIS - Multiple Scans")
print("="*70)
print()

try:
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    
    # Run 5 scans
    all_scans = []
    
    for scan_num in range(1, 6):
        print(f"Scan {scan_num}/5...", end=" ")
        
        # Scan IDs 1-127
        found = scan_all_ids(ser, range(1, 128))
        all_scans.append(found)
        
        print(f"Found {len(found)} motors: {sorted(found)}")
        time.sleep(1.0)  # Wait between scans
    
    ser.close()
    
    # Analysis
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print(f"{'='*70}\n")
    
    # Find IDs that appeared in ALL scans
    always_responding = set(all_scans[0])
    for scan in all_scans[1:]:
        always_responding &= set(scan)
    
    # Find IDs that appeared in ANY scan
    sometimes_responding = set()
    for scan in all_scans:
        sometimes_responding |= set(scan)
    
    # Find IDs that appeared sometimes but not always
    intermittent = sometimes_responding - always_responding
    
    print(f"Always responding ({len(always_responding)} motors):")
    if always_responding:
        print(f"  IDs: {sorted(always_responding)}")
    else:
        print(f"  None")
    
    print(f"\nIntermittent ({len(intermittent)} IDs):")
    if intermittent:
        print(f"  IDs: {sorted(intermittent)}")
        print(f"  These IDs respond inconsistently - may indicate:")
        print(f"    - Multiple motors sharing same ID range")
        print(f"    - Motors in unstable state")
        print(f"    - CAN bus interference")
    else:
        print(f"  None - all motors respond consistently")
    
    print(f"\nTotal unique IDs seen: {len(sometimes_responding)}")
    
    # Show which IDs appeared in which scans
    print(f"\n{'='*70}")
    print("DETAILED SCAN RESULTS")
    print(f"{'='*70}\n")
    
    all_ids = sorted(sometimes_responding)
    print(f"{'ID':<5} {'Scan 1':<8} {'Scan 2':<8} {'Scan 3':<8} {'Scan 4':<8} {'Scan 5':<8}")
    print("-" * 70)
    
    for can_id in all_ids:
        row = f"{can_id:<5}"
        for scan in all_scans:
            if can_id in scan:
                row += f"{'✓':<8}"
            else:
                row += f"{'✗':<8}"
        print(row)
    
    print(f"\n{'='*70}")
    print("CONCLUSION")
    print(f"{'='*70}\n")
    
    if len(always_responding) >= 6:
        print(f"✓ Found {len(always_responding)} consistently responding motors")
        print(f"  Use these IDs for reliable control: {sorted(always_responding)}")
    else:
        print(f"⚠️  Only {len(always_responding)} motors respond consistently")
        print(f"  Motor behavior is unstable - check:")
        print(f"    1. Power supply stability")
        print(f"    2. CAN bus termination")
        print(f"    3. Wiring connections")
        print(f"    4. Motor controller status")
    
    if len(intermittent) > 0:
        print(f"\n⚠️  {len(intermittent)} IDs respond intermittently")
        print(f"  This suggests configuration issues or multiple motors")
        print(f"  sharing ID ranges")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}\n")

