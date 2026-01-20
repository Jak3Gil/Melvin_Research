#!/usr/bin/env python3
"""
Test Motor 6 on /dev/ttyUSB0 and Motor 8 on /dev/ttyUSB1
Using exact COM6 sequence
"""

import subprocess
import sys

REMOTE_SCRIPT = '''#!/usr/bin/env python3
import serial
import time
import sys

def send_and_get_response(ser, cmd, timeout=0.5):
    """Send command and get response - EXACT from move_motor8_slow.py"""
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

def test_motor(port, motor_id, cmd_hex, motor_name):
    """Test a motor on a specific port"""
    print(f"\\n{'='*70}")
    print(f"Testing {motor_name} on {port}")
    print(f"{'='*70}")
    
    try:
        ser = serial.Serial(port, 921600, timeout=2.0)
        time.sleep(0.5)
        
        print(f"Initializing USB-CAN adapter on {port}...")
        ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
        time.sleep(0.5)
        resp1 = ser.read(500)
        print(f"  AT+AT response: {len(resp1)} bytes")
        
        ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
        time.sleep(0.5)
        resp2 = ser.read(500)
        print(f"  AT+A0 response: {len(resp2)} bytes")
        print("  [OK] Adapter initialized")
        print()
        
        # Activate motor
        print(f"Activating {motor_name} (CAN ID {motor_id})...")
        cmd = bytes.fromhex(cmd_hex)
        print(f"  Command: {cmd_hex}")
        resp = send_and_get_response(ser, cmd, timeout=1.0)
        if resp:
            print(f"  [RESPONSE] {resp}")
            print(f"  [SUCCESS] {motor_name} responded!")
            ser.close()
            return True
        else:
            print("  [NO RESPONSE]")
            print("  Trying longer timeout...")
            resp = send_and_get_response(ser, cmd, timeout=2.0)
            if resp:
                print(f"  [RESPONSE] {resp}")
                print(f"  [SUCCESS] {motor_name} responded!")
                ser.close()
                return True
            else:
                print("  [STILL NO RESPONSE]")
                ser.close()
                return False
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

print("="*70)
print("TEST MOTOR 6 (USB0) and MOTOR 8 (USB1)")
print("="*70)

# Motor 6 on /dev/ttyUSB0
# Motor 6: 41542007e8340800c40000000000000d0a (extended format, byte 0x34)
m6_success = test_motor(
    '/dev/ttyUSB0',
    6,
    '41542007e8340800c40000000000000d0a',
    'Motor 6'
)

# Motor 8 on /dev/ttyUSB1
# Motor 8: 41542007e8440800c40000000000000d0a (extended format, byte 0x44)
m8_success = test_motor(
    '/dev/ttyUSB1',
    8,
    '41542007e8440800c40000000000000d0a',
    'Motor 8'
)

print()
print("="*70)
print("SUMMARY")
print("="*70)
print(f"Motor 6 on /dev/ttyUSB0: {'[OK]' if m6_success else '[FAIL]'}")
print(f"Motor 8 on /dev/ttyUSB1: {'[OK]' if m8_success else '[FAIL]'}")
print("="*70)
'''

def run_on_jetson(hostname="192.168.55.1", username="melvin", port=22):
    """Run script on Jetson via SSH"""
    print("="*70)
    print("TEST MOTOR 6 (USB0) and MOTOR 8 (USB1) - Remote")
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
    print("Executing test script on Jetson...")
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
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("[ERROR] Command timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to execute: {e}")
        return False

if __name__ == "__main__":
    success = run_on_jetson()
    sys.exit(0 if success else 1)

