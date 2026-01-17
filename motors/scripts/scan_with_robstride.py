#!/usr/bin/env python3
"""
Scan for RobStride motors using official library on CAN interfaces
"""
import sys
sys.path.insert(0, '/home/melvin/RobStride_Control/python')

print("="*70)
print("  RobStride Motor Scanner (Official Library)")
print("="*70)
print()

try:
    from robstride_dynamics import RobstrideBus
    print("✓ RobStride library imported successfully")
    print()
except ImportError as e:
    print(f"✗ Failed to import RobStride: {e}")
    sys.exit(1)

# Test both CAN interfaces
can_interfaces = ['can0', 'can1']

all_motors = {}

for interface in can_interfaces:
    print(f"{'='*70}")
    print(f"Scanning {interface.upper()}")
    print(f"{'='*70}")
    
    try:
        bus = RobstrideBus(interface)
        print(f"✓ Connected to {interface}")
        
        print(f"Scanning for motors...")
        motors = bus.scan_channel()
        
        if motors:
            print(f"\n✓ Found {len(motors)} motor(s) on {interface}:")
            for motor_id in motors:
                print(f"  - Motor ID: {motor_id}")
            all_motors[interface] = motors
        else:
            print(f"\n✗ No motors found on {interface}")
        
    except Exception as e:
        print(f"✗ Error with {interface}: {e}")
        import traceback
        traceback.print_exc()
    
    print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)

total_motors = sum(len(motors) for motors in all_motors.values())

if total_motors > 0:
    print(f"\n✓ Total motors found: {total_motors}")
    for interface, motors in all_motors.items():
        print(f"\n{interface.upper()}: {len(motors)} motor(s)")
        for motor_id in motors:
            print(f"  - Motor ID: {motor_id}")
else:
    print("\n✗ No motors found on any CAN interface")
    print("\nTroubleshooting:")
    print("  1. Check if motors are powered on")
    print("  2. Verify CAN bus wiring (CAN-H, CAN-L)")
    print("  3. Check CAN bus bitrate (currently 500kbps)")
    print("  4. Try adjusting CAN bitrate:")
    print("     sudo ip link set can0 down")
    print("     sudo ip link set can0 type can bitrate 1000000")
    print("     sudo ip link set can0 up")

print()

