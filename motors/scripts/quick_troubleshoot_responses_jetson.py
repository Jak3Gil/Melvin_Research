#!/usr/bin/env python3
"""
Quick troubleshoot why motors aren't responding
Focus on what worked before for Motor 6
"""

import subprocess
import sys

REMOTE_SCRIPT = '''#!/usr/bin/env python3
import serial
import time
import struct

def read_response(ser, timeout=2.0):
    """Read response with timeout"""
    response = bytearray()
    start = time.time()
    last_data = time.time()
    
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            response.extend(chunk)
            last_data = time.time()
        else:
            if len(response) > 0 and (time.time() - last_data) > 0.3:
                break
        time.sleep(0.05)
    
    return bytes(response)

print("="*70)
print("QUICK TROUBLESHOOT - Motor Responses")
print("="*70)
print()

# Test Motor 6 (worked earlier)
print("Testing Motor 6 on /dev/ttyUSB1...")
print()

try:
    ser6 = serial.Serial('/dev/ttyUSB1', 921600, timeout=2.0)
    time.sleep(0.5)
    
    # Initialize
    print("1. Initializing adapter...")
    ser6.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    resp1 = ser6.read(500)
    print(f"   AT+AT response: {len(resp1)} bytes")
    
    ser6.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    resp2 = ser6.read(500)
    print(f"   AT+A0 response: {len(resp2)} bytes")
    print()
    
    # Wait longer after init
    print("2. Waiting 2 seconds after initialization...")
    time.sleep(2.0)
    print()
    
    # Send activation command
    print("3. Sending Motor 6 activation command...")
    cmd6 = bytes.fromhex("41542007e8340800c40000000000000d0a")
    print(f"   Command: {cmd6.hex()}")
    
    ser6.reset_input_buffer()
    time.sleep(0.2)
    
    ser6.write(cmd6)
    ser6.flush()
    print("   Command sent")
    
    # Check response with multiple attempts
    print("4. Reading response...")
    for attempt in range(3):
        time.sleep(0.5)
        bytes_available = ser6.in_waiting
        print(f"   Attempt {attempt+1}: {bytes_available} bytes available")
        
        if bytes_available > 0:
            response = read_response(ser6, timeout=1.0)
            if response:
                print(f"   [RESPONSE] {len(response)} bytes: {response.hex()[:80]}...")
                ser6.close()
                print()
                print("   [SUCCESS] Motor 6 responded!")
                sys.exit(0)
    
    print("   [NO RESPONSE]")
    ser6.close()
    
except Exception as e:
    print(f"   [ERROR] {e}")

print()
print("Testing Motor 8 on /dev/ttyUSB0...")
print()

try:
    ser8 = serial.Serial('/dev/ttyUSB0', 921600, timeout=2.0)
    time.sleep(0.5)
    
    # Initialize
    print("1. Initializing adapter...")
    ser8.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    resp1 = ser8.read(500)
    print(f"   AT+AT response: {len(resp1)} bytes")
    
    ser8.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    resp2 = ser8.read(500)
    print(f"   AT+A0 response: {len(resp2)} bytes")
    print()
    
    # Wait longer after init
    print("2. Waiting 2 seconds after initialization...")
    time.sleep(2.0)
    print()
    
    # Send activation command
    print("3. Sending Motor 8 activation command...")
    cmd8 = bytes.fromhex("41542007e8440800c40000000000000d0a")
    print(f"   Command: {cmd8.hex()}")
    
    ser8.reset_input_buffer()
    time.sleep(0.2)
    
    ser8.write(cmd8)
    ser8.flush()
    print("   Command sent")
    
    # Check response
    print("4. Reading response...")
    for attempt in range(3):
        time.sleep(0.5)
        bytes_available = ser8.in_waiting
        print(f"   Attempt {attempt+1}: {bytes_available} bytes available")
        
        if bytes_available > 0:
            response = read_response(ser8, timeout=1.0)
            if response:
                print(f"   [RESPONSE] {len(response)} bytes: {response.hex()[:80]}...")
                ser8.close()
                print()
                print("   [SUCCESS] Motor 8 responded!")
                sys.exit(0)
    
    print("   [NO RESPONSE]")
    ser8.close()
    
except Exception as e:
    print(f"   [ERROR] {e}")

print()
print("="*70)
print("SUMMARY")
print("="*70)
print()
print("If no responses:")
print("  1. Check CAN bus termination (120 ohm at both ends)")
print("  2. Verify CAN_H and CAN_L connections")
print("  3. Check if motors need power cycle")
print("  4. Verify motors are on correct bus segments")
print("="*70)
'''

def run_remote_script(hostname="192.168.55.1", username="melvin", port=22):
    """Run the troubleshooting script on Jetson via SSH"""
    print("=" * 70)
    print("QUICK TROUBLESHOOT MOTOR RESPONSES (Remote)")
    print("=" * 70)
    print()
    print(f"Connecting to: {username}@{hostname}:{port}")
    print()
    
    # Test connectivity
    print("Testing connectivity...", end=" ", flush=True)
    try:
        if sys.platform == 'win32':
            result = subprocess.run(['ping', '-n', '2', hostname], 
                                  capture_output=True, timeout=5)
        else:
            result = subprocess.run(['ping', '-c', '2', hostname], 
                                  capture_output=True, timeout=5)
        if result.returncode == 0:
            print("[OK]")
        else:
            print("[WARNING] Cannot ping - continuing anyway")
    except Exception as e:
        print(f"[WARNING] {e} - continuing anyway")
    
    print()
    print("Running quick diagnostics...")
    print()
    
    # Run the script on Jetson via SSH
    ssh_cmd = ['ssh', '-p', str(port), f'{username}@{hostname}', 'python3']
    
    try:
        result = subprocess.run(
            ssh_cmd,
            input=REMOTE_SCRIPT,
            text=True,
            capture_output=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Command timed out")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    run_remote_script()

