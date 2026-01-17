#!/usr/bin/env python3
"""
Quick hardware check - what happened?
"""

import serial
import time
import struct

print("="*70)
print("QUICK HARDWARE CHECK")
print("="*70)

port = '/dev/ttyUSB0'

try:
    # Test serial port
    print("\n1. Testing serial port...")
    ser = serial.Serial(port, 921600, timeout=1.0)
    print(f"   ✅ Serial port {port} opened successfully")
    time.sleep(0.5)
    
    # Test the working L91 AT protocol from earlier
    print("\n2. Testing L91 AT protocol (worked earlier)...")
    test_ids = [8, 16, 20, 24, 31, 32, 64, 72]
    
    for motor_id in test_ids:
        packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id])
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.extend([0x0d, 0x0a])
        
        ser.write(packet)
        ser.flush()
        time.sleep(0.2)
        
        response = ser.read(200)
        
        if response and len(response) > 4:
            print(f"   ✅ Motor ID {motor_id} responds!")
        else:
            print(f"   ✗ Motor ID {motor_id} no response")
    
    # Test L91 Checksum protocol (from instant_test.py)
    print("\n3. Testing L91 Checksum protocol (from instant_test.py)...")
    
    for motor_id in test_ids:
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        ser.flush()
        time.sleep(0.2)
        
        response = ser.read(200)
        
        if response and len(response) > 4:
            print(f"   ✅ Motor ID {motor_id} responds!")
        else:
            print(f"   ✗ Motor ID {motor_id} no response")
    
    # Listen for any CAN bus activity
    print("\n4. Listening for any CAN bus activity (5 seconds)...")
    
    ser.reset_input_buffer()
    start_time = time.time()
    activity = []
    
    while time.time() - start_time < 5:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            activity.append((time.time() - start_time, data))
            print(f"   [{time.time()-start_time:.2f}s] {len(data)} bytes: {data.hex(' ')}")
        time.sleep(0.1)
    
    if not activity:
        print("   ✗ No CAN bus activity detected")
    
    # Check USB device
    print("\n5. Checking USB-to-CAN adapter...")
    import subprocess
    result = subprocess.run(['ls', '-la', '/dev/ttyUSB*'], 
                          capture_output=True, text=True)
    print(f"   {result.stdout}")
    
    ser.close()
    
    print("\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)
    print("\n⚠️  Motors that were responding earlier are now silent!")
    print("\nPossible causes:")
    print("  1. Power was disconnected/lost")
    print("  2. CAN bus termination resistor disconnected")
    print("  3. USB-to-CAN adapter reset/changed mode")
    print("  4. Motors went into error/protection mode")
    print("  5. Wiring came loose")
    
    print("\nImmediate actions:")
    print("  1. Check power LEDs on all motors")
    print("  2. Check CAN H/L connections")
    print("  3. Check 120Ω termination resistors")
    print("  4. Power cycle everything")
    print("  5. Re-run instant_test.py to verify")
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

