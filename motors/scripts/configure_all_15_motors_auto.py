#!/usr/bin/env python3
"""
Configure all 15 motors to unique IDs 1-15 (Non-interactive)
Systematically separate motors from overlapping ID ranges
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
    time.sleep(0.15)
    
    return ser.read(200)

def activate_motor(ser, can_id):
    """Activate motor"""
    return send_command(ser, can_id, 0x00, [0x01, 0x00])

def deactivate_motor(ser, can_id):
    """Deactivate motor"""
    return send_command(ser, can_id, 0x00, [0x00, 0x00])

def set_can_id(ser, old_id, new_id):
    """Set new CAN ID for motor"""
    print(f"  Setting ID {old_id} → {new_id}...", end='', flush=True)
    
    # Deactivate
    deactivate_motor(ser, old_id)
    time.sleep(0.2)
    
    # Set CAN ID
    old_id_bytes = struct.pack('<I', old_id)
    packet = bytearray([0x41, 0x54, 0x07, 0x07, 0xe8, new_id])
    packet.extend(old_id_bytes[:2])
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    ser.read(200)
    
    # Save to flash
    packet = bytearray([0x41, 0x54, 0x08, 0x07, 0xe8, new_id, 0x00, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    ser.read(200)
    
    # Verify
    time.sleep(0.3)
    resp = activate_motor(ser, new_id)
    
    if resp and len(resp) > 0:
        print(f" ✅")
        return True
    else:
        print(f" ⚠️")
        return False

def scan_range(ser, start, end):
    """Scan a range and return responding IDs"""
    responding = []
    for motor_id in range(start, end + 1):
        resp = activate_motor(ser, motor_id)
        if resp and len(resp) > 0:
            responding.append(motor_id)
    return responding

print("="*70)
print("CONFIGURE ALL 15 MOTORS TO UNIQUE IDs 1-15 (AUTO)")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    # Initial scan
    print("Initial scan...")
    all_ids = scan_range(ser, 0, 127)
    
    # Group consecutive IDs
    groups = []
    if all_ids:
        current_group = [all_ids[0]]
        for i in range(1, len(all_ids)):
            if all_ids[i] == all_ids[i-1] + 1:
                current_group.append(all_ids[i])
            else:
                groups.append(current_group)
                current_group = [all_ids[i]]
        groups.append(current_group)
    
    print(f"Found {len(groups)} motor groups with {len(all_ids)} responding IDs\n")
    for i, group in enumerate(groups, 1):
        print(f"  Group {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
    
    # Configuration plan: Use IDs spread across the ranges
    config_plan = [
        {"target_id": 1, "source_id": 8},
        {"target_id": 2, "source_id": 16},
        {"target_id": 3, "source_id": 24},
        {"target_id": 4, "source_id": 32},
        {"target_id": 5, "source_id": 12},
        {"target_id": 6, "source_id": 20},
        {"target_id": 7, "source_id": 28},
        {"target_id": 8, "source_id": 64},
        {"target_id": 9, "source_id": 72},
        {"target_id": 10, "source_id": 36},
        {"target_id": 11, "source_id": 68},
        {"target_id": 12, "source_id": 76},
        {"target_id": 13, "source_id": 10},
        {"target_id": 14, "source_id": 18},
        {"target_id": 15, "source_id": 26},
    ]
    
    print(f"\n{'='*70}")
    print("CONFIGURING MOTORS")
    print(f"{'='*70}\n")
    
    configured = []
    
    for i, plan in enumerate(config_plan, 1):
        source_id = plan['source_id']
        target_id = plan['target_id']
        
        print(f"[{i:2d}/15] Motor {target_id}: ", end='', flush=True)
        
        # Check if source ID still responds
        resp = activate_motor(ser, source_id)
        
        if not resp or len(resp) == 0:
            # Check if already at target
            resp = activate_motor(ser, target_id)
            if resp and len(resp) > 0:
                print(f"Already at ID {target_id} ✅")
                configured.append(target_id)
            else:
                print(f"Source ID {source_id} not found ⚠️")
            continue
        
        # Reconfigure
        success = set_can_id(ser, source_id, target_id)
        
        if success:
            configured.append(target_id)
        
        time.sleep(0.3)
    
    # Final verification
    print(f"\n{'='*70}")
    print("FINAL VERIFICATION")
    print(f"{'='*70}\n")
    
    print("Scanning IDs 1-15...")
    final_ids = scan_range(ser, 1, 15)
    
    print(f"\n✅ Motors at target IDs: {final_ids}")
    print(f"   Count: {len(final_ids)}/15\n")
    
    # Check old ranges
    print("Checking old ID ranges...")
    old_range_1 = scan_range(ser, 8, 39)
    old_range_2 = scan_range(ser, 64, 79)
    
    remaining = len(old_range_1) + len(old_range_2)
    
    if old_range_1:
        print(f"  IDs 8-39: {len(old_range_1)} still responding")
    if old_range_2:
        print(f"  IDs 64-79: {len(old_range_2)} still responding")
    
    if remaining == 0:
        print(f"  ✅ All old ranges clear!")
    
    ser.close()
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    if len(final_ids) == 15:
        print(f"🎉 SUCCESS! All 15 motors configured!\n")
        print(f"Motors now at IDs 1-15:")
        for motor_id in sorted(final_ids):
            print(f"  ✅ Motor {motor_id}")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Power cycle motors (optional, to clear old IDs)")
        print(f"   2. Test each motor: python3 move_motor_test.py")
        print(f"   3. Ready for full robot control!")
        
    elif len(final_ids) >= 10:
        print(f"⚠️  Configured {len(final_ids)}/15 motors\n")
        print(f"Working IDs: {sorted(final_ids)}")
        
        missing = sorted(set(range(1, 16)) - set(final_ids))
        print(f"Missing IDs: {missing}")
        
        print(f"\nRecommendations:")
        print(f"   1. Power cycle all motors")
        print(f"   2. Run this script again")
        print(f"   3. Remaining motors will be configured")
        
    else:
        print(f"❌ Only {len(final_ids)}/15 motors configured\n")
        print(f"Working IDs: {sorted(final_ids)}")
        
        print(f"\nTroubleshooting:")
        print(f"   1. Check if all 15 motors have power")
        print(f"   2. Power cycle all motors")
        print(f"   3. Run: python3 find_motors_robstride_adapter.py")
        print(f"   4. Verify all motors are on same CAN bus")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

