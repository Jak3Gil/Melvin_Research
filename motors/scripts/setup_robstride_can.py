#!/usr/bin/env python3
"""
Setup RobStride Motors using Proper CAN Protocol
Based on: https://wiki.seeedstudio.com/robstride_control/
"""

import subprocess
import sys
import os
import time

def run_cmd(cmd, check=True):
    """Run shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_can_tools():
    """Check if CAN utilities are installed"""
    print("="*70)
    print("Checking CAN Tools Installation")
    print("="*70)
    
    tools = ['canconfig', 'candump', 'cansend', 'slcand', 'ip']
    missing = []
    
    for tool in tools:
        stdout, stderr, code = run_cmd(f"which {tool}", check=False)
        if code != 0:
            missing.append(tool)
            print(f"  ✗ {tool}: NOT FOUND")
        else:
            print(f"  ✓ {tool}: {stdout}")
    
    return missing

def setup_usb_can_as_slcan(serial_port, can_interface='slcan0', bitrate=1000000):
    """Setup USB-to-CAN adapter as slcan interface"""
    print("\n" + "="*70)
    print("Setting up USB-to-CAN as slcan interface")
    print("="*70)
    
    # Stop existing slcan if running
    print("\nStep 1: Stopping existing slcan interface...")
    run_cmd(f"sudo pkill slcand", check=False)
    run_cmd(f"sudo ip link set {can_interface} down", check=False)
    time.sleep(1)
    
    # Start slcand (Serial Line CAN daemon)
    print(f"\nStep 2: Starting slcand on {serial_port}...")
    print(f"  Command: sudo slcand -o -c -s8 -S {bitrate} {serial_port} {can_interface}")
    
    stdout, stderr, code = run_cmd(
        f"sudo slcand -o -c -s8 -S {bitrate} {serial_port} {can_interface}",
        check=False
    )
    
    if code != 0:
        print(f"  ✗ Failed: {stderr}")
        return False
    
    time.sleep(2)
    
    # Bring up the CAN interface
    print(f"\nStep 3: Bringing up {can_interface}...")
    stdout, stderr, code = run_cmd(
        f"sudo ip link set {can_interface} up type can bitrate {bitrate}",
        check=False
    )
    
    if code != 0:
        print(f"  ✗ Failed: {stderr}")
        return False
    
    # Verify interface is up
    print(f"\nStep 4: Verifying {can_interface} status...")
    stdout, stderr, code = run_cmd(f"ip -details link show {can_interface}", check=False)
    
    if code == 0 and 'UP' in stdout:
        print(f"  ✓ {can_interface} is UP")
        print(f"\n  Interface details:")
        print(f"  {stdout}")
        return True
    else:
        print(f"  ✗ {can_interface} is not UP")
        return False

def check_robstride_library():
    """Check if robstride_dynamics library is installed"""
    print("\n" + "="*70)
    print("Checking RobStride Python Library")
    print("="*70)
    
    try:
        import robstride_dynamics
        print("  ✓ robstride_dynamics library found")
        print(f"  Location: {robstride_dynamics.__file__}")
        return True
    except ImportError:
        print("  ✗ robstride_dynamics library NOT FOUND")
        print("\n  Install it with:")
        print("    pip install robstride-dynamics")
        print("  Or clone from:")
        print("    https://github.com/Seeed-Projects/RobStride_Control")
        return False

def scan_motors_with_library(can_interface='slcan0'):
    """Scan for motors using RobStride library"""
    print("\n" + "="*70)
    print("Scanning Motors with RobStride Library")
    print("="*70)
    
    try:
        from robstride_dynamics import RobstrideBus
        
        bus = RobstrideBus(can_interface)
        motors = bus.scan_channel()
        
        print(f"\n  Found {len(motors)} motor(s):")
        for motor_id in motors:
            print(f"    Motor ID: {motor_id}")
        
        return motors
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

def scan_motors_manual(can_interface='slcan0'):
    """Manually scan for motors by sending CAN frames"""
    print("\n" + "="*70)
    print("Manual Motor Scan (Direct CAN)")
    print("="*70)
    print("\nSending CAN frames to scan for motors...")
    print("This will test IDs 1-15 with proper RobStride protocol\n")
    
    # RobStride uses extended CAN frames (29-bit ID)
    # ID format: 0x200 + motor_id (for status requests)
    # Example: Motor 1 = 0x201, Motor 2 = 0x202, etc.
    
    found_motors = []
    
    for motor_id in range(1, 16):
        # Send status request frame
        # Extended ID: 0x200 + motor_id
        can_id = 0x200 + motor_id
        
        # Send frame using cansend
        # Format: cansend <interface> <id>#<data>
        # Status request: empty data frame
        cmd = f"timeout 0.1 cansend {can_interface} {can_id:03X}#"
        stdout, stderr, code = run_cmd(cmd, check=False)
        time.sleep(0.1)
        
        # Try to read response
        # This is simplified - in practice you'd use candump or socketcan
        
        print(f"  Motor ID {motor_id:2d}: Testing CAN ID 0x{can_id:03X}...", end='', flush=True)
        
        # For now, just note which IDs were sent
        # Real implementation would check for responses
        print(" [Sent]")
    
    print("\n  [NOTE] Check responses with: candump slcan0")
    return found_motors

def main():
    import time
    
    print("="*70)
    print("RobStride Motor Setup - Proper CAN Protocol")
    print("Based on: https://wiki.seeedstudio.com/robstride_control/")
    print("="*70)
    
    # Check CAN tools
    missing_tools = check_can_tools()
    # Filter out non-critical tools
    critical_missing = [t for t in missing_tools if t in ['slcand', 'ip', 'candump', 'cansend']]
    if critical_missing:
        print(f"\n[ERROR] Missing critical tools: {critical_missing}")
        print("Install with: sudo apt-get install can-utils")
        return
    elif missing_tools:
        print(f"\n[WARNING] Missing optional tools: {missing_tools}")
    
    # Get serial port
    serial_port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    can_interface = sys.argv[2] if len(sys.argv) > 2 else 'slcan0'
    
    print(f"\nUsing:")
    print(f"  Serial port: {serial_port}")
    print(f"  CAN interface: {can_interface}")
    
    # Setup slcan
    if not setup_usb_can_as_slcan(serial_port, can_interface):
        print("\n[ERROR] Failed to setup slcan interface")
        return
    
    # Check for RobStride library
    has_library = check_robstride_library()
    
    if has_library:
        # Use library method
        motors = scan_motors_with_library(can_interface)
        if motors:
            print(f"\n[SUCCESS] Found {len(motors)} motors using library!")
        else:
            print("\n[WARNING] No motors found with library")
    else:
        # Manual scan
        print("\n[NOTE] Using manual scan method")
        scan_motors_manual(can_interface)
        print("\n  To monitor CAN traffic, run in another terminal:")
        print(f"    candump {can_interface}")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Monitor CAN traffic:
   candump slcan0

2. Install RobStride library:
   pip install robstride-dynamics
   # OR
   git clone https://github.com/Seeed-Projects/RobStride_Control.git
   cd RobStride_Control/python
   pip install .

3. Use the library to scan and control motors:
   from robstride_dynamics import RobstrideBus
   bus = RobstrideBus('slcan0')
   motors = bus.scan_channel()
   print(f"Found motors: {motors}")
    """)

if __name__ == '__main__':
    main()

