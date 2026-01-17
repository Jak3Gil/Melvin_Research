#!/usr/bin/env python3
"""
Find all 15 motors using RobStride USB-to-CAN adapter protocol
Based on your l91_motor.cpp implementation!
"""

import serial
import time
import struct

def send_robstride_command(ser, can_id, command_type, data):
    """
    Send command via RobStride USB-to-CAN adapter
    Format from l91_motor.cpp: AT <cmd> 07 e8 <can_id> <data> 0d 0a
    """
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(command_type)
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(can_id)
    packet.extend(data)
    packet.extend([0x0d, 0x0a])  # \r\n
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)
    
    return ser.read(200)

def activate_motor(ser, can_id):
    """Activate motor - from l91_motor.cpp activateMotor()"""
    # Format: AT 00 07 e8 <can_id> 01 00 0d 0a
    return send_robstride_command(ser, can_id, 0x00, [0x01, 0x00])

def deactivate_motor(ser, can_id):
    """Deactivate motor - from l91_motor.cpp deactivateMotor()"""
    # Format: AT 00 07 e8 <can_id> 00 00 0d 0a
    return send_robstride_command(ser, can_id, 0x00, [0x00, 0x00])

print("="*70)
print("FIND ALL 15 MOTORS - ROBSTRIDE USB-TO-CAN ADAPTER")
print("="*70)
print("\nUsing CORRECT RobStride adapter protocol from your l91_motor.cpp!")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    # Test 1: Quick scan of known IDs
    print("="*70)
    print("TEST 1: Quick Scan of Known Motor IDs")
    print("="*70)
    
    test_ids = [1, 8, 12, 13, 14, 16, 20, 24, 31, 32, 64, 72, 100, 120]
    found_ids = []
    
    for motor_id in test_ids:
        print(f"Testing motor ID {motor_id}...", end='', flush=True)
        
        resp = activate_motor(ser, motor_id)
        
        if resp and len(resp) > 0:
            print(f" ✅ RESPONDS!")
            print(f"  Response: {resp.hex(' ')}")
            found_ids.append(motor_id)
        else:
            print(f" -")
    
    if found_ids:
        print(f"\n✅ Found {len(found_ids)} motors!")
        print(f"   IDs: {found_ids}")
        
        # Full scan
        print("\n" + "="*70)
        print("TEST 2: Full Scan (0-127)")
        print("="*70)
        
        all_found = []
        
        for motor_id in range(0, 128):
            if motor_id % 16 == 0:
                print(f"  Scanning {motor_id}-{min(motor_id+15, 127)}...", end='', flush=True)
            
            resp = activate_motor(ser, motor_id)
            
            if resp and len(resp) > 0:
                all_found.append(motor_id)
                if motor_id % 16 != 0:
                    print(f"\n    ✓ ID {motor_id}", end='')
            elif motor_id % 16 == 15:
                print(" -")
        
        print("\n")
        
        if all_found:
            print(f"✅ Total IDs found: {len(all_found)}")
            print(f"   IDs: {all_found}")
            
            # Group into motors
            groups = []
            if all_found:
                current_group = [all_found[0]]
                for i in range(1, len(all_found)):
                    if all_found[i] == all_found[i-1] + 1:
                        current_group.append(all_found[i])
                    else:
                        groups.append(current_group)
                        current_group = [all_found[i]]
                groups.append(current_group)
            
            print(f"\n✅ Motor Groups: {len(groups)}")
            for i, group in enumerate(groups, 1):
                print(f"   Motor {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
            
            if len(groups) >= 15:
                print(f"\n🎉 FOUND ALL 15 MOTORS!")
            else:
                print(f"\n⚠️  Found {len(groups)} motors, need {15 - len(groups)} more")
                
                # Try extended range
                print("\n" + "="*70)
                print("TEST 3: Extended Range (128-255)")
                print("="*70)
                
                extended_found = []
                
                for motor_id in range(128, 256):
                    if motor_id % 16 == 0:
                        print(f"  Scanning {motor_id}-{min(motor_id+15, 255)}...", end='', flush=True)
                    
                    resp = activate_motor(ser, motor_id)
                    
                    if resp and len(resp) > 0:
                        extended_found.append(motor_id)
                        if motor_id % 16 != 0:
                            print(f"\n    ✓ ID {motor_id}", end='')
                    elif motor_id % 16 == 15:
                        print(" -")
                
                if extended_found:
                    print(f"\n\n✅ Found motors in extended range!")
                    print(f"   IDs: {extended_found}")
                    all_found.extend(extended_found)
    else:
        print(f"\n✗ No motors found in quick scan")
        
        # Try full scan anyway
        print("\n" + "="*70)
        print("TEST 2: Full Scan (0-255)")
        print("="*70)
        
        all_found = []
        
        for motor_id in range(0, 256):
            if motor_id % 32 == 0:
                print(f"  Scanning {motor_id}-{min(motor_id+31, 255)}...", end='', flush=True)
            
            resp = activate_motor(ser, motor_id)
            
            if resp and len(resp) > 0:
                all_found.append(motor_id)
                print(f"\n    ✓ ID {motor_id}", end='', flush=True)
            elif motor_id % 32 == 31:
                print(" -")
        
        print("\n")
        
        if all_found:
            print(f"✅ Found {len(all_found)} responding IDs!")
            print(f"   IDs: {all_found}")
        else:
            print(f"❌ NO MOTORS FOUND")
    
    # Test 3: Listen for responses
    print("\n" + "="*70)
    print("TEST 3: Listen for Spontaneous Responses")
    print("="*70)
    
    ser.reset_input_buffer()
    print("Listening for 3 seconds...")
    
    start_time = time.time()
    responses = []
    
    while time.time() - start_time < 3:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            responses.append(data)
            print(f"  [{time.time()-start_time:.2f}s] {len(data)} bytes: {data.hex(' ')}")
        time.sleep(0.1)
    
    if responses:
        print(f"\n✅ Received {len(responses)} spontaneous response(s)")
    else:
        print(f"\n✗ No spontaneous responses")
    
    ser.close()
    
    # FINAL SUMMARY
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    if all_found:
        # Group motors
        groups = []
        if all_found:
            sorted_ids = sorted(all_found)
            current_group = [sorted_ids[0]]
            for i in range(1, len(sorted_ids)):
                if sorted_ids[i] == sorted_ids[i-1] + 1:
                    current_group.append(sorted_ids[i])
                else:
                    groups.append(current_group)
                    current_group = [sorted_ids[i]]
            groups.append(current_group)
        
        print(f"\n✅ SUCCESS!")
        print(f"   Total responding IDs: {len(all_found)}")
        print(f"   Estimated motors: {len(groups)}")
        print(f"\n   Motor groups:")
        for i, group in enumerate(groups, 1):
            print(f"     Motor {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
        
        if len(groups) >= 15:
            print(f"\n🎉 FOUND ALL 15 MOTORS!")
            print(f"\nNext step: Reconfigure them to unique IDs 1-15")
        else:
            print(f"\n⚠️  Found {len(groups)} motors, missing {15 - len(groups)}")
            print(f"\nPossible reasons for missing motors:")
            print(f"  1. Motors powered off")
            print(f"  2. Different baud rate")
            print(f"  3. On different CAN bus/adapter")
    else:
        print(f"\n❌ NO MOTORS FOUND")
        print(f"\nThis means:")
        print(f"  1. Motors not connected to /dev/ttyUSB0")
        print(f"  2. Motors have no power")
        print(f"  3. Wrong baud rate (try 115200, 230400, 460800)")
        print(f"  4. CAN wiring issue")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

