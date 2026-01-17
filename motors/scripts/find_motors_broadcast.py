#!/usr/bin/env python3
"""
Find Motors Using Broadcast/Detection Commands
Does NOT rely on specific CAN IDs - uses broadcast and detection methods
"""

import serial
import struct
import time

def send_packet(ser, command, motor_id, data=None):
    """Send packet in working format"""
    if data is None:
        data = [0x00] * 8
    
    packet = bytearray([0xAA, 0x55])  # Header
    packet.append(command)  # Command type
    packet.extend(struct.pack('<I', motor_id))  # Motor ID (4 bytes)
    packet.extend(data[:8])  # Data (8 bytes)
    
    # Checksum
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.15)
    
    return ser.read(200)

def broadcast_detect(ser):
    """
    Send broadcast detection command
    Command 0x00 = Get ID (should work on all motors)
    """
    print("\n" + "="*70)
    print("METHOD 1: Broadcast Get ID (0x00)")
    print("="*70)
    
    responses = []
    
    # Try different broadcast IDs
    broadcast_ids = [0x00, 0xFF, 0x7F, 0xFD, 0xFE]
    
    for bid in broadcast_ids:
        print(f"\nTrying broadcast ID 0x{bid:02X}...")
        response = send_packet(ser, 0x00, bid)  # Command 0x00 = Get ID
        
        if response and len(response) > 4:
            print(f"  ✓ Got response: {len(response)} bytes")
            print(f"    Data: {response.hex(' ')}")
            responses.append((bid, response))
            
            # Parse unique ID if present
            if len(response) >= 16:
                try:
                    unique_id = struct.unpack('<Q', response[8:16])[0]
                    print(f"    Unique ID: 0x{unique_id:016X}")
                except:
                    pass
        else:
            print(f"  ✗ No response")
        
        time.sleep(0.3)
    
    return responses

def scan_with_enable(ser, start=1, end=127, step=1):
    """
    Scan by sending enable commands and looking for ANY response
    """
    print("\n" + "="*70)
    print(f"METHOD 2: Enable Scan (IDs {start}-{end}, step={step})")
    print("="*70)
    
    found = []
    
    for motor_id in range(start, end + 1, step):
        if motor_id % 20 == 0:
            print(f"  Progress: {motor_id}/{end}...")
        
        # Command 0x01 = Enable
        response = send_packet(ser, 0x01, motor_id)
        
        if response and len(response) > 4:
            print(f"\n  ✓ ID {motor_id} (0x{motor_id:02X}) responds!")
            print(f"    Response: {response.hex(' ')}")
            found.append(motor_id)
        
        time.sleep(0.05)
    
    return found

def listen_for_traffic(ser, duration=5.0):
    """
    Just listen for any CAN traffic
    """
    print("\n" + "="*70)
    print(f"METHOD 3: Passive Listen ({duration}s)")
    print("="*70)
    print("Listening for any spontaneous motor traffic...")
    
    traffic = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            timestamp = time.time() - start_time
            traffic.append((timestamp, data))
            print(f"  [{timestamp:.2f}s] Received {len(data)} bytes: {data.hex(' ')}")
        time.sleep(0.1)
    
    if not traffic:
        print("  ✗ No spontaneous traffic detected")
    
    return traffic

def send_broadcast_enable(ser):
    """
    Send broadcast enable to wake up all motors
    """
    print("\n" + "="*70)
    print("METHOD 4: Broadcast Enable to All Motors")
    print("="*70)
    
    broadcast_ids = [0x00, 0xFF]
    
    for bid in broadcast_ids:
        print(f"\nSending enable to broadcast ID 0x{bid:02X}...")
        response = send_packet(ser, 0x01, bid)  # Command 0x01 = Enable
        
        if response:
            print(f"  Response: {response.hex(' ')}")
        else:
            print(f"  No response")
        
        time.sleep(0.5)

