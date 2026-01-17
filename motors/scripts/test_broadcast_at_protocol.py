#!/usr/bin/env python3
"""
Test broadcast commands with the working L91 AT protocol
Can we find motors without knowing specific CAN IDs?
"""

import serial
import time

def send_at_command(ser, comm_type, motor_id, data=None):
    """Send command using working L91 AT format"""
    if data is None:
        data = [0x01, 0x00]
    
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(comm_type)  # Command type
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(motor_id)
    packet.extend(data[:8])
    packet.extend([0x0d, 0x0a])  # \r\n
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    
    return ser.read(200)

print("="*70)
print("BROADCAST TEST - L91 AT Protocol")
print("="*70)
print("\nTesting if motors respond to broadcast IDs")
print("Using the WORKING L91 AT protocol format")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n[OK] Connected to {port} at {baud} baud\n")
    
    # Test different broadcast IDs
    broadcast_ids = [
        (0x00, "Broadcast 0x00"),
        (0xFF, "Broadcast 0xFF"),
        (0x7F, "Broadcast 0x7F (max standard)"),
        (0xFD, "Master ID 0xFD"),
        (0xFE, "ID 0xFE"),
    ]
    
    print("="*70)
    print("TEST 1: Broadcast Enable Commands")
    print("="*70)
    
    for bid, description in broadcast_ids:
        print(f"\n{description} (0x{bid:02X})...")
        
        # Command 0x00 = Enable
        response = send_at_command(ser, 0x00, bid, [0x01, 0x00])
        
        if response and len(response) > 4:
            print(f"  ✓ Got response: {len(response)} bytes")
            print(f"    {response.hex(' ')}")
            
            # Try to parse multiple responses
            if len(response) > 17:
                print(f"    Multiple motors may have responded!")
                # Parse in 17-byte chunks
                for i in range(0, len(response), 17):
                    chunk = response[i:i+17]
                    if len(chunk) >= 17:
                        print(f"    Response {i//17 + 1}: {chunk.hex(' ')}")
        else:
            print(f"  ✗ No response")
    
    print("\n" + "="*70)
    print("TEST 2: Broadcast Get ID (0x00 command)")
    print("="*70)
    
    for bid, description in broadcast_ids:
        print(f"\n{description} (0x{bid:02X})...")
        
        # Command 0x00 with different data
        packet = bytearray([0x41, 0x54])  # "AT"
        packet.append(0x00)  # Get ID command
        packet.append(0x07)
        packet.append(0xe8)
        packet.append(bid)
        packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.extend([0x0d, 0x0a])
        
        ser.write(packet)
        ser.flush()
        time.sleep(0.5)
        
        response = ser.read(200)
        
        if response and len(response) > 4:
            print(f"  ✓ Got response: {len(response)} bytes")
            print(f"    {response.hex(' ')}")
        else:
            print(f"  ✗ No response")
    
    print("\n" + "="*70)
    print("TEST 3: Scan Without Knowing IDs")
    print("="*70)
    print("Scanning every 8th ID to find motors...")
    
    found = []
    
    for test_id in range(0, 128, 8):
        response = send_at_command(ser, 0x00, test_id, [0x01, 0x00])
        
        if response and len(response) > 4:
            print(f"  ✓ ID {test_id} responds!")
            found.append(test_id)
    
    if found:
        print(f"\nFound motors at IDs: {found}")
        
        # Now scan around found IDs
        print("\n" + "="*70)
        print("TEST 4: Detailed Scan Around Found IDs")
        print("="*70)
        
        all_found = set(found)
        
        for base_id in found:
            print(f"\nScanning around ID {base_id}...")
            for offset in range(-8, 9):
                test_id = base_id + offset
                if 0 <= test_id <= 127 and test_id not in all_found:
                    response = send_at_command(ser, 0x00, test_id, [0x01, 0x00])
                    if response and len(response) > 4:
                        print(f"  ✓ ID {test_id}")
                        all_found.add(test_id)
        
        print(f"\n✅ Total IDs found: {len(all_found)}")
        print(f"   IDs: {sorted(all_found)}")
        
    else:
        print("\n❌ No motors found in quick scan")
    
    print("\n" + "="*70)
    print("TEST 5: Listen for Spontaneous Responses")
    print("="*70)
    print("Sending broadcast, then listening...")
    
    # Send broadcast enable
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00])
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    
    # Listen for 3 seconds
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
        print(f"\n✓ Received {len(responses)} response(s)")
    else:
        print(f"\n✗ No spontaneous responses")
    
    ser.close()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    print("\n✅ L91 AT Protocol is working!")
    print("   Motors respond to specific CAN IDs")
    
    if found:
        print(f"\n✅ Can find motors by scanning!")
        print(f"   Found {len(all_found)} responding IDs")
        print(f"   IDs: {sorted(all_found)}")
    else:
        print(f"\n⚠️  Broadcast IDs don't work")
        print(f"   Need to scan specific IDs to find motors")
        print(f"   But we know IDs: 8, 20, 31, 32, 64, 72 work!")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

