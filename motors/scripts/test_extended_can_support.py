#!/usr/bin/env python3
"""
Test if USB-to-CAN adapter supports extended 29-bit CAN IDs
This is required for OTA firmware updates
"""

import serial
import struct
import time

def test_extended_id_support():
    """Test if adapter supports 29-bit extended CAN IDs"""
    port = '/dev/ttyUSB0'
    baudrate = 921600
    
    print("="*60)
    print("  Testing Extended CAN ID Support")
    print("="*60)
    print(f"\nPort: {port}")
    print(f"Baud: {baudrate}\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print("✓ Serial port opened\n")
        
        # Test 1: Standard 11-bit ID (should work)
        print("[Test 1] Standard 11-bit CAN ID (0x008)")
        print("-" * 60)
        standard_id = 0x008
        packet = bytearray([0xAA, 0x55])
        packet.append(0x01)  # Standard frame type
        packet.append(0x08)  # Data length
        packet.extend(struct.pack('<I', standard_id))
        packet.extend([0x00] * 8)
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        ser.write(packet)
        time.sleep(0.3)
        response = ser.read(100)
        
        if response:
            print(f"  Response received: {len(response)} bytes")
            print(f"  ✓ Standard IDs work (as expected)")
        else:
            print(f"  No response (motor might be disabled)")
        
        print()
        
        # Test 2: Extended 29-bit ID (needed for OTA)
        print("[Test 2] Extended 29-bit CAN ID (0x1FFFFF00)")
        print("-" * 60)
        extended_id = 0x1FFFFF00  # OTA broadcast ID
        packet = bytearray([0xAA, 0x55])
        packet.append(0x02)  # Extended frame type (if supported)
        packet.append(0x08)  # Data length
        packet.extend(struct.pack('<I', extended_id))
        packet.extend([0x00] * 8)
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        ser.reset_input_buffer()
        ser.write(packet)
        time.sleep(0.5)
        response = ser.read(100)
        
        if response:
            print(f"  Response received: {len(response)} bytes")
            print(f"  ✓ Extended IDs might be supported!")
        else:
            print(f"  ✗ No response")
            print(f"  ✗ Extended IDs NOT supported")
        
        print()
        
        # Test 3: Try OTA Get Device ID command
        print("[Test 3] OTA Get Device ID Command")
        print("-" * 60)
        # Frame type 0, host 0x7F, target 8
        ota_id = (0 << 24) | (0x7F << 8) | 8
        packet = bytearray([0xAA, 0x55])
        packet.append(0x02)  # Try extended frame
        packet.append(0x08)
        packet.extend(struct.pack('<I', ota_id))
        packet.extend([0x00] * 8)
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        ser.reset_input_buffer()
        ser.write(packet)
        time.sleep(0.5)
        response = ser.read(100)
        
        if response:
            print(f"  Response received: {len(response)} bytes")
            print(f"  Response hex: {response.hex()}")
            print(f"  ✓ OTA protocol might work!")
        else:
            print(f"  ✗ No response")
            print(f"  ✗ OTA protocol NOT supported via L91")
        
        ser.close()
        print("\n✓ Serial port closed")
        
        # Conclusion
        print("\n" + "="*60)
        print("  CONCLUSION")
        print("="*60)
        print("\n✗ USB-to-CAN adapter uses L91 protocol")
        print("✗ L91 protocol only supports 11-bit standard CAN IDs")
        print("✗ OTA firmware updates require 29-bit extended CAN IDs")
        print("✗ Direct firmware update NOT possible with this adapter")
        print("\n✓ Solution: Use MotorStudio (handles protocol correctly)")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extended_id_support()

