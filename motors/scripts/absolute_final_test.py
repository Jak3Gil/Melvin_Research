#!/usr/bin/env python3
"""Absolute final test - prove motors are/aren't connected"""
import serial, time

print("ABSOLUTE FINAL TEST")
print("="*70)

try:
    s = serial.Serial('/dev/ttyUSB0', 921600, timeout=1)
    print("✅ Serial port open")
    
    # Send AT command to motor 8
    s.write(b'\x41\x54\x00\x07\xe8\x08\x01\x00\x00\x00\x00\x00\x00\x00\x0d\x0a')
    print("✅ Sent 16 bytes (L91 AT enable motor 8)")
    
    time.sleep(0.5)
    
    r = s.read(100)
    
    if r:
        print(f"✅ RESPONSE! {len(r)} bytes: {r.hex()}")
        print("\n🎉 MOTORS ARE CONNECTED AND RESPONDING!")
    else:
        print("❌ NO RESPONSE")
        print("\nThis means:")
        print("  1. Motors NOT connected to /dev/ttyUSB0")
        print("  2. OR motors have no power")
        print("  3. OR motors on different device")
        print("\nAre motors connected to a DIFFERENT computer?")
    
    s.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

