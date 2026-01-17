#!/usr/bin/env python3
"""
Find Motor 2 - Scan all possible CAN IDs using L91 protocol
"""
import serial
import struct
import time
import sys

def calculate_checksum(data):
    """Calculate L91 protocol checksum"""
    return sum(data[2:]) & 0xFF

def create_enable_packet(motor_id):
    """Create motor enable packet"""
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(calculate_checksum(packet))
    return packet

def scan_range(ser, start_id, end_id, description):
    """Scan a range of CAN IDs"""
    print(f"\n{'=' * 70}")
    print(f"  {description}")
    print(f"  Scanning IDs {start_id}-{end_id}")
    print(f"{'=' * 70}\n")
    
    found = []
    
    for motor_id in range(start_id, end_id + 1):
        # Show progress every 10 IDs
        if (motor_id - start_id) % 10 == 0:
            print(f"  Progress: Testing ID {motor_id}...")
        
        # Clear buffer
        ser.reset_input_buffer()
        
        # Send enable command
        packet = create_enable_packet(motor_id)
        ser.write(packet)
        time.sleep(0.15)  # Give motor time to respond
        
        # Check for response
        response = ser.read(100)
        
        if response and len(response) > 0:
            print(f"\n  ✅ FOUND MOTOR at ID {motor_id} (0x{motor_id:02X})")
            print(f"     Response: {response.hex()}")
            print(f"     Length: {len(response)} bytes\n")
            found.append(motor_id)
            time.sleep(0.2)
        
        time.sleep(0.05)
    
    return found

def main():
    print("\n🔍 Motor 2 Finder - L91 Protocol\n")
    
    port = '/dev/ttyUSB1'
    baudrate = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Configuration:")
    print(f"  Port: {port}")
    print(f"  Baudrate: {baudrate}")
    print(f"  Protocol: L91")
    print()
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"✓ Connected to {port}\n")
        
        # Send AT command
        print("Sending AT+AT detection command...")
        ser.write(b'AT+AT\r\n')
        time.sleep(0.2)
        response = ser.read(100)
        if response:
            print(f"  Response: {response.decode('utf-8', errors='ignore').strip()}")
        print()
        
        all_found = []
        
        # Scan different ranges
        ranges = [
            (1, 15, "Range 1: Standard IDs (1-15)"),
            (16, 30, "Range 2: Motor 2 Expected Range (16-30)"),
            (31, 50, "Range 3: Extended Range (31-50)"),
            (51, 79, "Range 4: High Range (51-79)"),
            (80, 127, "Range 5: Very High Range (80-127)")
        ]
        
        print("=" * 70)
        print("  STARTING COMPREHENSIVE SCAN")
        print("=" * 70)
        print("\nThis will take about 2-3 minutes...")
        print("Press Ctrl+C to stop early if motor is found.\n")
        
        try:
            for start, end, description in ranges:
                found = scan_range(ser, start, end, description)
                if found:
                    all_found.extend(found)
                    print(f"\n  ✅ Found {len(found)} motor(s) in this range: {found}")
                else:
                    print(f"  ⚠️  No motors found in range {start}-{end}")
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Scan stopped by user")
        
        ser.close()
        
        # Summary
        print(f"\n\n{'=' * 70}")
        print("  SCAN COMPLETE")
        print(f"{'=' * 70}\n")
        
        if all_found:
            print(f"✅ SUCCESS! Found {len(all_found)} motor(s): {all_found}")
            print(f"\n📝 Motor 2 is at CAN ID: {all_found[0]}")
            print(f"\nTo test this motor:")
            print(f"  python3 test_motor2_l91.py {port} {baudrate}")
            print(f"\nOr test specific ID:")
            print(f"  python3 quick_motor_test.py {port} {baudrate} {all_found[0]}")
        else:
            print("❌ No motors found in any range (1-127)")
            print("\nPossible issues:")
            print("  1. Motor 2 is not powered on")
            print("  2. Motor 2 is not connected to the CAN bus")
            print("  3. Wrong baudrate - try:")
            print(f"     python3 find_motor2_l91.py {port} 115200")
            print("  4. Motor might be at ID > 127")
            print("  5. CAN wiring issue (check CAN-H, CAN-L, GND)")
        
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        print(f"\nCheck:")
        print(f"  1. Port exists: ls -la {port}")
        print(f"  2. User permissions: sudo usermod -a -G dialout $USER")
        print(f"  3. Port not in use: sudo lsof {port}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
