#!/usr/bin/env python3
"""
PROOF: Reconfigure a motor to a single CAN ID
Using RobStride USB-to-CAN adapter protocol
"""

import serial
import time
import struct

def send_command(ser, can_id, command_type, data):
    """Send command via RobStride adapter"""
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(command_type)
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(can_id)
    packet.extend(data)
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.2)
    
    return ser.read(200)

def activate_motor(ser, can_id):
    """Activate motor"""
    return send_command(ser, can_id, 0x00, [0x01, 0x00])

def deactivate_motor(ser, can_id):
    """Deactivate motor"""
    return send_command(ser, can_id, 0x00, [0x00, 0x00])

def set_can_id(ser, old_id, new_id):
    """
    Set new CAN ID for motor
    Based on RobStride protocol
    """
    print(f"\n{'='*70}")
    print(f"SETTING CAN ID: {old_id} → {new_id}")
    print(f"{'='*70}")
    
    # Step 1: Deactivate motor first
    print(f"\n1. Deactivating motor at ID {old_id}...")
    resp = deactivate_motor(ser, old_id)
    if resp:
        print(f"   ✅ Deactivated: {resp.hex(' ')}")
    else:
        print(f"   ⚠️  No response (motor may already be deactivated)")
    
    time.sleep(0.3)
    
    # Step 2: Send SET_CAN_ID command
    # Command format: AT 07 07 e8 <new_id> <old_id_bytes> 0d 0a
    # Based on RobStride protocol, command 0x07 = SET_CAN_ID
    print(f"\n2. Sending SET_CAN_ID command...")
    print(f"   Old ID: {old_id} (0x{old_id:02X})")
    print(f"   New ID: {new_id} (0x{new_id:02X})")
    
    # Pack old_id as 4 bytes (little endian)
    old_id_bytes = struct.pack('<I', old_id)
    
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(0x07)  # Command: SET_CAN_ID
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(new_id)  # New CAN ID
    packet.extend(old_id_bytes[:2])  # Old ID (first 2 bytes)
    packet.extend([0x0d, 0x0a])
    
    print(f"   Sending: {packet.hex(' ')}")
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    
    resp = ser.read(200)
    if resp:
        print(f"   ✅ Response: {resp.hex(' ')}")
    else:
        print(f"   ⚠️  No response")
    
    time.sleep(0.3)
    
    # Step 3: Save to flash (command 0x08)
    print(f"\n3. Saving to flash...")
    
    packet = bytearray([0x41, 0x54])
    packet.append(0x08)  # Command: SAVE_DATA
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(new_id)  # Use new ID
    packet.extend([0x00, 0x00])
    packet.extend([0x0d, 0x0a])
    
    print(f"   Sending: {packet.hex(' ')}")
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    
    resp = ser.read(200)
    if resp:
        print(f"   ✅ Saved: {resp.hex(' ')}")
    else:
        print(f"   ⚠️  No response")
    
    time.sleep(0.5)
    
    # Step 4: Verify new ID
    print(f"\n4. Verifying new ID {new_id}...")
    resp = activate_motor(ser, new_id)
    
    if resp and len(resp) > 0:
        print(f"   ✅ Motor responds at NEW ID {new_id}!")
        print(f"   Response: {resp.hex(' ')}")
        return True
    else:
        print(f"   ❌ Motor does NOT respond at new ID {new_id}")
        return False

def scan_motor_ids(ser, id_range):
    """Scan a range of IDs to see which respond"""
    responding = []
    
    for motor_id in id_range:
        resp = activate_motor(ser, motor_id)
        if resp and len(resp) > 0:
            responding.append(motor_id)
    
    return responding