def quick_sample_scan(ser, sample_ids):
    """
    Quick scan of known good IDs from previous scans
    """
    print("\n" + "="*70)
    print("METHOD 5: Quick Sample Scan")
    print("="*70)
    print(f"Testing known IDs: {sample_ids}")
    
    found = []
    
    for motor_id in sample_ids:
        print(f"\n  Testing ID {motor_id}...", end=" ")
        response = send_packet(ser, 0x01, motor_id)  # Enable
        
        if response and len(response) > 4:
            print(f"✓ RESPONDS")
            print(f"    Response: {response.hex(' ')}")
            found.append(motor_id)
        else:
            print("✗")
        
        time.sleep(0.1)
    
    return found

def main():
    port = '/dev/ttyUSB0'
    baud = 921600
    
    print("="*70)
    print("FIND MOTORS - Broadcast/Detection Methods")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}")
    print("\nThis script uses multiple methods to find motors")
    print("WITHOUT relying on specific CAN IDs")
    print("="*70)
    
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
        time.sleep(0.5)
        print("\n[OK] Serial port opened\n")
        
        all_found = set()
        
        # Method 1: Broadcast Get ID
        broadcast_responses = broadcast_detect(ser)
        if broadcast_responses:
            print(f"\n✓ Method 1: Got {len(broadcast_responses)} broadcast responses")
        
        # Method 2: Quick sample scan of known IDs
        sample_ids = [8, 9, 10, 20, 31, 32, 64, 72]
        found_sample = quick_sample_scan(ser, sample_ids)
        all_found.update(found_sample)
        if found_sample:
            print(f"\n✓ Method 2: Found {len(found_sample)} motors: {found_sample}")
        
        # Method 3: Broadcast enable
        send_broadcast_enable(ser)
        
        # Method 4: Listen for traffic
        traffic = listen_for_traffic(ser, duration=3.0)
        if traffic:
            print(f"\n✓ Method 3: Detected {len(traffic)} traffic events")
        
        # Method 5: Fast scan with larger steps
        print("\n" + "="*70)
        print("METHOD 6: Fast Scan (every 8th ID)")
        print("="*70)
        found_fast = scan_with_enable(ser, 1, 127, step=8)
        all_found.update(found_fast)
        if found_fast:
            print(f"\n✓ Method 6: Found {len(found_fast)} motors: {found_fast}")
        
        # If we found some IDs, do detailed scan around them
        if all_found:
            print("\n" + "="*70)
            print("METHOD 7: Detailed Scan Around Found IDs")
            print("="*70)
            
            for base_id in sorted(all_found):
                # Scan ±8 IDs around each found ID
                start = max(1, base_id - 8)
                end = min(127, base_id + 8)
                print(f"\nScanning around ID {base_id}: {start}-{end}")
                
                for test_id in range(start, end + 1):
                    response = send_packet(ser, 0x01, test_id)
                    if response and len(response) > 4:
                        if test_id not in all_found:
                            print(f"  ✓ Found new ID: {test_id}")
                            all_found.add(test_id)
                    time.sleep(0.05)
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        if all_found:
            print(f"\n✅ Found {len(all_found)} responding CAN IDs:")
            print(f"   IDs: {sorted(all_found)}")
            
            # Group consecutive IDs
            sorted_ids = sorted(all_found)
            groups = []
            current_group = [sorted_ids[0]]
            
            for i in range(1, len(sorted_ids)):
                if sorted_ids[i] == current_group[-1] + 1:
                    current_group.append(sorted_ids[i])
                else:
                    groups.append(current_group)
                    current_group = [sorted_ids[i]]
            groups.append(current_group)
            
            print(f"\n   Grouped by range:")
            for group in groups:
                if len(group) > 1:
                    print(f"     IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
                else:
                    print(f"     ID {group[0]}")
            
            print(f"\n   Estimated physical motors: {len(groups)}")
            
        else:
            print("\n❌ No motors found!")
            print("\n   Possible reasons:")
            print("   1. Motors not powered on")
            print("   2. CAN bus not connected")
            print("   3. Missing termination resistors")
            print("   4. Wrong baud rate")
            print("   5. Hardware issues")
            
            print("\n   Try:")
            print("   1. Check motor power LEDs")
            print("   2. Verify CAN-H, CAN-L, GND connections")
            print("   3. Add 120Ω termination at both ends")
            print("   4. Power cycle motors")
        
        ser.close()
        print("\n[OK] Scan complete\n")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if 'ser' in locals():
            ser.close()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()

if __name__ == '__main__':
    main()

