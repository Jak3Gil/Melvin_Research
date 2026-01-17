#!/usr/bin/env python3
"""Test if motors are actually moving physically"""
import serial
import time

PORT = '/dev/ttyUSB1'
BAUD = 921600

print("="*70)
print("  MOTOR MOVEMENT TEST")
print("="*70)
print()
print("This will test motor 21 with STRONG, VISIBLE movement")
print("Watch your robot carefully!")
print()
input("Press Enter to start the test...")
print()

ser = serial.Serial(PORT, BAUD, timeout=0.5)

# Test motor 21
motor_id = 21

print(f"Testing Motor {motor_id}...")
print()

# Activate
print("1. Activating motor...")
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.3)

# Load params
print("2. Loading parameters...")
cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
             0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.3)

# Move with STRONG speed
print("3. MOVING MOTOR NOW (3 seconds)...")
print("   >>> WATCH THE MOTOR! <<<")
speed = 0.2  # Higher speed for visibility
speed_val = int(0x8000 + (speed * 3283.0))
cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, motor_id, 0x08, 0x05, 0x70,
                 0x00, 0x00, 0x07, 0x01])
cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
ser.write(bytes(cmd))

time.sleep(3.0)

# Stop
print("4. Stopping motor...")
speed_val = 0x7fff
cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, motor_id, 0x08, 0x05, 0x70,
                 0x00, 0x00, 0x07, 0x00])
cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
ser.write(bytes(cmd))
time.sleep(0.3)

# Deactivate
print("5. Deactivating motor...")
cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x00, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.2)

ser.close()

print()
print("="*70)
print("Test complete!")
print("="*70)
print()
print("Did you see motor 21 move?")
print()
print("If NO movement:")
print("  1. Check if motors are powered on")
print("  2. Check motor enable switches/buttons")
print("  3. Check if motor brakes are engaged")
print("  4. Verify CAN bus connections")
print("  5. Try testing different motor IDs (8, 16, 31, 72)")
print()

