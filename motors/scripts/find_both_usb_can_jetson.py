#!/usr/bin/env python3
"""
Find Both USB-CAN Adapters on Jetson
Connects via SSH and detects all USB-CAN devices (typically /dev/ttyUSB0 and /dev/ttyUSB1)
"""

import subprocess
import sys
import re
from typing import List, Dict, Optional

def run_ssh_command(hostname: str, username: str, port: int, command: str, timeout: int = 30) -> tuple:
    """Run a command on Jetson via SSH"""
    ssh_cmd = [
        'ssh',
        '-p', str(port),
        f'{username}@{hostname}',
        command
    ]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return None, "Command timed out", 1
    except Exception as e:
        return None, str(e), 1

def find_usb_can_devices(hostname: str = "192.168.55.1", username: str = "melvin", port: int = 22) -> List[Dict]:
    """Find all USB-CAN adapters on Jetson"""
    
    print("=" * 70)
    print("FIND BOTH USB-CAN ADAPTERS ON JETSON")
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
    devices_found = []
    
    # 1. Find all /dev/ttyUSB* devices
    print("1. Finding USB Serial Devices (/dev/ttyUSB*)...")
    print("-" * 70)
    stdout, stderr, code = run_ssh_command(hostname, username, port, 
        "ls -la /dev/ttyUSB* 2>/dev/null | head -10 || echo ''")
    
    if stdout and stdout.strip():
        print(stdout)
        # Extract device names
        ttyusb_pattern = r'/dev/ttyUSB\d+'
        ttyusb_devices = re.findall(ttyusb_pattern, stdout)
        
        if ttyusb_devices:
            print(f"  [OK] Found {len(ttyusb_devices)} USB serial device(s)")
            for device in sorted(ttyusb_devices):
                # Get device info
                info_stdout, _, _ = run_ssh_command(hostname, username, port,
                    f"udevadm info {device} 2>/dev/null | grep -E 'ID_SERIAL|ID_MODEL|ID_VENDOR|ID_USB_INTERFACE_NUM' || echo ''")
                
                device_info = {
                    'device': device,
                    'type': 'USB Serial',
                    'info': info_stdout.strip() if info_stdout else 'No udev info available'
                }
                
                # Check if device is accessible
                test_stdout, _, test_code = run_ssh_command(hostname, username, port,
                    f"test -r {device} && echo 'readable' || echo 'not readable'")
                
                if 'readable' in (test_stdout or ''):
                    device_info['accessible'] = True
                else:
                    device_info['accessible'] = False
                
                devices_found.append(device_info)
                print(f"    Device: {device}")
                if device_info['accessible']:
                    print(f"      Status: Accessible")
                else:
                    print(f"      Status: Not accessible (may need permissions)")
        else:
            print("  [INFO] No /dev/ttyUSB* devices found")
    else:
        print("  [INFO] No /dev/ttyUSB* devices found")
    
    print()
    
    # 2. Check USB devices with lsusb to identify CAN adapters
    print("2. Checking USB Devices (lsusb)...")
    print("-" * 70)
    stdout, stderr, code = run_ssh_command(hostname, username, port, "lsusb")
    
    if stdout:
        print(stdout)
        # Look for common USB-CAN adapter chips
        can_keywords = ['cp210', 'ch340', 'ft232', 'ftdi', 'cp210x', 'silicon labs']
        can_devices = []
        
        for line in stdout.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in can_keywords):
                can_devices.append(line.strip())
                print(f"  [FOUND] Possible USB-CAN adapter: {line.strip()}")
        
        if not can_devices:
            print("  [INFO] No obvious USB-CAN adapter chips found in lsusb")
            print("         (This is normal if using generic USB-CAN adapters)")
    
    print()
    
    # 3. Check /sys/bus/usb-serial/devices for active serial devices
    print("3. Checking Active USB Serial Devices (/sys/bus/usb-serial/devices/)...")
    print("-" * 70)
    stdout, stderr, code = run_ssh_command(hostname, username, port,
        "ls -la /sys/bus/usb-serial/devices/ 2>/dev/null || echo 'No USB serial devices in /sys'")
    
    if stdout and 'No USB serial' not in stdout:
        print(stdout)
        # Extract device names
        tty_pattern = r'ttyUSB\d+'
        tty_devices = re.findall(tty_pattern, stdout)
        if tty_devices:
            print(f"  [OK] Found {len(set(tty_devices))} active USB serial device(s) in sysfs")
    else:
        print(stdout if stdout else "  [INFO] No active USB serial devices found in sysfs")
    
    print()
    
    # 4. Check dmesg for USB device connections
    print("4. Recent USB Device Connections (dmesg)...")
    print("-" * 70)
    stdout, stderr, code = run_ssh_command(hostname, username, port,
        "dmesg | grep -iE 'ttyUSB|usb.*serial|cp210|ch340' | tail -20 || echo 'No recent USB serial messages'")
    
    if stdout and 'No recent' not in stdout:
        print(stdout)
    else:
        print("  [INFO] No recent USB serial messages in dmesg")
    
    print()
    
    # 5. Test each device to see if it responds to CAN commands
    print("5. Testing USB-CAN Adapters with AT Commands...")
    print("-" * 70)
    
    if devices_found:
        for device_info in devices_found:
            device = device_info['device']
            print(f"  Testing {device}...", end=" ", flush=True)
            
            # Try to send AT+AT command and see if we get a response
            # This requires Python on Jetson with pyserial
            test_cmd = f"""python3 << 'EOF'
import serial
import time
import sys
try:
    ser = serial.Serial('{device}', 921600, timeout=0.5)
    time.sleep(0.2)
    ser.write(bytes.fromhex('41542b41540d0a'))  # AT+AT
    time.sleep(0.3)
    resp = ser.read(100)
    ser.close()
    if len(resp) > 0:
        print('RESPONDED')
        print(resp.hex()[:40])
    else:
        print('NO_RESPONSE')
except Exception as e:
    print(f'ERROR: {{str(e)}}')
EOF"""
            
            test_stdout, test_stderr, test_code = run_ssh_command(hostname, username, port, test_cmd)
            
            if test_stdout:
                if 'RESPONDED' in test_stdout:
                    device_info['can_responsive'] = True
                    print("[OK] Responds to AT commands")
                    # Extract response hex
                    for line in test_stdout.split('\n'):
                        if len(line) > 10 and all(c in '0123456789abcdef' for c in line.lower()):
                            device_info['test_response'] = line[:40]
                elif 'NO_RESPONSE' in test_stdout:
                    device_info['can_responsive'] = False
                    print("[INFO] No response (may not be CAN adapter or may be in use)")
                elif 'ERROR' in test_stdout:
                    device_info['can_responsive'] = None
                    device_info['error'] = test_stdout.strip()
                    print(f"[ERROR] {test_stdout.strip()}")
                else:
                    print("[UNKNOWN]")
            else:
                print("[SKIP] Could not test")
    else:
        print("  [SKIP] No USB devices found to test")
    
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    if devices_found:
        print(f"Found {len(devices_found)} USB serial device(s):")
        print()
        
        can_adapters = []
        for device_info in devices_found:
            device = device_info['device']
            print(f"  Device: {device}")
            print(f"    Type: {device_info['type']}")
            print(f"    Accessible: {'Yes' if device_info.get('accessible') else 'No'}")
            
            if device_info.get('can_responsive') is True:
                print(f"    CAN Adapter: Yes (responds to AT commands)")
                can_adapters.append(device)
            elif device_info.get('can_responsive') is False:
                print(f"    CAN Adapter: Unknown (no response)")
            elif device_info.get('can_responsive') is None:
                print(f"    CAN Adapter: Unknown (error: {device_info.get('error', 'unknown')})")
            else:
                print(f"    CAN Adapter: Not tested")
            
            if device_info.get('test_response'):
                print(f"    Test Response: {device_info['test_response']}...")
            
            print()
        
        if can_adapters:
            print("=" * 70)
            print("USB-CAN ADAPTERS READY TO USE")
            print("=" * 70)
            print()
            print("Use these devices in your Python scripts:")
            for idx, adapter in enumerate(sorted(can_adapters), 1):
                print(f"  Adapter {idx}: {adapter}")
            print()
            print("Example usage in Python:")
            for adapter in sorted(can_adapters):
                print(f"  ser = serial.Serial('{adapter}', 921600)")
            print()
        else:
            print("=" * 70)
            print("NO CAN ADAPTERS DETECTED")
            print("=" * 70)
            print()
            print("If devices were found but not responding:")
            print("  1. Check if devices are in use by another program")
            print("  2. Set permissions: sudo chmod 666 /dev/ttyUSB*")
            print("  3. Add user to dialout group: sudo usermod -aG dialout $USER")
            print("  4. Verify devices are USB-CAN adapters (not just USB serial)")
            print()
    else:
        print("[FAIL] No USB serial devices found!")
        print()
        print("Possible reasons:")
        print("  1. USB-CAN adapters not connected")
        print("  2. USB drivers not installed")
        print("  3. Devices connected but not recognized")
        print()
        print("Try:")
        print("  - Check USB connections")
        print("  - Install USB serial drivers: sudo apt-get install setserial")
        print("  - Check dmesg on Jetson: dmesg | tail -50")
        print()
    
    print("=" * 70)
    
    return devices_found

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Find both USB-CAN adapters on Jetson')
    parser.add_argument('--hostname', '-H', default='192.168.55.1',
                       help='Jetson hostname or IP (default: 192.168.55.1 for USB network)')
    parser.add_argument('--username', '-u', default='melvin',
                       help='SSH username (default: melvin)')
    parser.add_argument('--port', '-p', type=int, default=22,
                       help='SSH port (default: 22)')
    
    args = parser.parse_args()
    
    find_usb_can_devices(args.hostname, args.username, args.port)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

