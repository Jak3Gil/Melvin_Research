#!/usr/bin/env python3
"""
Quick deep scan - test multiple baud rates quickly
"""

import serial
import time

def test_id(ser, can_id):
    """Quick test of a CAN ID"""
    try:
        # Activate
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.15)
        resp = ser.read(100)
        return len(resp) > 4
    except:
        return False

def scan_at_baud(port, baud):
    """Scan at specific baud rate"""
    print(f"\nTesting {baud} baud...")
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.3)
        
        found = []
        # Test key IDs
        test_ids = list(range(1, 128, 4))  # Test every 4th ID for speed
        
        for can_id in test_ids:
            if test_id(ser, can_id):
                found.append(can_id)
                print(f"  ✓ ID {can_id}")
        
        ser.close()
        return found
    except Exception as e:
        print(f"  Error: {e}")
        return []

# Test common baud rates
port = '/dev/ttyUSB0'
baud_rates = [115200, 250000, 500000, 921600, 1000000]

print("="*60)
print("Quick Multi-Baud Scan")
print("="*60)

results = {}
for baud in baud_rates:
    found = scan_at_baud(port, baud)
    if found:
        results[baud] = found
        print(f"  Found {len(found)} at {baud}: {found}")

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
for baud, motors in results.items():
    print(f"{baud} baud: {len(motors)} motors - {motors}")

if not results:
    print("No motors found at any baud rate!")
    print("\nCheck:")
    print("1. Motors powered on?")
    print("2. CAN bus connected?")
    print("3. USB adapter working?")

