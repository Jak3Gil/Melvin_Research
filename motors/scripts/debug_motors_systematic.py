#!/usr/bin/env python3
"""
Systematic motor debugging - find what changed
Hardware confirmed working, so this is a protocol/configuration issue
"""

import serial
import time
import struct

def test_protocol_1_at(ser, motor_id):
    """L91 AT Protocol - Original working format"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id])
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)
    return ser.read(200)

def test_protocol_2_checksum(ser, motor_id):
    """L91 Checksum Protocol - From instant_test.py"""
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)
    return ser.read(200)

def test_protocol_3_simple_at(ser, motor_id):
    """Simplified AT command"""
    packet = bytearray([0x41, 0x54, motor_id, 0x00, 0x01, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)
    return ser.read(200)

def test_protocol_4_raw_enable(ser, motor_id):
    """Raw enable command"""
    packet = bytearray([0x01, motor_id, 0x01, 0x00])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)
    return ser.read(200)

def test_all_baud_rates(port, motor_id=8):
    """Test different baud rates"""
    baud_rates = [115200, 230400, 460800, 921600, 1000000, 2000000]
    
    print("="*70)
    print("BAUD RATE SCAN")
    print("="*70)
    
    for baud in baud_rates:
        print(f"\nTesting {baud} baud...")
        try:
            ser = serial.Serial(port, baud, timeout=0.5)
            time.sleep(0.3)
            
            # Try AT protocol
            resp = test_protocol_1_at(ser, motor_id)
            if resp and len(resp) > 4:
                print(f"  ✅ FOUND! Motor responds at {baud} baud")
                print(f"     Response: {resp.hex(' ')}")
                ser.close()
                return baud
            
            ser.close()
            print(f"  ✗ No response at {baud}")
            
        except Exception as e:
            print(f"  ✗ Error at {baud}: {e}")
    
    return None

print("="*70)
print("SYSTEMATIC MOTOR DEBUGGING")
print("="*70)
print("\nHardware confirmed working - debugging protocol/config")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    # STEP 1: Test all baud rates
    print("\n" + "="*70)
    print("STEP 1: Baud Rate Detection")
    print("="*70)
    
    working_baud = test_all_baud_rates(port)
    
    if working_baud:
        print(f"\n✅ Motors respond at {working_baud} baud!")
        baud = working_baud
    else:
        print(f"\n⚠️  No response at any standard baud rate")
        print(f"   Continuing with 921600...")
    
    # STEP 2: Test all protocols at working baud
    print("\n" + "="*70)
    print("STEP 2: Protocol Detection")
    print("="*70)
    
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    
    protocols = [
        ("L91 AT Protocol", test_protocol_1_at),
        ("L91 Checksum Protocol", test_protocol_2_checksum),
        ("Simple AT", test_protocol_3_simple_at),
        ("Raw Enable", test_protocol_4_raw_enable),
    ]
    
    working_protocol = None
    
    for proto_name, proto_func in protocols:
        print(f"\nTesting {proto_name}...")
        
        test_ids = [1, 8, 16, 20, 24, 31, 32, 64, 72, 100, 120]
        found = []
        
        for motor_id in test_ids:
            resp = proto_func(ser, motor_id)
            if resp and len(resp) > 4:
                found.append(motor_id)
                print(f"  ✓ ID {motor_id} responds!")
        
        if found:
            print(f"  ✅ {proto_name} WORKS!")
            print(f"     Found IDs: {found}")
            working_protocol = (proto_name, proto_func)
            break
        else:
            print(f"  ✗ No response")
    
    # STEP 3: Full scan with working protocol
    if working_protocol:
        print("\n" + "="*70)
        print(f"STEP 3: Full Scan with {working_protocol[0]}")
        print("="*70)
        
        proto_func = working_protocol[1]
        all_found = []
        
        print("\nScanning IDs 0-255...")
        for test_id in range(0, 256):
            if test_id % 32 == 0:
                print(f"  Scanning {test_id}-{min(test_id+31, 255)}...", end='', flush=True)
            
            resp = proto_func(ser, test_id)
            if resp and len(resp) > 4:
                all_found.append(test_id)
                if test_id % 32 != 0:
                    print(f"\n    ✓ ID {test_id}", end='')
            elif test_id % 32 == 31:
                print(" -")
        
        print("\n")
        
        if all_found:
            print(f"\n✅ Found {len(all_found)} responding IDs!")
            print(f"   IDs: {all_found}")
            
            # Group into motors
            groups = []
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
            
            if len(groups) < 15:
                print(f"\n⚠️  Found {len(groups)} motors, need 15 total")
                print(f"   Missing: {15 - len(groups)} motors")
    
    # STEP 4: Try passive listening
    if not working_protocol:
        print("\n" + "="*70)
        print("STEP 4: Passive CAN Bus Listening")
        print("="*70)
        print("\nNo active protocol working - trying passive listening...")
        print("Listening for 10 seconds...")
        
        ser.reset_input_buffer()
        start_time = time.time()
        packets = []
        
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                packets.append((time.time() - start_time, data))
                print(f"  [{time.time()-start_time:.2f}s] {len(data)} bytes: {data.hex(' ')}")
            time.sleep(0.05)
        
        if packets:
            print(f"\n✅ Detected {len(packets)} CAN packets!")
            print("   Motors are communicating, but not responding to our commands")
        else:
            print(f"\n✗ No CAN bus activity detected")
    
    # STEP 5: Try sending broadcast and listening
    print("\n" + "="*70)
    print("STEP 5: Broadcast + Listen Strategy")
    print("="*70)
    
    broadcast_commands = [
        ("AT Broadcast 0x00", bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])),
        ("AT Broadcast 0xFF", bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])),
        ("Checksum Broadcast", bytearray([0xAA, 0x55, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])),
        ("Query All", bytearray([0x41, 0x54, 0x02, 0x07, 0xe8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])),
    ]
    
    for cmd_name, cmd_packet in broadcast_commands:
        print(f"\nTrying {cmd_name}...")
        print(f"  Sending: {cmd_packet.hex(' ')}")
        
        ser.reset_input_buffer()
        ser.write(cmd_packet)
        ser.flush()
        
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"  ✅ Got response: {len(response)} bytes")
            print(f"     {response.hex(' ')}")
        else:
            print(f"  ✗ No response")
    
    ser.close()
    
    # FINAL SUMMARY
    print("\n" + "="*70)
    print("DEBUGGING SUMMARY")
    print("="*70)
    
    if working_protocol:
        print(f"\n✅ SUCCESS!")
        print(f"   Working Protocol: {working_protocol[0]}")
        print(f"   Working Baud: {baud}")
        print(f"   Motors Found: {len(groups)}")
        
        if len(groups) < 15:
            print(f"\n📋 NEXT STEPS:")
            print(f"   1. Found {len(groups)} motors, need {15 - len(groups)} more")
            print(f"   2. Check if missing motors are on different CAN bus")
            print(f"   3. Check if missing motors have different baud rate")
            print(f"   4. Power cycle motors one at a time to identify")
    else:
        print(f"\n❌ NO PROTOCOL WORKING")
        print(f"\nPossible issues:")
        print(f"  1. Motors in wrong mode (need protocol switch?)")
        print(f"  2. Motors waiting for specific initialization sequence")
        print(f"  3. CAN bus configuration issue")
        print(f"  4. Motors in error/protection state")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"  1. Try power cycling all motors")
        print(f"  2. Check motor documentation for initialization sequence")
        print(f"  3. Try RobStride Motor Studio software first")
        print(f"  4. Check if motors need firmware update")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

