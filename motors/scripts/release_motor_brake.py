#!/usr/bin/env python3
"""Try to release motor brakes and enable full power"""
import serial
import time

PORT = '/dev/ttyUSB1'
BAUD = 921600

print("="*70)
print("  MOTOR BRAKE RELEASE & POWER ENABLE")
print("="*70)
print()

ser = serial.Serial(PORT, BAUD, timeout=0.5)

motor_id = 21

print(f"Attempting to fully enable Motor {motor_id}...")
print()

# Try various enable/unlock commands
commands_to_try = [
    ("Brake Release (0x03)", bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x03, 0x00, 0x0d, 0x0a])),
    ("Power Enable (0x04)", bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x04, 0x00, 0x0d, 0x0a])),
    ("Unlock (0x05)", bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x05, 0x00, 0x0d, 0x0a])),
    ("Full Enable (0x01)", bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])),
]

for desc, cmd in commands_to_try:
    print(f"Trying: {desc}")
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.2)
    response = ser.read(100)
    print(f"  Response: {len(response)} bytes - {response.hex() if response else 'NONE'}")
    time.sleep(0.1)

print()
print("Now trying movement with all enables sent...")
print()

# Load params
cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
             0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
ser.write(cmd)
time.sleep(0.2)

# Try MAXIMUM speed
print("Sending MAXIMUM SPEED command...")
print(">>> WATCH MOTOR 21 NOW! <<<")
speed = 0.5  # Maximum safe speed
speed_val = int(0x8000 + (speed * 3283.0))
cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, motor_id, 0x08, 0x05, 0x70,
                 0x00, 0x00, 0x07, 0x01])
cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
ser.write(bytes(cmd))

print("Motor running at max speed for 3 seconds...")
time.sleep(3.0)

# Stop
speed_val = 0x7fff
cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, motor_id, 0x08, 0x05, 0x70,
                 0x00, 0x00, 0x07, 0x00])
cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
ser.write(bytes(cmd))

ser.close()

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)
print()
print("Did you see ANY movement?")
print()
print("If still NO movement, please check:")
print()
print("1. PHYSICAL POWER:")
print("   - Is there a main power switch? Is it ON?")
print("   - Are there LED indicators on the motors? Are they lit?")
print("   - Check power supply voltage")
print()
print("2. ENABLE SIGNAL:")
print("   - Some robots have a hardware enable line")
print("   - Check for an 'ENABLE' or 'MOTOR POWER' switch")
print("   - May need to press/hold an enable button")
print()
print("3. EMERGENCY STOP:")
print("   - Is there an E-STOP button? Is it released?")
print("   - E-stop might be cutting motor power")
print()
print("4. MOTOR CONFIGURATION:")
print("   - Motors might be in 'configuration mode' not 'run mode'")
print("   - May need to use RobStride Motor Studio to enable")
print()
print("5. TRY MANUALLY:")
print("   - Can you rotate the motor shaft by hand?")
print("   - If completely locked: brake is engaged")
print("   - If free-spinning: motor has no power")
print("   - If has resistance: motor is powered but not commanded")
print()

