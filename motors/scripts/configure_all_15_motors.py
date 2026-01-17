#!/usr/bin/env python3
"""
Configure all 15 motors to unique IDs 1-15
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
    print(f"\n  Setting ID {old_id} → {new_id}...")
    
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
        print(f"  ✅ Motor now at ID {new_id}")
        return True
    else:
        print(f"  ⚠️  No response at ID {new_id}")
        return False

def scan_range(ser, start, end):
    """Scan a range and return responding IDs"""
    responding = []
    for motor_id in range(start, end + 1):
        resp = activate_motor(ser, motor_id)
        if resp and len(resp) > 0:
            responding.append(motor_id)
    return responding

def move_motor_test(ser, can_id, duration=1.0):
    """Briefly move motor to identify it physically"""
    print(f"  Moving motor at ID {can_id} for {duration}s...")
    
    # Activate
    activate_motor(ser, can_id)
    time.sleep(0.2)
    
    # Move slowly
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, 0x01, 0x81, 0x48])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    
    time.sleep(duration)
    
    # Stop
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, 0x00, 0x7f, 0xff])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.2)

print("="*70)
print("CONFIGURE ALL 15 MOTORS TO UNIQUE IDs 1-15")
print("="*70)
print("\nStrategy: Systematically separate overlapping motors")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    # Initial scan
    print("="*70)
    print("INITIAL SCAN")
    print("="*70)
    
    print("\nScanning IDs 0-127...")
    all_ids = scan_range(ser, 0, 127)
    
    print(f"\nFound {len(all_ids)} responding IDs")
    
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
    
    print(f"Motor groups: {len(groups)}")
    for i, group in enumerate(groups, 1):
        print(f"  Group {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
    
    # Configuration plan: Use IDs spread across the ranges
    # This ensures we grab different physical motors
    config_plan = [
        {"target_id": 1, "source_id": 8, "name": "Motor 1"},
        {"target_id": 2, "source_id": 16, "name": "Motor 2"},
        {"target_id": 3, "source_id": 24, "name": "Motor 3"},
        {"target_id": 4, "source_id": 32, "name": "Motor 4"},
        {"target_id": 5, "source_id": 12, "name": "Motor 5"},
        {"target_id": 6, "source_id": 20, "name": "Motor 6"},
        {"target_id": 7, "source_id": 28, "name": "Motor 7"},
        {"target_id": 8, "source_id": 64, "name": "Motor 8"},
        {"target_id": 9, "source_id": 72, "name": "Motor 9"},
        {"target_id": 10, "source_id": 36, "name": "Motor 10"},
        {"target_id": 11, "source_id": 68, "name": "Motor 11"},
        {"target_id": 12, "source_id": 76, "name": "Motor 12"},
        {"target_id": 13, "source_id": 10, "name": "Motor 13"},
        {"target_id": 14, "source_id": 18, "name": "Motor 14"},
        {"target_id": 15, "source_id": 26, "name": "Motor 15"},
    ]
    
    print("\n" + "="*70)
    print("CONFIGURATION PLAN")
    print("="*70)
    
    for plan in config_plan:
        print(f"  {plan['name']}: ID {plan['source_id']} → ID {plan['target_id']}")
    
    input("\nPress ENTER to start configuration (or Ctrl+C to cancel)...")
    
    # Configure each motor
    configured = []
    
    for i, plan in enumerate(config_plan, 1):
        print(f"\n{'='*70}")
        print(f"CONFIGURING {plan['name']} ({i}/15)")
        print(f"{'='*70}")
        
        source_id = plan['source_id']
        target_id = plan['target_id']
        
        # Check if source ID still responds
        print(f"\nChecking source ID {source_id}...")
        resp = activate_motor(ser, source_id)
        
        if not resp or len(resp) == 0:
            print(f"  ⚠️  ID {source_id} no longer responds (already configured?)")
            
            # Check if target ID responds
            resp = activate_motor(ser, target_id)
            if resp and len(resp) > 0:
                print(f"  ✅ Motor already at target ID {target_id}")
                configured.append(target_id)
            continue
        
        print(f"  ✅ Found motor at ID {source_id}")
        
        # Optional: Move motor to identify it
        print(f"\n  Testing motor movement (watch which motor moves)...")
        move_motor_test(ser, source_id, 1.5)
        
        # Reconfigure
        success = set_can_id(ser, source_id, target_id)
        
        if success:
            configured.append(target_id)
            print(f"\n✅ {plan['name']} configured successfully!")
        else:
            print(f"\n⚠️  {plan['name']} configuration uncertain")
        
        # Show progress
        print(f"\nProgress: {len(configured)}/15 motors configured")
        print(f"Configured IDs: {sorted(configured)}")
        
        time.sleep(0.5)
    
    # Final verification
    print(f"\n{'='*70}")
    print("FINAL VERIFICATION")
    print(f"{'='*70}")
    
    print(f"\nScanning IDs 1-15...")
    final_ids = scan_range(ser, 1, 15)
    
    print(f"\n✅ Motors responding at target IDs: {final_ids}")
    print(f"   Count: {len(final_ids)}/15")
    
    # Check for any remaining overlapping IDs
    print(f"\nChecking for remaining overlapping IDs...")
    old_range_1 = scan_range(ser, 8, 39)
    old_range_2 = scan_range(ser, 64, 79)
    
    if old_range_1:
        print(f"  ⚠️  IDs 8-39 still has {len(old_range_1)} responding: {old_range_1[:10]}...")
    else:
        print(f"  ✅ IDs 8-39 clear")
    
    if old_range_2:
        print(f"  ⚠️  IDs 64-79 still has {len(old_range_2)} responding: {old_range_2}")
    else:
        print(f"  ✅ IDs 64-79 clear")
    
    ser.close()
    
    # Summary
    print(f"\n{'='*70}")
    print("CONFIGURATION COMPLETE")
    print(f"{'='*70}")
    
    if len(final_ids) == 15:
        print(f"\n🎉 SUCCESS! All 15 motors configured!")
        print(f"\nMotors now at IDs 1-15:")
        for motor_id in final_ids:
            print(f"  ✅ Motor {motor_id} → ID {motor_id}")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Power cycle motors to ensure changes persist")
        print(f"   2. Test each motor individually")
        print(f"   3. Create motor control library")
    else:
        print(f"\n⚠️  Configured {len(final_ids)}/15 motors")
        print(f"   Responding at: {final_ids}")
        
        missing = set(range(1, 16)) - set(final_ids)
        if missing:
            print(f"   Missing IDs: {sorted(missing)}")
            print(f"\n   Recommendations:")
            print(f"   1. Power cycle all motors")
            print(f"   2. Run this script again")
            print(f"   3. Check if some motors need different source IDs")
    
    print()
    
except KeyboardInterrupt:
    print(f"\n\n⚠️  Configuration interrupted by user")
    print(f"   Run again to continue from where you left off")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

