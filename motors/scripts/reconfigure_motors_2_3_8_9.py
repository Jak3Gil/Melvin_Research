#!/usr/bin/env python3
"""
Reconfigure motors to match their motor numbers
Motor 2: IDs 16-20 → ID 2
Motor 3: IDs 21-30 → ID 3
Motor 8: ID 64 → ID 8
Motor 9: ID 73 → ID 9
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
    Returns True if successful
    """
    print(f"\n{'='*70}")
    print(f"Reconfiguring: ID {old_id} → ID {new_id}")
    print(f"{'='*70}")
    
    # Step 1: Deactivate motor
    print(f"1. Deactivating motor at ID {old_id}...")
    resp = deactivate_motor(ser, old_id)
    if resp:
        print(f"   ✅ Response: {resp.hex(' ')}")
    time.sleep(0.3)
    
    # Step 2: Send SET_CAN_ID command (0x07)
    print(f"2. Setting CAN ID {old_id} → {new_id}...")
    
    old_id_bytes = struct.pack('<I', old_id)
    
    packet = bytearray([0x41, 0x54])
    packet.append(0x07)  # SET_CAN_ID
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(new_id)
    packet.extend(old_id_bytes[:2])
    packet.extend([0x0d, 0x0a])
    
    print(f"   Sending: {packet.hex(' ')}")
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    
    resp = ser.read(200)
    if resp:
        print(f"   ✅ Response: {resp.hex(' ')}")
    time.sleep(0.3)
    
    # Step 3: Save to flash (0x08)
    print(f"3. Saving to flash...")
    
    packet = bytearray([0x41, 0x54])
    packet.append(0x08)  # SAVE_DATA
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(new_id)
    packet.extend([0x00, 0x00])
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    
    resp = ser.read(200)
    if resp:
        print(f"   ✅ Saved: {resp.hex(' ')}")
    time.sleep(0.5)
    
    # Step 4: Verify
    print(f"4. Verifying new ID {new_id}...")
    resp = activate_motor(ser, new_id)
    
    if resp and len(resp) > 0:
        print(f"   ✅ Motor responds at ID {new_id}!")
        print(f"   Response: {resp.hex(' ')}")
        return True
    else:
        print(f"   ⚠️  No response at ID {new_id}")
        return False

def verify_motor(ser, motor_id):
    """Check if motor responds at given ID"""
    resp = activate_motor(ser, motor_id)
    return resp and len(resp) > 0

print("="*70)
print("RECONFIGURE MOTORS 2, 3, 8, 9")
print("="*70)
print("\nMapping:")
print("  Motor 2: IDs 16-20 → ID 2")
print("  Motor 3: IDs 21-30 → ID 3")
print("  Motor 8: ID 64 → ID 8")
print("  Motor 9: ID 73 → ID 9")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    # Configuration plan
    motors = [
        {"name": "Motor 2", "old_id": 18, "new_id": 2},  # Middle of 16-20 range
        {"name": "Motor 3", "old_id": 25, "new_id": 3},  # Middle of 21-30 range
        {"name": "Motor 8", "old_id": 64, "new_id": 8},
        {"name": "Motor 9", "old_id": 73, "new_id": 9},
    ]
    
    results = []
    
    for motor in motors:
        name = motor["name"]
        old_id = motor["old_id"]
        new_id = motor["new_id"]
        
        print(f"\n{'#'*70}")
        print(f"CONFIGURING {name}")
        print(f"{'#'*70}")
        
        # Verify motor exists at old ID
        print(f"\nVerifying {name} at old ID {old_id}...")
        if not verify_motor(ser, old_id):
            print(f"   ⚠️  {name} not responding at ID {old_id}")
            results.append({"motor": name, "success": False, "reason": "Not found at old ID"})
            continue
        else:
            print(f"   ✅ {name} found at ID {old_id}")
        
        # Reconfigure
        success = set_can_id(ser, old_id, new_id)
        
        if success:
            print(f"\n✅ {name} successfully reconfigured to ID {new_id}")
            results.append({"motor": name, "success": True, "old_id": old_id, "new_id": new_id})
        else:
            print(f"\n⚠️  {name} reconfiguration may have failed")
            results.append({"motor": name, "success": False, "reason": "No response at new ID"})
        
        time.sleep(1)
    
    # Final verification
    print(f"\n{'='*70}")
    print("FINAL VERIFICATION")
    print(f"{'='*70}")
    
    print(f"\nChecking all new IDs (2, 3, 8, 9)...")
    
    final_status = {}
    for new_id in [2, 3, 8, 9]:
        print(f"\nID {new_id}...", end='', flush=True)
        if verify_motor(ser, new_id):
            print(f" ✅ Motor responds!")
            final_status[new_id] = True
        else:
            print(f" ❌ No response")
            final_status[new_id] = False
    
    # Check old IDs are gone
    print(f"\n\nChecking old IDs are no longer responding...")
    old_ids_to_check = [18, 25, 64, 73]
    
    for old_id in old_ids_to_check:
        print(f"Old ID {old_id}...", end='', flush=True)
        if verify_motor(ser, old_id):
            print(f" ⚠️  Still responds (may need power cycle)")
        else:
            print(f" ✅ No longer responds")
    
    ser.close()
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r["success"])
    
    print(f"\n✅ Successfully reconfigured: {successful}/4 motors")
    
    for result in results:
        if result["success"]:
            print(f"   ✅ {result['motor']}: ID {result['old_id']} → ID {result['new_id']}")
        else:
            print(f"   ❌ {result['motor']}: {result['reason']}")
    
    if successful == 4:
        print(f"\n🎉 ALL MOTORS RECONFIGURED!")
        print(f"\nMotor IDs now match motor numbers:")
        print(f"   Motor 2 → CAN ID 2")
        print(f"   Motor 3 → CAN ID 3")
        print(f"   Motor 8 → CAN ID 8")
        print(f"   Motor 9 → CAN ID 9")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Power cycle motors to ensure changes persist")
        print(f"   2. Find and configure remaining motors")
        print(f"   3. Test motor movements at new IDs")
    else:
        print(f"\n⚠️  Some motors failed to reconfigure")
        print(f"   Try power cycling the motors and running again")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

