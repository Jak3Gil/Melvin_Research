#!/usr/bin/env python3
"""
Verify motor IDs after reconfiguration
Check IDs 2, 3, 8, 9 and old IDs
"""

import serial
import time

def activate_motor(ser, can_id):
    """Activate motor"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)
    return ser.read(200)

print("="*70)
print("VERIFY MOTOR IDS")
print("="*70)
print("\nChecking if motors respond at new IDs...")
print("(Power cycle motors if they don't respond)")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected\n")
    
    # Check new IDs
    print("NEW IDs (Target):")
    print("-" * 70)
    
    new_ids = {
        2: "Motor 2",
        3: "Motor 3", 
        8: "Motor 8",
        9: "Motor 9"
    }
    
    working_new = []
    
    for motor_id, name in new_ids.items():
        resp = activate_motor(ser, motor_id)
        if resp and len(resp) > 0:
            print(f"  ✅ ID {motor_id} ({name}): RESPONDS")
            working_new.append(motor_id)
        else:
            print(f"  ❌ ID {motor_id} ({name}): No response")
    
    # Check old IDs
    print(f"\nOLD IDs (Should NOT respond):")
    print("-" * 70)
    
    old_ids = {
        18: "Motor 2 old",
        25: "Motor 3 old",
        64: "Motor 8 old",
        73: "Motor 9 old"
    }
    
    still_old = []
    
    for motor_id, name in old_ids.items():
        resp = activate_motor(ser, motor_id)
        if resp and len(resp) > 0:
            print(f"  ⚠️  ID {motor_id} ({name}): Still responds (needs power cycle)")
            still_old.append(motor_id)
        else:
            print(f"  ✅ ID {motor_id} ({name}): No longer responds")
    
    # Full scan to see what's actually responding
    print(f"\nFULL SCAN (IDs 0-127):")
    print("-" * 70)
    
    all_responding = []
    
    for motor_id in range(0, 128):
        resp = activate_motor(ser, motor_id)
        if resp and len(resp) > 0:
            all_responding.append(motor_id)
    
    print(f"All responding IDs: {all_responding}")
    
    # Group consecutive IDs
    if all_responding:
        groups = []
        current_group = [all_responding[0]]
        for i in range(1, len(all_responding)):
            if all_responding[i] == all_responding[i-1] + 1:
                current_group.append(all_responding[i])
            else:
                groups.append(current_group)
                current_group = [all_responding[i]]
        groups.append(current_group)
        
        print(f"\nMotor groups found: {len(groups)}")
        for i, group in enumerate(groups, 1):
            if len(group) == 1:
                print(f"  Group {i}: ID {group[0]} (single ID - GOOD!)")
            else:
                print(f"  Group {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs - needs config)")
    
    ser.close()
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    if len(working_new) == 4:
        print(f"\n🎉 ALL 4 MOTORS AT CORRECT IDs!")
        print(f"   ✅ Motor 2 → ID 2")
        print(f"   ✅ Motor 3 → ID 3")
        print(f"   ✅ Motor 8 → ID 8")
        print(f"   ✅ Motor 9 → ID 9")
    else:
        print(f"\n⚠️  {len(working_new)}/4 motors at correct IDs")
        print(f"   Working: {working_new}")
        
        if still_old:
            print(f"\n   Motors still at old IDs: {still_old}")
            print(f"   → POWER CYCLE the motors to apply changes")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

