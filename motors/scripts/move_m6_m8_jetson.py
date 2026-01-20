#!/usr/bin/env python3
"""
Move Motor 6 (USB0) and Motor 8 (USB1) on Jetson
Using exact protocol from move_motor8_slow.py
"""

import subprocess
import sys

REMOTE_SCRIPT = '''#!/usr/bin/env python3
import serial
import time
import sys
import threading

def send_and_get_response(ser, cmd, timeout=0.5):
    """Send command and get response"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.03)
    
    return response.hex() if len(response) > 0 else None

def move_motor_jog_extended(ser, byte_val, speed, flag=1):
    """Move motor using JOG command (extended format)"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    # Extended format JOG command
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, byte_val])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)

def stop_motor(ser, byte_val):
    """Stop motor"""
    move_motor_jog_extended(ser, byte_val, 0.0, 0)

print("="*70)
print("Move Motor 6 (USB0) and Motor 8 (USB1) - Jetson")
print("="*70)
print()
print("Motor 6: /dev/ttyUSB0 (byte 0x34)")
print("Motor 8: /dev/ttyUSB1 (byte 0x44)")
print()
print("WATCH BOTH MOTORS - They will move!")
print()
print("Starting in 3 seconds...")
time.sleep(3)
print()

try:
    # Open both serial ports
    ser_m6 = serial.Serial('/dev/ttyUSB0', 921600, timeout=2.0)
    ser_m8 = serial.Serial('/dev/ttyUSB1', 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing USB-CAN adapters...")
    
    # Initialize Motor 6 adapter
    print("  Initializing /dev/ttyUSB0 (Motor 6)...")
    ser_m6.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
    time.sleep(0.5)
    ser_m6.read(500)
    ser_m6.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
    time.sleep(0.5)
    ser_m6.read(500)
    print("    [OK]")
    
    # Initialize Motor 8 adapter
    print("  Initializing /dev/ttyUSB1 (Motor 8)...")
    ser_m8.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
    time.sleep(0.5)
    ser_m8.read(500)
    ser_m8.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
    time.sleep(0.5)
    ser_m8.read(500)
    print("    [OK]")
    print()
    
    # Activate both motors
    print("Activating motors...")
    
    print("  Activating Motor 6...")
    cmd_6_act = bytes.fromhex("41542007e8340800c40000000000000d0a")
    resp6 = send_and_get_response(ser_m6, cmd_6_act, timeout=1.0)
    if resp6:
        print(f"    [RESPONSE] {resp6[:60]}...")
    else:
        print("    [NO RESPONSE]")
    
    print("  Activating Motor 8...")
    cmd_8_act = bytes.fromhex("41542007e8440800c40000000000000d0a")
    resp8 = send_and_get_response(ser_m8, cmd_8_act, timeout=1.0)
    if resp8:
        print(f"    [RESPONSE] {resp8[:60]}...")
    else:
        print("    [NO RESPONSE]")
    
    time.sleep(0.5)
    print()
    
    speed = 0.05  # Slow speed
    
    # Move both motors forward simultaneously
    print(f"Moving BOTH motors FORWARD (speed={speed}) - WATCH BOTH MOTORS!")
    move_motor_jog_extended(ser_m6, 0x34, speed, 1)  # Motor 6
    move_motor_jog_extended(ser_m8, 0x44, speed, 1)  # Motor 8
    time.sleep(3.0)
    
    # Stop both
    print("Stopping both motors...")
    stop_motor(ser_m6, 0x34)
    stop_motor(ser_m8, 0x44)
    time.sleep(1.0)
    
    # Move both motors backward simultaneously
    print(f"Moving BOTH motors BACKWARD (speed={-speed}) - WATCH BOTH MOTORS!")
    move_motor_jog_extended(ser_m6, 0x34, -speed, 1)  # Motor 6
    move_motor_jog_extended(ser_m8, 0x44, -speed, 1)  # Motor 8
    time.sleep(3.0)
    
    # Final stop
    print("Final stop for both motors...")
    stop_motor(ser_m6, 0x34)
    stop_motor(ser_m8, 0x44)
    time.sleep(1.0)
    
    ser_m6.close()
    ser_m8.close()
    
    print()
    print("="*70)
    print("MOVEMENT TEST COMPLETE")
    print("="*70)
    print()
    print("Did both motors move?")
    print("  - Motor 6 on /dev/ttyUSB0")
    print("  - Motor 8 on /dev/ttyUSB1")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

def run_on_jetson(hostname="192.168.55.1", username="melvin", port=22):
    """Run script on Jetson via SSH"""
    print("="*70)
    print("MOVE MOTOR 6 (USB0) and MOTOR 8 (USB1) - Remote")
    print("="*70)
    print()
    print(f"Connecting to: {username}@{hostname}:{port}")
    print()
    
    # Test connectivity
    try:
        result = subprocess.run(
            ['ping', '-n', '2', hostname],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("Testing connectivity... [OK]")
        else:
            print("Testing connectivity... [WARNING] Ping failed - continuing anyway")
    except subprocess.TimeoutExpired:
        print("Testing connectivity... [WARNING] Command timed out - continuing anyway")
    except Exception as e:
        print(f"Testing connectivity... [WARNING] {e} - continuing anyway")
    
    print()
    print("Executing movement script on Jetson...")
    print()
    
    # Create SSH command
    ssh_cmd = [
        'ssh',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'ConnectTimeout=10',
        f'{username}@{hostname}',
        f'python3 - <<\'EOF\'\n{REMOTE_SCRIPT}\nEOF'
    ]
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("[ERROR] Command timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to execute: {e}")
        return False

if __name__ == "__main__":
    success = run_on_jetson()
    sys.exit(0 if success else 1)

