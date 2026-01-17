#!/usr/bin/env python3
"""
Configure the remaining 7 motors (IDs 1-7)
After power cycle, use different source IDs
"""

import serial
import time
import struct

def send_command(ser, can_id, command_type, data):
    """Send command via RobStride adapter"""
    packet = bytearray([0x41, 0x54])
    packet.append(command_type)
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(can_id)
    packet.extend(data)
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.15)
    
    return ser.read(200)

def activate_motor(ser, can_id):
    return send_command(ser, can_id, 0x00, [0x01, 0x00])

def deactivate_motor(ser, can_id):
    return send_command(ser, can_id, 0x00, [0x00, 0x00])

def set_can_id(ser, old_id, new_id):
    print(f"  Configuring ID {old_id} → {new_id}...", end='', flush=True)
    
    deactivate_motor(ser, old_id)
    time.sleep(0.2)
    
    old_id_bytes = struct.pack('<I', old_id)
    packet = bytearray([0x41, 0x54, 0x07, 0x07, 0xe8, new_id])
    packet.extend(old_id_bytes[:2])
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    ser.read(200)
    
    packet = bytearray([0x41, 0x54, 0x08, 0x07, 0xe8, new_id, 0x00, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    ser.read(200)
    
    time.sleep(0.3)
    resp = activate_motor(ser, new_id)
    
    if resp and len(resp) > 0:
        print(f" ✅")
        return True
    else:
        print(f" ⚠️")
        return False

def scan_range(ser, start, end):
    responding = []
    for motor_id in range(start, end + 1):
        resp = activate_motor(ser, motor_id)
        if resp and len(resp) > 0:
            responding.append(motor_id)
    return responding

print("="*70)
print("CONFIGURE REMAINING 7 MOTORS (IDs 1-7)")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected\n")
    
    # Check current status
    print("Checking current configuration...")
    configured = scan_range(ser, 1, 15)
    print(f"Already configured: {configured}")
    
    missing = sorted(set(range(1, 16)) - set(configured))
    print(f"Missing: {missing}\n")
    
    if len(missing) == 0:
        print("🎉 All 15 motors already configured!")
        ser.close()
        exit(0)
    
    # Check what's in the old ranges
    print("Scanning old ID ranges...")
    old_8_39 = scan_range(ser, 8, 39)
    old_64_79 = scan_range(ser, 64, 79)
    
    print(f"  IDs 8-39: {len(old_8_39)} responding")
    print(f"  IDs 64-79: {len(old_64_79)} responding")
    
    # Find available source IDs (not overlapping with configured motors)
    available_sources = []
    
    # Try IDs from range 8-39 that aren't 8-15 (already used)
    for sid in [16, 17, 19, 21, 22, 23, 24, 25, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]:
        if sid in old_8_39:
            available_sources.append(sid)
    
    # Try IDs from range 64-79 that aren't already used
    for sid in [64, 65, 66, 67, 69, 70, 71, 72, 73, 74, 75, 77, 78, 79]:
        if sid in old_64_79 and sid not in [64, 68, 72, 76]:  # Skip already configured
            available_sources.append(sid)
    
    print(f"\nAvailable source IDs: {available_sources[:15]}\n")
    
    if len(available_sources) < len(missing):
        print(f"⚠️  Only {len(available_sources)} source IDs available for {len(missing)} motors")
        print(f"   Power cycle recommended to clear old IDs")
    
    # Configure remaining motors
    print("="*70)
    print("CONFIGURING REMAINING MOTORS")
    print("="*70 + "\n")
    
    configured_now = []
    
    for i, target_id in enumerate(missing):
        if i >= len(available_sources):
            print(f"Motor {target_id}: No source ID available ⚠️")
            continue
        
        source_id = available_sources[i]
        print(f"Motor {target_id}: ", end='', flush=True)
        
        # Verify source exists
        resp = activate_motor(ser, source_id)
        if not resp or len(resp) == 0:
            print(f"Source ID {source_id} not found ⚠️")
            continue
        
        # Configure
        success = set_can_id(ser, source_id, target_id)
        if success:
            configured_now.append(target_id)
        
        time.sleep(0.3)
    
    # Final check
    print(f"\n{'='*70}")
    print("FINAL STATUS")
    print(f"{'='*70}\n")
    
    final_ids = scan_range(ser, 1, 15)
    print(f"✅ Motors at IDs 1-15: {sorted(final_ids)}")
    print(f"   Count: {len(final_ids)}/15\n")
    
    ser.close()
    
    if len(final_ids) == 15:
        print("🎉 SUCCESS! All 15 motors configured!\n")
        print("Motors ready at IDs 1-15")
        print("\n📋 Recommended: Power cycle motors to clear old IDs")
    else:
        missing_final = sorted(set(range(1, 16)) - set(final_ids))
        print(f"⚠️  {len(final_ids)}/15 motors configured")
        print(f"   Still missing: {missing_final}\n")
        print("Next steps:")
        print("   1. POWER CYCLE all motors")
        print("   2. Run this script again")
        print("   3. Or manually configure remaining motors")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

