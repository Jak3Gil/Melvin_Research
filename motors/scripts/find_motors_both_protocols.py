#!/usr/bin/env python3
"""
Find all 15 motors using BOTH protocols
Based on RobStride GitHub repositories analysis
"""

import serial
import time
import struct

def send_l91_at_protocol(ser, motor_id):
    """L91 AT Protocol - 0x41 0x54 format"""
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(0x00)  # Enable command
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(motor_id)
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.extend([0x0d, 0x0a])  # \r\n
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.05)
    return ser.read(200)

def send_l91_checksum_protocol(ser, motor_id):
    """L91 Checksum Protocol - 0xAA 0x55 format (from instant_test.py)"""
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.05)
    return ser.read(200)

def send_mit_protocol(ser, motor_id):
    """MIT Protocol - Standard CAN format (from ROS samples)"""
    # MIT mode enable command
    # CAN ID format: 0x000 + motor_id
    # Data: [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC]
    packet = bytearray([0x55, 0xAA])  # Header
    packet.extend(struct.pack('<H', motor_id))  # CAN ID
    packet.extend([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.05)
    return ser.read(200)

def send_broadcast_scan(ser):
    """Try broadcast commands that might trigger responses"""
    broadcasts = []
    
    # L91 AT broadcast
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00])
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    resp = ser.read(500)
    if resp:
        broadcasts.append(("L91 AT Broadcast 0x00", resp))
    
    # L91 Checksum broadcast
    packet = bytearray([0xAA, 0x55, 0x01, 0x00])
    packet.extend(struct.pack('<I', 0))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    resp = ser.read(500)
    if resp:
        broadcasts.append(("L91 Checksum Broadcast 0x00", resp))
    
    # MIT broadcast
    packet = bytearray([0x55, 0xAA])
    packet.extend(struct.pack('<H', 0x7FF))  # Broadcast ID
    packet.extend([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    resp = ser.read(500)
    if resp:
        broadcasts.append(("MIT Broadcast 0x7FF", resp))
    
    return broadcasts

print("="*70)
print("FIND ALL 15 MOTORS - MULTI-PROTOCOL SCAN")
print("="*70)
print("\nBased on RobStride GitHub repositories:")
print("  - CAN-USB-data-conversion")
print("  - robstride_ros_sample")
print("  - SampleProgram")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n[OK] Connected to {port} at {baud} baud\n")
    
    # TEST 1: Broadcast commands
    print("="*70)
    print("TEST 1: Broadcast Commands (All Protocols)")
    print("="*70)
    
    broadcasts = send_broadcast_scan(ser)
    
    if broadcasts:
        print(f"\n✅ Got {len(broadcasts)} broadcast response(s)!")
        for name, resp in broadcasts:
            print(f"\n{name}:")
            print(f"  {len(resp)} bytes: {resp.hex(' ')}")
    else:
        print("\n✗ No broadcast responses")
    
    # TEST 2: Scan with all 3 protocols
    print("\n" + "="*70)
    print("TEST 2: Full Scan with All 3 Protocols")
    print("="*70)
    
    results = {
        'L91 AT': {},
        'L91 Checksum': {},
        'MIT': {}
    }
    
    print("\nScanning IDs 0-127 with all protocols...")
    
    for test_id in range(0, 128):
        if test_id % 16 == 0:
            print(f"  Testing ID {test_id}-{min(test_id+15, 127)}...", end='', flush=True)
        
        # Try L91 AT
        resp = send_l91_at_protocol(ser, test_id)
        if resp and len(resp) > 4:
            results['L91 AT'][test_id] = resp
            if test_id % 16 != 0:
                print(f"\n    ✓ L91 AT: ID {test_id}", end='')
        
        # Try L91 Checksum
        resp = send_l91_checksum_protocol(ser, test_id)
        if resp and len(resp) > 4:
            results['L91 Checksum'][test_id] = resp
            if test_id % 16 != 0:
                print(f"\n    ✓ L91 Checksum: ID {test_id}", end='')
        
        # Try MIT
        resp = send_mit_protocol(ser, test_id)
        if resp and len(resp) > 4:
            results['MIT'][test_id] = resp
            if test_id % 16 != 0:
                print(f"\n    ✓ MIT: ID {test_id}", end='')
        
        if test_id % 16 == 15:
            found_in_range = any(
                test_id in results[proto] 
                for proto in results
            )
            if found_in_range:
                print(" ✓")
            else:
                print(" -")
    
    print("\n")
    
    # Analyze results
    print("="*70)
    print("RESULTS BY PROTOCOL")
    print("="*70)
    
    total_motors = 0
    all_found_ids = set()
    
    for protocol, ids in results.items():
        if ids:
            print(f"\n{protocol}:")
            print(f"  Found {len(ids)} responding IDs: {sorted(ids.keys())}")
            
            # Group consecutive IDs
            sorted_ids = sorted(ids.keys())
            groups = []
            if sorted_ids:
                current_group = [sorted_ids[0]]
                for i in range(1, len(sorted_ids)):
                    if sorted_ids[i] == sorted_ids[i-1] + 1:
                        current_group.append(sorted_ids[i])
                    else:
                        groups.append(current_group)
                        current_group = [sorted_ids[i]]
                groups.append(current_group)
            
            print(f"  Motor groups ({len(groups)} motors):")
            for i, group in enumerate(groups, 1):
                print(f"    Motor {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
                all_found_ids.update(group)
            
            total_motors += len(groups)
        else:
            print(f"\n{protocol}: No motors found")
    
    # TEST 3: Extended range scan for L91 Checksum (it supports 0-255)
    if results['L91 Checksum']:
        print("\n" + "="*70)
        print("TEST 3: Extended Range (128-255) - L91 Checksum Only")
        print("="*70)
        
        extended_found = []
        
        for test_id in range(128, 256):
            if test_id % 16 == 0:
                print(f"  Testing ID {test_id}-{min(test_id+15, 255)}...", end='', flush=True)
            
            resp = send_l91_checksum_protocol(ser, test_id)
            if resp and len(resp) > 4:
                extended_found.append(test_id)
                print(f"\n    ✓ ID {test_id}", end='')
            elif test_id % 16 == 15:
                print(" -")
        
        if extended_found:
            print(f"\n\n✅ Found motors in extended range!")
            print(f"   IDs: {extended_found}")
            all_found_ids.update(extended_found)
        else:
            print(f"\n\n✗ No motors in extended range (128-255)")
    
    ser.close()
    
    # FINAL SUMMARY
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    print(f"\n✅ Total unique IDs found: {len(all_found_ids)}")
    print(f"   IDs: {sorted(all_found_ids)}")
    
    # Estimate motor count
    sorted_all = sorted(all_found_ids)
    motor_groups = []
    if sorted_all:
        current_group = [sorted_all[0]]
        for i in range(1, len(sorted_all)):
            if sorted_all[i] == sorted_all[i-1] + 1:
                current_group.append(sorted_all[i])
            else:
                motor_groups.append(current_group)
                current_group = [sorted_all[i]]
        motor_groups.append(current_group)
    
    print(f"\n✅ Estimated motor count: {len(motor_groups)}")
    for i, group in enumerate(motor_groups, 1):
        print(f"   Motor {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
    
    if len(motor_groups) < 15:
        print(f"\n⚠️  STILL MISSING {15 - len(motor_groups)} MOTORS")
        print("\nPossible reasons:")
        print("  1. Motors are powered off")
        print("  2. Motors are on different baud rate")
        print("  3. Motors are on different CAN bus/port")
        print("  4. Motors need factory reset")
        print("  5. Different USB-to-CAN adapter for other motors")
        
        print("\nNext steps:")
        print("  1. Check if all 15 motors have power LEDs on")
        print("  2. Try different baud rates (115200, 230400, 460800)")
        print("  3. Check for additional /dev/ttyUSB* devices")
        print("  4. Power cycle motors one at a time to identify them")
    else:
        print(f"\n🎉 FOUND ALL 15 MOTORS!")
        print("\nNext step: Reconfigure them to unique IDs 1-15")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

