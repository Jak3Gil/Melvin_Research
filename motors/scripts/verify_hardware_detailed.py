#!/usr/bin/env python3
"""
Detailed hardware verification
Even though user says hardware works, we're getting NO CAN activity
"""

import serial
import time
import subprocess
import os

print("="*70)
print("DETAILED HARDWARE VERIFICATION")
print("="*70)

# Check 1: USB devices
print("\n1. USB-to-CAN Adapter Detection:")
print("-" * 70)
try:
    result = subprocess.run(['ls', '-la', '/dev/ttyUSB*'], 
                          capture_output=True, text=True, shell=False)
    if result.returncode == 0:
        print(result.stdout)
        print("✅ USB device found")
    else:
        print("❌ No /dev/ttyUSB* devices found!")
        print("   Check if USB-to-CAN adapter is connected")
except Exception as e:
    print(f"❌ Error checking USB: {e}")

# Check 2: dmesg for USB events
print("\n2. Recent USB Events (dmesg):")
print("-" * 70)
try:
    result = subprocess.run(['dmesg', '|', 'tail', '-30'], 
                          capture_output=True, text=True, shell=True)
    print(result.stdout[-1000:])  # Last 1000 chars
except Exception as e:
    print(f"Error: {e}")

# Check 3: Serial port permissions
print("\n3. Serial Port Permissions:")
print("-" * 70)
try:
    result = subprocess.run(['ls', '-l', '/dev/ttyUSB0'], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    result = subprocess.run(['groups'], capture_output=True, text=True)
    print(f"Current user groups: {result.stdout.strip()}")
    
    if 'dialout' in result.stdout:
        print("✅ User in dialout group")
    else:
        print("⚠️  User NOT in dialout group - may need: sudo usermod -a -G dialout $USER")
except Exception as e:
    print(f"Error: {e}")

# Check 4: Test serial port directly
print("\n4. Serial Port Direct Test:")
print("-" * 70)

port = '/dev/ttyUSB0'
baud = 921600

try:
    print(f"Opening {port} at {baud} baud...")
    ser = serial.Serial(port, baud, timeout=1.0)
    print(f"✅ Port opened successfully")
    
    print(f"\nPort settings:")
    print(f"  Baudrate: {ser.baudrate}")
    print(f"  Bytesize: {ser.bytesize}")
    print(f"  Parity: {ser.parity}")
    print(f"  Stopbits: {ser.stopbits}")
    print(f"  Timeout: {ser.timeout}")
    
    # Check if we can write
    print(f"\nTesting write capability...")
    test_data = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, 0x08, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    bytes_written = ser.write(test_data)
    ser.flush()
    print(f"✅ Wrote {bytes_written} bytes")
    
    # Check if we can read
    print(f"\nTesting read capability...")
    time.sleep(0.3)
    
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        print(f"✅ Read {len(data)} bytes: {data.hex(' ')}")
    else:
        print(f"⚠️  No data in buffer (motors not responding)")
    
    # Try loopback test if adapter supports it
    print(f"\n5. Loopback Test (if adapter supports):")
    print("-" * 70)
    
    # Some USB-CAN adapters echo back commands
    ser.reset_input_buffer()
    test_msg = bytearray([0xAA, 0x55, 0xAA, 0x55])
    ser.write(test_msg)
    ser.flush()
    time.sleep(0.1)
    
    if ser.in_waiting > 0:
        echo = ser.read(ser.in_waiting)
        if echo == test_msg:
            print(f"✅ Loopback working - adapter echoes commands")
        else:
            print(f"⚠️  Got data but not echo: {echo.hex(' ')}")
    else:
        print(f"✗ No loopback (normal for most adapters)")
    
    ser.close()
    
except serial.SerialException as e:
    print(f"❌ SERIAL ERROR: {e}")
    print(f"   This means the USB-to-CAN adapter has a problem!")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Check 6: Alternative USB ports
print(f"\n6. Checking for Alternative USB Ports:")
print("-" * 70)

try:
    result = subprocess.run(['ls', '/dev/tty*'], 
                          capture_output=True, text=True, shell=True)
    tty_devices = [line for line in result.stdout.split('\n') 
                   if 'USB' in line or 'ACM' in line]
    
    if tty_devices:
        print("Found USB serial devices:")
        for dev in tty_devices:
            print(f"  {dev}")
    else:
        print("No USB serial devices found")
        
except Exception as e:
    print(f"Error: {e}")

# Check 7: Power and wiring checklist
print(f"\n7. PHYSICAL HARDWARE CHECKLIST:")
print("="*70)

checklist = [
    ("Motor Power Supply", "Are all 15 motors powered? Check LEDs"),
    ("Power Supply Voltage", "Correct voltage for motors? (usually 24V-48V)"),
    ("CAN-H Connection", "Yellow/Orange wire connected at both ends?"),
    ("CAN-L Connection", "Green/Blue wire connected at both ends?"),
    ("Ground Connection", "Common ground between motors and adapter?"),
    ("Termination Resistor 1", "120Ω resistor at START of CAN bus?"),
    ("Termination Resistor 2", "120Ω resistor at END of CAN bus?"),
    ("USB-to-CAN Adapter Power", "Does adapter have power LED on?"),
    ("USB Cable", "USB cable properly connected to Jetson?"),
    ("Motor Daisy Chain", "All motors connected in series (daisy chain)?"),
]

for i, (item, question) in enumerate(checklist, 1):
    print(f"\n{i:2d}. {item}")
    print(f"    ❓ {question}")

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)

print("""
Based on the tests:

✅ IF serial port opens: USB-to-CAN adapter is connected
✅ IF we can write: Adapter accepts commands
❌ IF no responses: Either:
   1. Motors have no power
   2. CAN bus wiring is wrong/disconnected
   3. Termination resistors missing/wrong
   4. Motors are on different CAN bus
   5. Motors in error state requiring reset

CRITICAL: We see ZERO CAN bus activity!
This means:
  - Either motors aren't powered
  - Or CAN wiring is disconnected
  - Or termination is wrong

ACTION REQUIRED:
1. Check EVERY item in the physical checklist above
2. Use a multimeter to verify:
   - Motor power voltage
   - CAN-H voltage (should be ~3.5V idle)
   - CAN-L voltage (should be ~1.5V idle)
   - Resistance between CAN-H and CAN-L (should be ~60Ω with 120Ω terminators)
3. Power cycle EVERYTHING
4. Try connecting just ONE motor first

""")

