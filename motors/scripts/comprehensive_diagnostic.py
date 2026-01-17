#!/usr/bin/env python3
"""
Comprehensive diagnostic - test everything
"""

import serial
import struct
import time
import sys

def test_serial_port():
    """Test if serial port opens and can send data"""
    print("\n" + "="*60)
    print("  TEST 1: Serial Port")
    print("="*60)
    
    try:
        ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0.5)
        print("✓ /dev/ttyUSB0 opened at 921600 baud")
        
        # Send enable command to motor 8
        packet = bytearray([0xAA, 0x55, 0x01, 0x08])
        packet.extend(struct.pack('<I', 8))
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        print(f"  Sending: {packet.hex()}")
        ser.write(packet)
        ser.flush()
        time.sleep(0.3)
        
        response = ser.read(100)
        
        if response and len(response) > 0:
            print(f"✓ Response received: {response.hex()}")
            ser.close()
            return True
        else:
            print("✗ No response from motor")
            ser.close()
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_multiple_motors():
    """Try multiple motor IDs"""
    print("\n" + "="*60)
    print("  TEST 2: Multiple Motor IDs")
    print("="*60)
    
    motor_ids = [1, 2, 3, 8, 16, 21, 31, 64, 72]
    
    try:
        ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0.3)
        print("✓ Serial port opened")
        
        for motor_id in motor_ids:
            print(f"  Testing motor ID {motor_id}... ", end='', flush=True)
            
            packet = bytearray([0xAA, 0x55, 0x01, 0x08])
            packet.extend(struct.pack('<I', motor_id))
            packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            checksum = sum(packet[2:]) & 0xFF
            packet.append(checksum)
            
            ser.write(packet)
            ser.flush()
            time.sleep(0.2)
            
            response = ser.read(100)
            
            if response and len(response) > 0:
                print(f"✓ Response ({len(response)} bytes)")
                ser.close()
                return True
            else:
                print("✗")
        
        print("\n✗ No motor responded")
        ser.close()
        return False
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def test_raw_serial():
    """Test if serial port receives ANY data"""
    print("\n" + "="*60)
    print("  TEST 3: Raw Serial Monitoring")
    print("="*60)
    
    try:
        ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0.1)
        print("✓ Listening for ANY serial data (5 seconds)...")
        
        start_time = time.time()
        data_received = bytearray()
        
        while time.time() - start_time < 5.0:
            byte = ser.read(1)
            if byte:
                data_received.extend(byte)
                print(f"  Received: {byte.hex()}")
        
        ser.close()
        
        if len(data_received) > 0:
            print(f"✓ Received {len(data_received)} bytes total")
            return True
        else:
            print("✗ No data received")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("="*60)
    print("  Comprehensive Motor Diagnostic")
    print("="*60)
    print("\nThis will test:")
    print("  1. Serial port communication")
    print("  2. Multiple motor IDs")
    print("  3. Raw serial data reception")
    
    # Run tests
    test1 = test_serial_port()
    
    if test1:
        print("\n✅ MOTORS ARE WORKING!")
        print("   Serial communication successful at 921600 baud\n")
        return
    
    test2 = test_multiple_motors()
    
    if test2:
        print("\n✅ MOTORS ARE WORKING!")
        print("   Found working motor with different ID\n")
        return
    
    test3 = test_raw_serial()
    
    # Final summary
    print("\n" + "="*60)
    print("  DIAGNOSTIC SUMMARY")
    print("="*60)
    
    if not test1 and not test2 and not test3:
        print("\n❌ MOTORS NOT RESPONDING")
        print("\nPossible causes:")
        print("  1. Motors not powered on")
        print("  2. DIP switches in wrong position")
        print("  3. USB cable disconnected")
        print("  4. Controller needs reset")
        print("\nRecommendations:")
        print("  1. Check motor power LEDs")
        print("  2. Switch DIP switches back to original")
        print("  3. Unplug/replug USB cable")
        print("  4. Power cycle motors")
    
    print()

if __name__ == "__main__":
    main()

