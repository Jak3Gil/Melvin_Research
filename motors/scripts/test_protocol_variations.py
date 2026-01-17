#!/usr/bin/env python3
"""
Test different protocol variations to find what works
Since hardware is good (power + termination), maybe protocol needs adjustment
"""

import serial
import struct
import time

def test_format_1(ser, motor_id):
    """Original working format from instant_test.py"""
    packet = bytearray([0xAA, 0x55, 0x01, 0x08])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    return ser.read(100)

def test_format_2(ser, motor_id):
    """L91 AT format"""
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(0x00)  # Type
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(motor_id)
    packet.extend([0x01, 0x00])
    packet.extend([0x0d, 0x0a])  # \r\n
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    return ser.read(100)

def test_format_3(ser, motor_id):
    """Extended CAN format"""
    # ExtId = 0x03 << 24 | 0xFD << 8 | motor_id
    ext_id = (0x03 << 24) | (0xFD << 8) | motor_id
    
    packet = bytearray([0xAA, 0x55])
    packet.extend(struct.pack('<I', ext_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    return ser.read(100)

def test_format_4(ser, motor_id):
    """Simplified format - just command and ID"""
    packet = bytearray([0xAA, 0x55, 0x01])
    packet.append(motor_id)
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    return ser.read(100)

def test_format_5(ser, motor_id):
    """MIT protocol format"""
    packet = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    return ser.read(100)

def test_broadcast(ser):
    """Broadcast to all motors"""
    print("\n" + "="*70)
    print("BROADCAST TESTS")
    print("="*70)
    
    # Test 1: Broadcast enable
    print("\n1. Broadcast enable (ID 0x00)...")
    packet = bytearray([0xAA, 0x55, 0x01, 0x08])
    packet.extend(struct.pack('<I', 0x00))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    response = ser.read(200)
    
    if response:
        print(f"   ✓ Response: {len(response)} bytes")
        print(f"     {response.hex(' ')}")
    else:
        print(f"   ✗ No response")
    
    # Test 2: Broadcast 0xFF
    print("\n2. Broadcast enable (ID 0xFF)...")
    packet = bytearray([0xAA, 0x55, 0x01, 0x08])
    packet.extend(struct.pack('<I', 0xFF))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    response = ser.read(200)
    
    if response:
        print(f"   ✓ Response: {len(response)} bytes")
        print(f"     {response.hex(' ')}")
    else:
        print(f"   ✗ No response")
    
    # Test 3: MIT broadcast
    print("\n3. MIT protocol broadcast...")
    packet = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)
    response = ser.read(200)
    
    if response:
        print(f"   ✓ Response: {len(response)} bytes")
        print(f"     {response.hex(' ')}")
    else:
        print(f"   ✗ No response")

def test_long_timeout(ser, motor_id):
    """Test with longer timeout"""
    packet = bytearray([0xAA, 0x55, 0x01, 0x08])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    checksum = sum(packet[2:]) & 0xFF
    packet.append(checksum)
    
    ser.write(packet)
    ser.flush()
    time.sleep(1.0)  # Longer wait
    return ser.read(200)

print("="*70)
print("PROTOCOL VARIATION TESTS")
print("="*70)
print("\nHardware confirmed:")
print("  ✓ Motors powered")
print("  ✓ 120Ω termination on both ends")
print("\nTesting different protocol formats...")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n[OK] Connected to {port} at {baud} baud\n")
    
    test_ids = [8, 20, 31, 32, 64, 72]
    
    # Test broadcast first
    test_broadcast(ser)
    
    # Test each format
    formats = [
        ("Format 1: Original (0xAA 0x55)", test_format_1),
        ("Format 2: L91 AT", test_format_2),
        ("Format 3: Extended CAN", test_format_3),
        ("Format 4: Simplified", test_format_4),
        ("Format 5: MIT Protocol", test_format_5),
        ("Format 6: Long Timeout", test_long_timeout),
    ]
    
    for format_name, test_func in formats:
        print("\n" + "="*70)
        print(format_name)
        print("="*70)
        
        found_any = False
        
        for motor_id in test_ids:
            print(f"\nTesting motor {motor_id}...", end=" ")
            
            try:
                response = test_func(ser, motor_id)
                
                if response and len(response) > 4:
                    print(f"✓ RESPONSE!")
                    print(f"  {len(response)} bytes: {response.hex(' ')}")
                    found_any = True
                else:
                    print("✗")
            except Exception as e:
                print(f"Error: {e}")
        
        if found_any:
            print(f"\n✅ {format_name} WORKS!")
            break
    
    # Try continuous sending
    print("\n" + "="*70)
    print("CONTINUOUS TEST (5 seconds)")
    print("="*70)
    print("Sending commands continuously...")
    
    start_time = time.time()
    count = 0
    
    while time.time() - start_time < 5:
        for motor_id in [8, 32, 64]:
            packet = bytearray([0xAA, 0x55, 0x01, 0x08])
            packet.extend(struct.pack('<I', motor_id))
            packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            checksum = sum(packet[2:]) & 0xFF
            packet.append(checksum)
            
            ser.write(packet)
            ser.flush()
            count += 1
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"\n✓ RESPONSE after {count} attempts!")
                print(f"  Motor {motor_id}: {len(response)} bytes")
                print(f"  {response.hex(' ')}")
                ser.close()
                exit(0)
            
            time.sleep(0.05)
    
    print(f"\n✗ No response after {count} attempts")
    
    ser.close()
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("\n❌ No motors responding with any protocol format")
    print("\nSince hardware is confirmed good:")
    print("  ✓ Motors powered")
    print("  ✓ Termination installed")
    print("\nPossible remaining issues:")
    print("  1. Wrong CAN bus wiring (H/L swapped?)")
    print("  2. Motors in different protocol mode")
    print("  3. Motors need reset/power cycle")
    print("  4. USB-to-CAN adapter not compatible")
    print("  5. Motors configured for different baud rate")
    print("\nTry:")
    print("  1. Swap CAN-H and CAN-L wires")
    print("  2. Power cycle motors completely (off 30 seconds)")
    print("  3. Check motor LED patterns for error codes")
    print("  4. Try different USB-to-CAN adapter")
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

