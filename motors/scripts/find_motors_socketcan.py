#!/usr/bin/env python3
"""
Find all 15 motors using SocketCAN (the CORRECT way!)
We were using serial - should have been using CAN interface!
"""

import can
import struct
import time

def send_l91_command(bus, motor_id, command_type=0x00, data=None):
    """Send L91 command via CAN"""
    if data is None:
        data = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    
    # L91 protocol uses CAN ID as motor ID
    # Data format: [command_type, ...data...]
    can_data = [command_type] + data[:7]
    
    msg = can.Message(
        arbitration_id=motor_id,
        data=can_data,
        is_extended_id=False
    )
    
    try:
        bus.send(msg)
        return True
    except can.CanError:
        return False

def listen_for_responses(bus, timeout=0.5):
    """Listen for CAN responses"""
    responses = []
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        msg = bus.recv(timeout=0.1)
        if msg:
            responses.append(msg)
    
    return responses

print("="*70)
print("FIND ALL 15 MOTORS - SOCKETCAN (CORRECT METHOD!)")
print("="*70)
print("\nUsing SocketCAN interface - the proper way!")
print("="*70)

# Try both can0 and can1
for can_interface in ['can0', 'can1']:
    print(f"\n{'='*70}")
    print(f"Testing {can_interface}")
    print(f"{'='*70}")
    
    try:
        # Create CAN bus
        bus = can.interface.Bus(channel=can_interface, bustype='socketcan')
        print(f"✅ Connected to {can_interface}")
        
        # Clear any pending messages
        while bus.recv(timeout=0.1):
            pass
        
        # Test 1: Quick scan of known IDs
        print(f"\nTest 1: Quick Scan of Known IDs")
        print("-" * 70)
        
        test_ids = [1, 8, 16, 20, 24, 31, 32, 64, 72, 100, 120]
        found_ids = []
        
        for motor_id in test_ids:
            # Send enable command
            send_l91_command(bus, motor_id, 0x00, [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            
            # Listen for response
            time.sleep(0.05)
            msg = bus.recv(timeout=0.1)
            
            if msg:
                print(f"  ✅ Motor ID {motor_id} responds!")
                print(f"     CAN ID: 0x{msg.arbitration_id:03X}, Data: {msg.data.hex(' ')}")
                found_ids.append(motor_id)
        
        if found_ids:
            print(f"\n✅ Found {len(found_ids)} motors on {can_interface}!")
            print(f"   IDs: {found_ids}")
            
            # Do full scan
            print(f"\nTest 2: Full Scan (0-127)")
            print("-" * 70)
            
            all_found = []
            
            for motor_id in range(0, 128):
                if motor_id % 16 == 0:
                    print(f"  Scanning {motor_id}-{min(motor_id+15, 127)}...", end='', flush=True)
                
                send_l91_command(bus, motor_id, 0x00, [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                time.sleep(0.02)
                
                msg = bus.recv(timeout=0.05)
                if msg:
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
        else:
            print(f"\n✗ No motors found on {can_interface}")
        
        # Test 3: Listen for spontaneous traffic
        print(f"\nTest 3: Listen for Spontaneous CAN Traffic")
        print("-" * 70)
        print("Listening for 3 seconds...")
        
        start_time = time.time()
        packets = []
        
        while time.time() - start_time < 3:
            msg = bus.recv(timeout=0.1)
            if msg:
                packets.append(msg)
                print(f"  [{time.time()-start_time:.2f}s] ID: 0x{msg.arbitration_id:03X}, Data: {msg.data.hex(' ')}")
        
        if packets:
            print(f"\n✅ Received {len(packets)} CAN packets")
            
            # Extract unique IDs
            unique_ids = set(msg.arbitration_id for msg in packets)
            print(f"   Unique CAN IDs: {sorted(unique_ids)}")
        else:
            print(f"\n✗ No spontaneous traffic")
        
        bus.shutdown()
        
    except Exception as e:
        print(f"✗ Error on {can_interface}: {e}")
        print(f"   Make sure interface is UP:")
        print(f"   sudo ip link set {can_interface} type can bitrate 1000000")
        print(f"   sudo ip link set {can_interface} up")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
✅ Now using SocketCAN - the CORRECT method!

If motors still don't respond:
  1. Check CAN bitrate matches motors (try 500000, 1000000)
  2. Check physical CAN wiring to can0/can1
  3. Verify motors are powered
  4. Check termination resistors

To reconfigure CAN interface:
  sudo ip link set can0 down
  sudo ip link set can0 type can bitrate 500000
  sudo ip link set can0 up
""")