print("="*70)
print("PROOF: RECONFIGURE MOTOR TO SINGLE CAN ID")
print("="*70)
print("\nUsing RobStride SET_CAN_ID protocol")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    # BEFORE: Scan motor 1 (IDs 8-39)
    print("="*70)
    print("BEFORE: Motor 1 Status")
    print("="*70)
    
    print("\nScanning IDs 8-39 (Motor 1's current range)...")
    before_ids = scan_motor_ids(ser, range(8, 40))
    
    print(f"\n✅ Motor 1 responds to {len(before_ids)} IDs:")
    print(f"   IDs: {before_ids}")
    
    # Choose an ID from the middle of the range
    old_id = 20  # Middle of 8-39 range
    new_id = 1   # Target: Single ID
    
    print(f"\n📋 PLAN:")
    print(f"   Current: Motor responds to IDs {before_ids[0]}-{before_ids[-1]}")
    print(f"   Action: Reconfigure using ID {old_id} → {new_id}")
    print(f"   Goal: Motor should ONLY respond to ID {new_id}")
    
    input("\nPress ENTER to proceed with reconfiguration...")
    
    # RECONFIGURE
    success = set_can_id(ser, old_id, new_id)
    
    if not success:
        print(f"\n⚠️  Reconfiguration may have failed, but let's verify...")
    
    time.sleep(1)
    
    # AFTER: Verify
    print(f"\n{'='*70}")
    print("AFTER: Verification")
    print(f"{'='*70}")
    
    # Check if motor still responds to old range
    print(f"\n1. Checking old ID range (8-39)...")
    after_old_range = scan_motor_ids(ser, range(8, 40))
    
    if after_old_range:
        print(f"   ⚠️  Motor still responds to {len(after_old_range)} old IDs: {after_old_range}")
    else:
        print(f"   ✅ Motor NO LONGER responds to old range!")
    
    # Check if motor responds to new ID
    print(f"\n2. Checking new ID {new_id}...")
    resp = activate_motor(ser, new_id)
    
    if resp and len(resp) > 0:
        print(f"   ✅ Motor responds at NEW ID {new_id}!")
        print(f"   Response: {resp.hex(' ')}")
        new_id_works = True
    else:
        print(f"   ❌ Motor does NOT respond at new ID {new_id}")
        new_id_works = False
    
    # Check surrounding IDs
    print(f"\n3. Checking IDs around {new_id} (0-7)...")
    after_new_range = scan_motor_ids(ser, range(0, 8))
    
    if after_new_range:
        print(f"   Motor responds to: {after_new_range}")
        if len(after_new_range) == 1 and after_new_range[0] == new_id:
            print(f"   ✅ PERFECT! Motor ONLY responds to ID {new_id}")
        else:
            print(f"   ⚠️  Motor responds to multiple IDs")
    else:
        print(f"   ❌ Motor doesn't respond to any ID in range 0-7")
    
    ser.close()
    
    # FINAL RESULT
    print(f"\n{'='*70}")
    print("FINAL RESULT")
    print(f"{'='*70}")
    
    if new_id_works and len(after_old_range) == 0:
        print(f"\n🎉 SUCCESS!")
        print(f"   ✅ Motor reconfigured from IDs {before_ids[0]}-{before_ids[-1]} → ID {new_id}")
        print(f"   ✅ Motor NO LONGER responds to old IDs")
        print(f"   ✅ Motor ONLY responds to new ID {new_id}")
        print(f"\n✅ PROOF COMPLETE: SET_CAN_ID protocol works!")
        
    elif new_id_works:
        print(f"\n⚠️  PARTIAL SUCCESS")
        print(f"   ✅ Motor responds at new ID {new_id}")
        print(f"   ⚠️  Motor still responds to some old IDs: {after_old_range}")
        print(f"\n   This may require:")
        print(f"   1. Power cycle the motor")
        print(f"   2. Or reconfigure again from each old ID")
        
    else:
        print(f"\n❌ FAILED")
        print(f"   Motor does not respond at new ID {new_id}")
        print(f"   Motor still at old IDs: {after_old_range if after_old_range else 'unknown'}")
        print(f"\n   Possible issues:")
        print(f"   1. Wrong SET_CAN_ID command format")
        print(f"   2. Motor needs power cycle to apply changes")
        print(f"   3. Motor requires different configuration sequence")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

