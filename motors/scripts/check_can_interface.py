#!/usr/bin/env python3
"""
Check if we need to use SocketCAN instead of serial
Maybe the USB-CAN adapter is a proper CAN interface, not serial!
"""

import subprocess
import os

print("="*70)
print("CAN INTERFACE CHECK")
print("="*70)
print("\nChecking if USB-CAN adapter is a SocketCAN device...")
print("="*70)

# Check 1: List network interfaces
print("\n1. Network Interfaces:")
print("-" * 70)
try:
    result = subprocess.run(['ip', 'link', 'show'], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    if 'can0' in result.stdout or 'can1' in result.stdout:
        print("\n✅ FOUND CAN INTERFACE!")
        print("   Your adapter is a SocketCAN device, not serial!")
    else:
        print("\n⚠️  No CAN interface found")
        
except Exception as e:
    print(f"Error: {e}")

# Check 2: Check for CAN devices specifically
print("\n2. CAN-Specific Devices:")
print("-" * 70)
try:
    result = subprocess.run(['ls', '-la', '/sys/class/net/'], 
                          capture_output=True, text=True)
    
    can_devices = [line for line in result.stdout.split('\n') if 'can' in line.lower()]
    
    if can_devices:
        print("Found CAN devices:")
        for dev in can_devices:
            print(f"  {dev}")
    else:
        print("No CAN devices in /sys/class/net/")
        
except Exception as e:
    print(f"Error: {e}")

# Check 3: Check if can-utils is installed
print("\n3. CAN Utils Availability:")
print("-" * 70)
try:
    result = subprocess.run(['which', 'candump'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ can-utils installed: {result.stdout.strip()}")
    else:
        print("❌ can-utils NOT installed")
        print("   Install with: sudo apt-get install can-utils")
        
except Exception as e:
    print(f"Error: {e}")

# Check 4: Check USB device info
print("\n4. USB Device Information:")
print("-" * 70)
try:
    result = subprocess.run(['lsusb'], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    # Look for common CAN adapter names
    adapters = ['CAN', 'CANable', 'PEAK', 'Kvaser', 'PCAN', 'USB-CAN', 'Canable']
    found_adapter = False
    
    for line in result.stdout.split('\n'):
        for adapter in adapters:
            if adapter.lower() in line.lower():
                print(f"\n✅ Found possible CAN adapter: {line}")
                found_adapter = True
    
    if not found_adapter:
        print("\n⚠️  No obvious CAN adapter found in lsusb")
        
except Exception as e:
    print(f"Error: {e}")

# Check 5: Check dmesg for CAN-related messages
print("\n5. Recent CAN-Related Kernel Messages:")
print("-" * 70)
try:
    result = subprocess.run(['dmesg'], 
                          capture_output=True, text=True, shell=True)
    
    can_messages = [line for line in result.stdout.split('\n')[-100:] 
                   if 'can' in line.lower() or 'usb' in line.lower()]
    
    if can_messages:
        print("Recent CAN/USB messages:")
        for msg in can_messages[-20:]:  # Last 20
            print(f"  {msg}")
    else:
        print("No recent CAN-related messages")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
print("DIAGNOSIS & SOLUTION")
print("="*70)

print("""
📋 POSSIBLE SCENARIOS:

SCENARIO 1: SocketCAN Device (Proper CAN Interface)
----------------------------------------------------
If you saw 'can0' or 'can1' above:
  Your adapter is a proper CAN interface!
  
  You need to:
  1. Configure the CAN interface:
     sudo ip link set can0 type can bitrate 1000000
     sudo ip link set can0 up
  
  2. Use python-can library instead of pyserial:
     pip3 install python-can
  
  3. Use SocketCAN in code:
     import can
     bus = can.interface.Bus(channel='can0', bustype='socketcan')

SCENARIO 2: Serial CAN Adapter (SLCAN/Serial)
----------------------------------------------
If you saw /dev/ttyUSB0 but NO can0:
  Your adapter uses serial protocol (SLCAN)
  
  You need to:
  1. Configure SLCAN:
     sudo slcand -o -c -s8 /dev/ttyUSB0 can0
     sudo ip link set can0 up
  
  2. Then use SocketCAN as above

SCENARIO 3: Custom Serial Protocol
-----------------------------------
If adapter doesn't support SLCAN:
  It uses a custom serial protocol
  
  This is what we've been testing - and NOTHING works!
  This means:
  - Motors have no power
  - CAN wiring disconnected
  - Wrong adapter type
  - Adapter needs Windows driver/software

🔧 IMMEDIATE ACTION:
Run these commands on Jetson:

  # Check for CAN interface
  ip link show
  
  # If you see can0, configure it:
  sudo ip link set can0 type can bitrate 1000000
  sudo ip link set can0 up
  
  # Test with candump:
  candump can0
  
  # If that works, I'll write new code using python-can!

""")

