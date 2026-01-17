#!/usr/bin/env python3
"""
Test EVERY L91 protocol variation
Motors are probably in a unique mode - find the right format!
"""

import serial
import time
import struct

def test_variation(ser, variation_name, packet, motor_id=8):
    """Test a specific protocol variation"""
    ser.reset_input_buffer()
    ser.write(packet)
    ser.flush()
    time.sleep(0.15)
    
    if ser.in_waiting > 0:
        resp = ser.read(ser.in_waiting)
        print(f"  ✅ {variation_name} WORKS!")
        print(f"     Sent: {packet.hex(' ')}")
        print(f"     Response: {resp.hex(' ')}")
        return True
    return False

print("="*70)
print("L91 PROTOCOL - ALL VARIATIONS TEST")
print("="*70)
print("\nTesting EVERY possible L91 command format")
print("Motors might be in a unique mode - we'll find it!")
print("="*70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    ser = serial.Serial(port, baud, timeout=1.0)
    time.sleep(0.5)
    print(f"\n✅ Connected to {port} at {baud} baud\n")
    
    motor_id = 8
    working_formats = []
    
    # VARIATION 1: Original L91 AT format
    print("="*70)
    print("VARIATION 1: L91 AT Protocol (Original)")
    print("="*70)
    
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(0x00)  # Command: Enable
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(motor_id)
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.extend([0x0d, 0x0a])  # \r\n
    
    if test_variation(ser, "L91 AT Original", packet, motor_id):
        working_formats.append("L91 AT Original")
    else:
        print(f"  ✗ No response")
    
    # VARIATION 2: L91 AT without \r\n
    print("\n" + "="*70)
    print("VARIATION 2: L91 AT Without \\r\\n")
    print("="*70)
    
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id])
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    if test_variation(ser, "L91 AT No CRLF", packet, motor_id):
        working_formats.append("L91 AT No CRLF")
    else:
        print(f"  ✗ No response")
    
    # VARIATION 3: L91 Checksum (0xAA 0x55)
    print("\n" + "="*70)
    print("VARIATION 3: L91 Checksum Protocol")
    print("="*70)
    
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    
    if test_variation(ser, "L91 Checksum", packet, motor_id):
        working_formats.append("L91 Checksum")
    else:
        print(f"  ✗ No response")
    
    # VARIATION 4: L91 with different command byte positions
    print("\n" + "="*70)
    print("VARIATION 4: L91 AT - Different Command Positions")
    print("="*70)
    
    variations = [
        (bytearray([0x41, 0x54, motor_id, 0x00, 0x07, 0xe8, 0x01, 0x00, 0x0d, 0x0a]), "ID first"),
        (bytearray([0x41, 0x54, 0x07, 0xe8, motor_id, 0x00, 0x01, 0x00, 0x0d, 0x0a]), "Short format"),
        (bytearray([0x41, 0x54, 0x00, motor_id, 0x01, 0x00, 0x0d, 0x0a]), "Minimal format"),
    ]
    
    for pkt, desc in variations:
        if test_variation(ser, f"L91 AT {desc}", pkt, motor_id):
            working_formats.append(f"L91 AT {desc}")
        else:
            print(f"  ✗ {desc} - No response")
    
    # VARIATION 5: Different header bytes
    print("\n" + "="*70)
    print("VARIATION 5: Different Header Bytes")
    print("="*70)
    
    headers = [
        ([0xAA, 0x55], "0xAA 0x55"),
        ([0x55, 0xAA], "0x55 0xAA"),
        ([0x41, 0x54], "0x41 0x54 (AT)"),
        ([0xFF, 0xFE], "0xFF 0xFE"),
        ([0xFE, 0xFF], "0xFE 0xFF"),
        ([0x5A, 0xA5], "0x5A 0xA5"),
    ]
    
    for header, desc in headers:
        packet = bytearray(header)
        packet.extend([0x01, motor_id, 0x01, 0x00, 0x00, 0x00])
        
        if test_variation(ser, f"Header {desc}", packet, motor_id):
            working_formats.append(f"Header {desc}")
        else:
            print(f"  ✗ {desc} - No response")
    
    # VARIATION 6: MIT Protocol variants
    print("\n" + "="*70)
    print("VARIATION 6: MIT Protocol Variants")
    print("="*70)
    
    mit_variants = [
        (bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC]), "MIT Enable"),
        (bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD]), "MIT Exit"),
        (bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]), "MIT Zero"),
    ]
    
    for data, desc in mit_variants:
        packet = bytearray([0x55, 0xAA])
        packet.extend(struct.pack('<H', motor_id))
        packet.extend(data)
        
        if test_variation(ser, f"MIT {desc}", packet, motor_id):
            working_formats.append(f"MIT {desc}")
        else:
            print(f"  ✗ {desc} - No response")
    
    # VARIATION 7: Raw CAN format
    print("\n" + "="*70)
    print("VARIATION 7: Raw CAN Packet Format")
    print("="*70)
    
    # Standard CAN frame format
    packet = bytearray([0x00, 0x00])  # CAN ID high/low
    packet.extend([motor_id, 0x00])  # Extended ID
    packet.append(0x08)  # DLC (data length)
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # Data
    
    if test_variation(ser, "Raw CAN Standard", packet, motor_id):
        working_formats.append("Raw CAN Standard")
    else:
        print(f"  ✗ No response")
    
    # VARIATION 8: Try ALL command bytes with AT protocol
    print("\n" + "="*70)
    print("VARIATION 8: Scan All Command Bytes (0x00-0xFF)")
    print("="*70)
    print("Testing which command byte gets a response...")
    
    for cmd_byte in range(0, 256):
        if cmd_byte % 64 == 0:
            print(f"  Testing commands 0x{cmd_byte:02X}-0x{min(cmd_byte+63, 255):02X}...", end='', flush=True)
        
        packet = bytearray([0x41, 0x54, cmd_byte, 0x07, 0xe8, motor_id])
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.extend([0x0d, 0x0a])
        
        ser.reset_input_buffer()
        ser.write(packet)
        ser.flush()
        time.sleep(0.02)
        
        if ser.in_waiting > 0:
            resp = ser.read(ser.in_waiting)
            print(f"\n  ✅ Command 0x{cmd_byte:02X} WORKS!")
            print(f"     Response: {resp.hex(' ')}")
            working_formats.append(f"AT Command 0x{cmd_byte:02X}")
        elif cmd_byte % 64 == 63:
            print(" -")
    
    # VARIATION 9: Try different motor IDs
    print("\n" + "="*70)
    print("VARIATION 9: Quick Scan Multiple Motor IDs")
    print("="*70)
    print("Maybe motor 8 isn't responding, try others...")
    
    test_ids = [1, 2, 3, 4, 5, 6, 7, 8, 10, 16, 20, 24, 31, 32, 64, 72, 100, 120, 127]
    
    for test_id in test_ids:
        # Try AT protocol
        packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, test_id])
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.extend([0x0d, 0x0a])
        
        ser.reset_input_buffer()
        ser.write(packet)
        ser.flush()
        time.sleep(0.05)
        
        if ser.in_waiting > 0:
            resp = ser.read(ser.in_waiting)
            print(f"  ✅ Motor ID {test_id} responds!")
            print(f"     Response: {resp.hex(' ')}")
            working_formats.append(f"Motor ID {test_id}")
    
    if not any("Motor ID" in fmt for fmt in working_formats):
        print(f"  ✗ No motors responded to any ID")
    
    # VARIATION 10: Listen for spontaneous traffic
    print("\n" + "="*70)
    print("VARIATION 10: Listen for Spontaneous CAN Traffic")
    print("="*70)
    print("Maybe motors are broadcasting status...")
    
    ser.reset_input_buffer()
    print("Listening for 5 seconds...")
    
    start_time = time.time()
    packets_received = []
    
    while time.time() - start_time < 5:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            packets_received.append((time.time() - start_time, data))
            print(f"  [{time.time()-start_time:.2f}s] {len(data)} bytes: {data.hex(' ')}")
        time.sleep(0.05)
    
    if packets_received:
        print(f"\n  ✅ Received {len(packets_received)} spontaneous packets!")
        working_formats.append("Spontaneous traffic detected")
    else:
        print(f"  ✗ No spontaneous traffic")
    
    ser.close()
    
    # FINAL RESULTS
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    if working_formats:
        print(f"\n🎉 SUCCESS! Found {len(working_formats)} working format(s):")
        for i, fmt in enumerate(working_formats, 1):
            print(f"  {i}. {fmt}")
        
        print(f"\n✅ Motors ARE responding - not a hardware problem!")
        print(f"   Now we can scan for all 15 motors using the working format")
    else:
        print(f"\n❌ NO WORKING FORMAT FOUND")
        print(f"\nThis could mean:")
        print(f"  1. Motors are in a completely different protocol mode")
        print(f"  2. Motors need a specific initialization sequence first")
        print(f"  3. USB-to-CAN adapter needs configuration")
        print(f"  4. Actually IS a hardware problem (power/wiring)")
        
        print(f"\n🔧 NEXT STEPS:")
        print(f"  1. Check if motors have status LEDs - are they blinking?")
        print(f"  2. Try RobStride Motor Studio software first")
        print(f"  3. Check motor documentation for protocol mode")
        print(f"  4. Verify CAN bus termination (120Ω resistors)")
    
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

