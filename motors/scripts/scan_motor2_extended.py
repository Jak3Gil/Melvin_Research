#!/usr/bin/env python3
"""
Extended Motor 2 scan - IDs 1-255 and raw packet tests
"""
import serial
import struct
import time
import sys

def calculate_checksum(data):
    """Calculate L91 protocol checksum"""
    return sum(data[2:]) & 0xFF

def scan_all_ids(port, baudrate):
    """Scan ALL possible CAN IDs (1-255)"""
    print("=" * 70)
    print("  EXTENDED SCAN: IDs 1-255")
    print("=" * 70)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"\n✓ Connected to {port} at {baudrate} baud\n")
        
        # Send AT command
        ser.write(b'AT+AT\r\n')
        time.sleep(0.2)
        response = ser.read(100)
        if response:
            print(f"Adapter: {response.decode('utf-8', errors='ignore').strip()}\n")
        
        found = []
        
        print("Scanning... (this will take 3-4 minutes)")
        print("=" * 70)
        
        for motor_id in range(1, 256):
            # Show progress
            if motor_id % 25 == 0:
                print(f"  Progress: {motor_id}/255 ({int(motor_id/255*100)}%)")
            
            # Clear buffer
            ser.reset_input_buffer()
            
            # Create enable packet
            packet = bytearray([0xAA, 0x55, 0x01, motor_id & 0xFF])
            packet.extend(struct.pack('<I', motor_id))
            packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            packet.append(calculate_checksum(packet))
            
            ser.write(packet)
            time.sleep(0.12)  # Give motor time to respond
            
            response = ser.read(100)
            
            if response and len(response) > 0:
                print(f"\n  ✅ FOUND at ID {motor_id} (0x{motor_id:02X})")
                print(f"     Response: {response.hex()}")
                print(f"     Length: {len(response)} bytes\n")
                found.append(motor_id)
                time.sleep(0.2)
        
        ser.close()
        
        print("\n" + "=" * 70)
        print("  RESULTS")
        print("=" * 70)
        
        if found:
            print(f"\n✅ Found {len(found)} motor(s): {found}")
            return found
        else:
            print(f"\n❌ No motors found in range 1-255")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_raw_packets(port, baudrate):
    """Test with various raw packet formats"""
    print("\n" + "=" * 70)
    print("  RAW PACKET TESTS")
    print("=" * 70)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"\n✓ Connected\n")
        
        tests = [
            ("Broadcast ID 0", bytearray([0xAA, 0x55, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02])),
            ("Broadcast ID 255", bytearray([0xAA, 0x55, 0x01, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01])),
            ("Motor 2 (ID 16)", bytearray([0xAA, 0x55, 0x01, 0x10, 0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x12])),
            ("Motor 2 (ID 2)", bytearray([0xAA, 0x55, 0x01, 0x02, 0x02, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04])),
        ]
        
        for name, packet in tests:
            print(f"Test: {name}")
            print(f"  Packet: {packet.hex()}")
            
            ser.reset_input_buffer()
            ser.write(packet)
            time.sleep(0.3)
            
            response = ser.read(100)
            if response:
                print(f"  ✅ Response: {response.hex()}")
            else:
                print(f"  ⚠️  No response")
            print()
        
        ser.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def listen_passive(port, baudrate, duration=10):
    """Passively listen for any CAN traffic"""
    print("\n" + "=" * 70)
    print(f"  PASSIVE LISTENING ({duration} seconds)")
    print("=" * 70)
    print("\nListening for ANY data from motor...")
    print("(Motor might send status updates if powered)\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        
        start = time.time()
        msg_count = 0
        
        while time.time() - start < duration:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                msg_count += 1
                print(f"  [{msg_count}] Received: {data.hex()}")
                print(f"      ASCII: {data.decode('utf-8', errors='ignore')}")
            time.sleep(0.1)
        
        ser.close()
        
        if msg_count == 0:
            print("  ⚠️  No data received")
            print("     Motor is not transmitting spontaneously")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n🔍 Extended Motor 2 Scanner\n")
    
    port = '/dev/ttyUSB1'
    baudrate = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Configuration:")
    print(f"  Port: {port}")
    print(f"  Baudrate: {baudrate}\n")
    
    # Test 1: Passive listening
    print("=" * 70)
    print("TEST 1: PASSIVE LISTENING")
    print("=" * 70)
    listen_passive(port, baudrate, 5)
    
    # Test 2: Raw packet tests
    print("\n" + "=" * 70)
    print("TEST 2: RAW PACKET TESTS")
    print("=" * 70)
    test_raw_packets(port, baudrate)
    
    # Test 3: Full scan
    print("\n" + "=" * 70)
    print("TEST 3: FULL ID SCAN (1-255)")
    print("=" * 70)
    print("\nDo you want to scan ALL IDs 1-255? (takes 3-4 minutes)")
    print("Press Enter to continue, or Ctrl+C to skip...")
    
    try:
        input()
        found = scan_all_ids(port, baudrate)
        
        if found:
            print(f"\n✅ Motor 2 found at ID(s): {found}")
        else:
            print("\n❌ Motor 2 not found")
            print("\nPossible reasons:")
            print("  1. Motor is not powered")
            print("  2. CAN wiring not connected")
            print("  3. Motor needs 120Ω termination resistor")
            print("  4. Motor firmware issue")
    except KeyboardInterrupt:
        print("\n\n⏹️  Scan cancelled")

if __name__ == "__main__":
    main()

