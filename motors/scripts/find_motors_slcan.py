#!/usr/bin/env python3
"""
Find and configure RobStride motors using SLCAN/SocketCAN
Now using proper CAN protocol instead of L91 serial
"""

import can
import time
import struct

def send_can_message(bus, can_id, data):
    """Send CAN message"""
    msg = can.Message(
        arbitration_id=can_id,
        data=data,
        is_extended_id=False
    )
    try:
        bus.send(msg)
        return True
    except can.CanError as e:
        print(f"CAN Error: {e}")
        return False

def listen_for_response(bus, timeout=0.2):
    """Listen for CAN responses"""
    responses = []
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        msg = bus.recv(timeout=0.05)
        if msg:
            responses.append(msg)
    
    return responses

def scan_motors_mit(bus, id_range):
    """Scan for motors using MIT protocol"""
    print(f"Scanning IDs {id_range[0]}-{id_range[-1]} (MIT protocol)...")
    found = []
    
    for motor_id in id_range:
        # MIT enable command: 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFC
        data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC]
        send_can_message(bus, motor_id, data)
        
        # Listen for response
        responses = listen_for_response(bus, 0.1)
        
        if responses:
            found.append(motor_id)
            print(f"  ✓ ID {motor_id} responds (MIT)")
            for resp in responses:
                print(f"    Response: ID=0x{resp.arbitration_id:03X}, Data={resp.data.hex(' ')}")
    
    return found

def scan_motors_standard(bus, id_range):
    """Scan for motors using standard CAN frames"""
    print(f"Scanning IDs {id_range[0]}-{id_range[-1]} (Standard CAN)...")
    found = []
    
    for motor_id in id_range:
        # Send simple enable/query frame
        data = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        send_can_message(bus, motor_id, data)
        
        # Listen for response
        responses = listen_for_response(bus, 0.1)
        
        if responses:
            found.append(motor_id)
            print(f"  ✓ ID {motor_id} responds (Standard)")
    
    return found

print("="*70)
print("FIND MOTORS USING SLCAN/SocketCAN")
print("="*70)
print("\nUsing proper CAN protocol via slcan0 interface")
print("="*70)

try:
    # Connect to slcan0
    print("\nConnecting to slcan0...")
    bus = can.interface.Bus(channel='slcan0', interface='socketcan')
    print("✅ Connected to slcan0\n")
    
    # Show interface status
    import subprocess
    result = subprocess.run(['ip', 'link', 'show', 'slcan0'], 
                          capture_output=True, text=True)
    print("Interface status:")
    print(result.stdout)
    
    # Test 1: Scan with MIT protocol
    print("="*70)
    print("TEST 1: MIT Protocol Scan")
    print("="*70 + "\n")
    
    mit_motors = []
    mit_motors += scan_motors_mit(bus, range(1, 21))
    mit_motors += scan_motors_mit(bus, range(21, 41))
    mit_motors += scan_motors_mit(bus, range(64, 81))
    
    if mit_motors:
        print(f"\n✅ Found {len(mit_motors)} motors with MIT protocol!")
        print(f"   IDs: {mit_motors}")
    else:
        print(f"\n✗ No motors found with MIT protocol")
    
    # Test 2: Scan with standard CAN
    print("\n" + "="*70)
    print("TEST 2: Standard CAN Scan")
    print("="*70 + "\n")
    
    std_motors = []
    std_motors += scan_motors_standard(bus, range(1, 21))
    std_motors += scan_motors_standard(bus, range(21, 41))
    std_motors += scan_motors_standard(bus, range(64, 81))
    
    if std_motors:
        print(f"\n✅ Found {len(std_motors)} motors with Standard CAN!")
        print(f"   IDs: {std_motors}")
    else:
        print(f"\n✗ No motors found with Standard CAN")
    
    # Test 3: Listen for spontaneous traffic
    print("\n" + "="*70)
    print("TEST 3: Listen for Spontaneous CAN Traffic")
    print("="*70 + "\n")
    
    print("Listening for 5 seconds...")
    spontaneous = listen_for_response(bus, 5.0)
    
    if spontaneous:
        print(f"\n✅ Received {len(spontaneous)} CAN messages!")
        unique_ids = set(msg.arbitration_id for msg in spontaneous)
        print(f"   Unique CAN IDs: {sorted(unique_ids)}")
        
        # Show first few messages
        print(f"\n   Sample messages:")
        for msg in spontaneous[:10]:
            print(f"     ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex(' ')}")
    else:
        print(f"\n✗ No spontaneous CAN traffic")
    
    bus.shutdown()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    
    all_found = set(mit_motors + std_motors)
    
    if all_found:
        print(f"✅ Found {len(all_found)} unique motor IDs!")
        print(f"   IDs: {sorted(all_found)}")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Test motor movement via SocketCAN")
        print(f"   2. Configure motors to unique IDs")
        print(f"   3. This should properly handle address masks")
    else:
        print(f"⚠️  No motors found via SocketCAN")
        print(f"\nPossible reasons:")
        print(f"   1. Motors still using L91 protocol (not standard CAN)")
        print(f"   2. Need to send different initialization sequence")
        print(f"   3. Bitrate mismatch (SLCAN is at 1Mbps)")
        
        print(f"\nTo try different bitrate:")
        print(f"   sudo killall slcand")
        print(f"   sudo slcand -o -c -s6 /dev/ttyUSB0 slcan0  # 500kbps")
        print(f"   sudo ip link set slcan0 up")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    
    print(f"\n📋 Make sure SLCAN is set up:")
    print(f"   sudo bash test_slcan_setup.sh")

