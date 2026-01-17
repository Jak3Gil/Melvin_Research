#!/usr/bin/env python3
"""
Find the missing 13 motors
Try different baud rates and USB ports
"""

import serial
import time
import glob

def activate_motor(ser, can_id):
    """Activate motor using RobStride protocol"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.05)
    return ser.read(200)

def scan_motors(port, baud):
    """Scan for motors at given port and baud rate"""
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
        time.sleep(0.3)
        
        found = []
        
        # Quick scan of common IDs
        for motor_id in [1, 2, 3, 4, 5, 6, 7, 40, 41, 42, 43, 44, 45, 46, 47, 48, 80, 81, 82, 83, 84, 85, 86, 87, 88, 96, 97, 98, 99, 100, 104, 105, 106, 107, 108, 112, 113, 114, 115, 116, 120, 121, 122, 123, 124]:
            resp = activate_motor(ser, motor_id)
            if resp and len(resp) > 0:
                found.append(motor_id)
        
        ser.close()
        return found
        
    except Exception as e:
        return None

print("="*70)
print("FIND MISSING 13 MOTORS")
print("="*70)
print("\nSearching different baud rates and USB ports...")
print("="*70)

# Check for multiple USB ports
print("\n1. Checking for USB-Serial devices...")
print("-" * 70)

import subprocess
result = subprocess.run(['ls', '/dev/ttyUSB*'], 
                       capture_output=True, text=True, shell=True)

usb_ports = []
if result.returncode == 0:
    usb_ports = result.stdout.strip().split('\n')
    print(f"Found USB ports: {usb_ports}")
else:
    usb_ports = ['/dev/ttyUSB0']
    print(f"Only found: {usb_ports}")

# Test different baud rates
baud_rates = [115200, 230400, 460800, 921600, 1000000]

print("\n2. Scanning all combinations...")
print("-" * 70)

all_results = {}

for port in usb_ports:
    print(f"\nTesting {port}:")
    
    for baud in baud_rates:
        print(f"  Baud {baud}...", end='', flush=True)
        
        found = scan_motors(port, baud)
        
        if found is None:
            print(f" ✗ Can't open port")
        elif found:
            print(f" ✅ Found {len(found)} motors!")
            print(f"     IDs: {found}")
            all_results[(port, baud)] = found
        else:
            print(f" -")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if all_results:
    print(f"\n✅ Found motors at:")
    
    total_unique_ids = set()
    
    for (port, baud), ids in all_results.items():
        print(f"\n  {port} @ {baud} baud:")
        print(f"    IDs: {ids}")
        total_unique_ids.update(ids)
    
    print(f"\n✅ Total unique motor ID ranges found: {len(total_unique_ids)}")
    print(f"   IDs: {sorted(total_unique_ids)}")
    
    # Now do full scan at working configs
    print("\n" + "="*70)
    print("FULL SCAN at working configurations")
    print("="*70)
    
    for (port, baud), _ in all_results.items():
        print(f"\nFull scan: {port} @ {baud} baud")
        print("-" * 70)
        
        try:
            ser = serial.Serial(port, baud, timeout=0.5)
            time.sleep(0.3)
            
            all_ids = []
            
            for motor_id in range(0, 128):
                if motor_id % 16 == 0:
                    print(f"  {motor_id}-{min(motor_id+15, 127)}...", end='', flush=True)
                
                resp = activate_motor(ser, motor_id)
                if resp and len(resp) > 0:
                    all_ids.append(motor_id)
                    if motor_id % 16 != 0:
                        print(f"\n    ✓ {motor_id}", end='')
                elif motor_id % 16 == 15:
                    print(" -")
            
            print("\n")
            
            if all_ids:
                # Group into motors
                groups = []
                current_group = [all_ids[0]]
                for i in range(1, len(all_ids)):
                    if all_ids[i] == all_ids[i-1] + 1:
                        current_group.append(all_ids[i])
                    else:
                        groups.append(current_group)
                        current_group = [all_ids[i]]
                groups.append(current_group)
                
                print(f"  ✅ Found {len(groups)} motor groups:")
                for i, group in enumerate(groups, 1):
                    print(f"     Motor {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
            
            ser.close()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")

else:
    print(f"\n❌ No motors found at any baud rate or port")
    print(f"\nThis means:")
    print(f"  1. The 13 missing motors are powered OFF")
    print(f"  2. OR they're on a different/disconnected CAN bus")
    print(f"  3. OR they need a different USB-to-CAN adapter")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)

print("""
To find the missing 13 motors:

1. **Power Check**:
   - Count how many motors have power LEDs ON
   - Should be 15 total
   - If less than 15, some motors have no power

2. **Physical Test**:
   - Power OFF all motors
   - Power ON motors ONE AT A TIME
   - Run this script after each motor powers on
   - This will map physical motor → CAN ID range

3. **Check Wiring**:
   - Are all 15 motors on the same CAN bus?
   - Or are they split across multiple buses?
   - Check for second USB-to-CAN adapter

4. **Check Adapter**:
   - Is there a /dev/ttyUSB1 or /dev/ttyUSB2?
   - Some motors may be on a different adapter

Currently found: 2 motors (responding to 48 IDs total)
Still missing: 13 motors

""")

