#!/usr/bin/env python3
"""
Scan for RobStride motors using the actual SDK API
Based on: https://github.com/LyraLiu1208/robstride-sdk
"""

import sys
import time

def scan_motors(can_interface='can0', max_id=15):
    """Scan for motors using the SDK"""
    print("="*70)
    print("RobStride Motor Scan - Using SDK")
    print("="*70)
    print(f"CAN Interface: {can_interface}")
    print(f"Testing IDs: 1-{max_id}\n")
    
    try:
        from robstride import RobStrideMotor, MotorType
        
        found_motors = []
        
        for motor_id in range(1, max_id + 1):
            print(f"  Testing Motor ID {motor_id}...", end='', flush=True)
            try:
                # Try RS05 motor type first (most common)
                motor = RobStrideMotor(
                    can_id=motor_id,
                    interface=can_interface,
                    motor_type=MotorType.RS05,
                    timeout=0.5
                )
                
                # Try to connect
                motor.connect()
                
                # Try to get device ID (verifies motor responds)
                device_id = motor.get_device_id()
                
                if device_id:
                    found_motors.append(motor_id)
                    print(f" ✓ FOUND (Device ID: {device_id})")
                else:
                    print(f" -")
                
                motor.disconnect()
                
            except Exception as e:
                print(f" -")
                # Motor not found or error
                pass
            
            time.sleep(0.1)
        
        return found_motors
    except ImportError as e:
        print(f"\n[ERROR] Failed to import SDK: {e}")
        print("Make sure SDK is installed: cd robstride-sdk && pip install -e .")
        return []
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return []

def test_motor_info(can_interface, motor_id):
    """Get detailed info from a found motor"""
    print("\n" + "="*70)
    print(f"Motor {motor_id} Information")
    print("="*70)
    
    try:
        from robstride import RobStrideMotor, MotorType
        
        motor = RobStrideMotor(
            can_id=motor_id,
            interface=can_interface,
            motor_type=MotorType.RS05
        )
        
        motor.connect()
        
        print(f"\n  Device ID: {motor.get_device_id()}")
        print(f"  Position: {motor.position:.3f} rad")
        print(f"  Velocity: {motor.velocity:.3f} rad/s")
        print(f"  Temperature: {motor.temperature:.1f}°C")
        print(f"  Error Code: {motor.error_code}")
        
        motor.disconnect()
        return True
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False

def main():
    can_interface = sys.argv[1] if len(sys.argv) > 1 else 'can0'
    
    # Scan for motors
    found = scan_motors(can_interface, max_id=15)
    
    print("\n" + "="*70)
    print("SCAN RESULTS")
    print("="*70)
    
    if found:
        print(f"\n  ✓ Found {len(found)} motor(s): {found}")
        print(f"  ✗ Missing: {15 - len(found)} motors")
        
        # Get info from first found motor
        if found:
            print(f"\n  Getting info from Motor {found[0]}...")
            test_motor_info(can_interface, found[0])
    else:
        print("\n  ✗ No motors found")
        print("\n  Troubleshooting:")
        print(f"    1. Check CAN interface: ip link show {can_interface}")
        print(f"    2. Monitor CAN traffic: candump {can_interface}")
        print(f"    3. Try other interface: python3 scan_with_robstride_sdk.py can1")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()

