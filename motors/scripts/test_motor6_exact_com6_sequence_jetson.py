#!/usr/bin/env python3
"""
Test Motor 6 on Jetson using EXACT sequence from working COM6 script
Replicates move_motor8_slow.py initialization and response reading
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

port = '/dev/ttyUSB0'
print("="*70)
print("Test Motor 6 - EXACT COM6 Sequence")
print("="*70)
print()

try:
    # EXACT baud rate from COM6 script
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing USB-CAN adapter (EXACT COM6 sequence)...")
    ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
    time.sleep(0.5)
    resp1 = ser.read(500)
    print(f"  AT+AT response: {len(resp1)} bytes")
    if resp1:
        print(f"  Response hex: {resp1.hex()[:60]}...")
    
    ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
    time.sleep(0.5)
    resp2 = ser.read(500)
    print(f"  AT+A0 response: {len(resp2)} bytes")
    if resp2:
        print(f"  Response hex: {resp2.hex()[:60]}...")
    print("  [OK]")
    print()
    
    # Motor 6 - Activate with extended format (same as Motor 8 but byte 0x34)
    print("Activating Motor 6 (extended format, byte 0x34)...")
    cmd_6_act = bytes.fromhex("41542007e8340800c40000000000000d0a")
    print(f"  Command: {cmd_6_act.hex()}")
    resp = send_and_get_response(ser, cmd_6_act, timeout=1.0)
    if resp:
        print(f"  [RESPONSE] {resp}")
        print(f"  [SUCCESS] Motor 6 responded!")
    else:
        print("  [NO RESPONSE]")
        print("  Trying longer timeout...")
        resp = send_and_get_response(ser, cmd_6_act, timeout=2.0)
        if resp:
            print(f"  [RESPONSE] {resp}")
        else:
            print("  [STILL NO RESPONSE]")
    time.sleep(0.5)
    
    ser.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
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
    print("TEST MOTOR 6 - EXACT COM6 SEQUENCE (Remote)")
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

