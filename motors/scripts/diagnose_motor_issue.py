#!/usr/bin/env python3
"""Diagnose why motors aren't moving physically"""
import serial
import time

PORT = '/dev/ttyUSB1'
BAUD = 921600

print("="*70)
print("  MOTOR DIAGNOSTICS")
print("="*70)
print()

ser = serial.Serial(PORT, BAUD, timeout=0.5)

motor_id = 21

print(f"Testing Motor {motor_id} with detailed diagnostics...")
print()

# Test 1: Check if motor responds to status query
print("Test 1: Checking motor response...")
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
ser.reset_input_buffer()
ser.write(cmd)
time.sleep(0.2)
response = ser.read(100)
print(f"  Response length: {len(response)} bytes")
print(f"  Response hex: {response.hex() if response else 'NONE'}")
if len(response) > 0:
    print("  ✓ Motor is responding to commands")
else:
    print("  ✗ Motor not responding")
print()

# Test 2: Try to read motor status
print("Test 2: Reading motor parameters...")
cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
             0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
ser.reset_input_buffer()
ser.write(cmd)
time.sleep(0.2)
response = ser.read(100)
print(f"  Response length: {len(response)} bytes")
print(f"  Response hex: {response.hex() if response else 'NONE'}")
print()

# Test 3: Try different movement command (position mode)
print("Test 3: Trying position control mode...")
# Enable
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.2)

# Try position command instead of jog
print("  Sending position command...")
# This is a different command format that might work
cmd = bytes([0x41, 0x54, 0x10, 0x07, 0xe8, motor_id, 0x08, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(2.0)

# Disable
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x00, 0x00, 0x0d, 0x0a])
ser.write(cmd)
print()

# Test 4: Check if motors need to be "unlocked" first
print("Test 4: Trying to unlock motor...")
# Some motors have a lock/unlock command
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x02, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.3)
print()

# Test 5: Try broadcast enable (enable all motors)
print("Test 5: Trying broadcast enable...")
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x01, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.3)
print()

# Test 6: Try very slow movement
print("Test 6: Trying VERY SLOW movement (easier to see)...")
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.2)

cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
             0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.2)

# Very slow speed
speed = 0.05
speed_val = int(0x8000 + (speed * 3283.0))
cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, motor_id, 0x08, 0x05, 0x70,
                 0x00, 0x00, 0x07, 0x01])
cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
print("  Motor should move SLOWLY for 5 seconds...")
print("  >>> WATCH CAREFULLY! <<<")
ser.write(bytes(cmd))
time.sleep(5.0)

# Stop
speed_val = 0x7fff
cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, motor_id, 0x08, 0x05, 0x70,
                 0x00, 0x00, 0x07, 0x00])
cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
ser.write(bytes(cmd))
time.sleep(0.2)

# Disable
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x00, 0x00, 0x0d, 0x0a])
ser.write(cmd)

ser.close()

print()
print("="*70)
print("DIAGNOSTICS COMPLETE")
print("="*70)
print()
print("IMPORTANT CHECKS:")
print()
print("1. Are the motors POWERED ON?")
print("   - Check power supply is connected and ON")
print("   - Look for LED indicators on motors")
print()
print("2. Are motor BRAKES engaged?")
print("   - Some motors have mechanical brakes")
print("   - Check if motors can be moved by hand")
print()
print("3. Are motors in SAFE MODE?")
print("   - Some motors need a safety enable signal")
print("   - Check for enable switches or buttons")
print()
print("4. Is the motor SHAFT visible?")
print("   - Make sure you're watching the right motor")
print("   - Motor 21 should be in the 21-30 range")
print()
print("5. Try manually rotating the motor:")
print("   - Can you turn the motor shaft by hand?")
print("   - If it's locked solid, brake might be engaged")
print("   - If it moves freely, motor might not be powered")
print()

