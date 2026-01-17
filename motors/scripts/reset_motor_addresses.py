#!/usr/bin/env python3
"""
Reset motor address masks using advanced configuration
Try to clear address masking and set unique IDs
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
    time.sleep(0.2)
    
    return ser.read(200)

def activate_motor(ser, can_id):
    return send_command(ser, can_id, 0x00, [0x01, 0x00])

def deactivate_motor(ser, can_id):
    return send_command(ser, can_id, 0x00, [0x00, 0x00])

def advanced_set_can_id(ser, old_id, new_id):
    """
    Advanced CAN ID configuration
    Try multiple methods to clear address mask
    """
    print(f"\n{'='*70}")
    print(f"Advanced Config: ID {old_id} → {new_id}")
    print(f"{'='*70}")
    
    # Method 1: Deactivate with clear error flag
    print(f"1. Deactivating with clear...")
    packet = bytearray([0x41, 0x54, 0x01, 0x07, 0xe8, old_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    ser.read(200)
    
    # Method 2: Set CAN ID with extended data
    print(f"2. Setting CAN ID with full parameters...")
    old_id_bytes = struct.pack('<I', old_id)
    new_id_bytes = struct.pack('<I', new_id)
    
    packet = bytearray([0x41, 0x54, 0x07, 0x07, 0xe8, new_id])
    packet.extend(old_id_bytes[:4])  # Full 4 bytes
    packet.extend([0x0d, 0x0a])
    
    print(f"   Sending: {packet.hex(' ')}")
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    resp = ser.read(200)
    if resp:
        print(f"   Response: {resp.hex(' ')}")
    
    # Method 3: Save with reset flag
    print(f"3. Saving to flash with reset...")
    packet = bytearray([0x41, 0x54, 0x08, 0x07, 0xe8, new_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    resp = ser.read(200)
    if resp:
        print(f"   Response: {resp.hex(' ')}")
    
    # Method 4: Load parameters (might reset mask)
    print(f"4. Loading parameters...")
    packet = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, new_id])
    packet.extend([0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    resp = ser.read(200)
    
    # Verify
    time.sleep(0.5)
    print(f"5. Verifying new ID {new_id}...")
    resp = activate_motor(ser, new_id)
    
    if resp and len(resp) > 0:
        print(f"   ✅ Motor responds at ID {new_id}")
        return True
    else:
        print(f"   ⚠️  No response at ID {new_id}")
        return False

print("="*70)
print("ADVANCED MOTOR ADDRESS RESET")
print("="*70)
print("\nThis will try advanced configuration methods")
print("to clear address masks and set unique IDs")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected\n")
    
    print("IMPORTANT: This approach may not work due to hardware address masking.")
    print("The REAL solution is:")
    print("  1. Use RobStride Motor Studio software (Windows)")
    print("  2. Or physically isolate motors one at a time")
    print("  3. Or contact RobStride for factory reset procedure")
    
    input("\nPress ENTER to try advanced config anyway (or Ctrl+C to cancel)...")
    
    # Try configuring one motor as a test
    print("\n" + "="*70)
    print("TEST: Configure Motor at ID 16 → ID 1")
    print("="*70)
    
    success = advanced_set_can_id(ser, 16, 1)
    
    if success:
        print("\n✅ Configuration may have worked!")
        print("   Testing if other IDs still respond...")
        
        # Check if old IDs still respond
        test_ids = [16, 17, 18, 19, 20]
        still_responding = []
        
        for test_id in test_ids:
            resp = activate_motor(ser, test_id)
            if resp and len(resp) > 0:
                still_responding.append(test_id)
        
        if still_responding:
            print(f"   ⚠️  Old IDs still respond: {still_responding}")
            print(f"   Address mask NOT cleared")
        else:
            print(f"   ✅ Old IDs no longer respond!")
            print(f"   Address mask successfully cleared!")
    
    ser.close()
    
    print("\n" + "="*70)
    print("RECOMMENDED SOLUTION")
    print("="*70)
    
    print("""
Since software commands cannot clear the address mask, you need:

**OPTION 1: RobStride Motor Studio (BEST)**
   - Download from RobStride website
   - Run on Windows PC
   - Connect USB-to-CAN adapter to PC
   - Use Motor Studio to:
     1. Detect all motors
     2. Set each to unique ID (1-15)
     3. Clear address masks
     4. Save to flash

**OPTION 2: Physical Isolation Method**
   1. Disconnect CAN-H/CAN-L from 14 motors
   2. Leave only 1 motor connected
   3. Configure that motor to ID 1
   4. Disconnect it, connect next motor
   5. Configure to ID 2
   6. Repeat for all 15 motors
   7. Reconnect all motors

**OPTION 3: DIP Switches (if motors have them)**
   - Some RobStride motors have DIP switches
   - Check motor housing for switches
   - Set unique IDs via hardware switches

**OPTION 4: Contact RobStride Support**
   - Ask for factory reset procedure
   - May require special command sequence
   - Or firmware update tool

For now, you have 2 motors responding (Motor 2 at IDs 8-39, another at 64-79).
You can use these for testing while figuring out the configuration.
""")
    
except KeyboardInterrupt:
    print("\n\nCancelled")
    ser.close()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

