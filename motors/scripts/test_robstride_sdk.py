#!/usr/bin/env python3
"""
Test RobStride SDK from https://github.com/LyraLiu1208/robstride-sdk
This SDK uses python-can and SocketCAN (not L91 protocol)
"""

import sys
import subprocess

def install_sdk():
    """Install the robstride-sdk"""
    print("="*70)
    print("Installing RobStride SDK")
    print("="*70)
    
    print("\nStep 1: Installing python-can...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "python-can"], check=True)
        print("  ✓ python-can installed")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to install python-can: {e}")
        return False
    
    print("\nStep 2: Cloning robstride-sdk...")
    try:
        subprocess.run(["git", "clone", "https://github.com/LyraLiu1208/robstride-sdk.git"], check=True)
        print("  ✓ SDK cloned")
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e) or e.returncode == 128:
            print("  ℹ SDK directory already exists")
        else:
            print(f"  ✗ Failed to clone: {e}")
            return False
    
    print("\nStep 3: Installing SDK...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "robstride-sdk"], check=True)
        print("  ✓ SDK installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to install SDK: {e}")
        return False

def test_sdk_import():
    """Test if SDK can be imported"""
    print("\n" + "="*70)
    print("Testing SDK Import")
    print("="*70)
    
    try:
        from robstride import RobStrideMotor, ProtocolType
        print("  ✓ SDK imported successfully")
        print(f"  Available protocols: {list(ProtocolType)}")
        return True
    except ImportError as e:
        print(f"  ✗ Failed to import: {e}")
        return False

def scan_motors_private(can_interface='can0', max_id=15):
    """Scan for motors using Private protocol (29-bit extended frames)"""
    print("\n" + "="*70)
    print(f"Scanning Motors - Private Protocol (Extended CAN)")
    print("="*70)
    print(f"CAN Interface: {can_interface}")
    print(f"Testing IDs: 1-{max_id}\n")
    
    try:
        from robstride import RobStrideMotor, ProtocolType
        
        found_motors = []
        
        for motor_id in range(1, max_id + 1):
            print(f"  Testing Motor ID {motor_id}...", end='', flush=True)
            try:
                motor = RobStrideMotor(
                    can_id=motor_id,
                    interface=can_interface,
                    protocol=ProtocolType.PRIVATE
                )
                
                # Try to connect and get info
                with motor:
                    # Try to get motor info (this will fail if motor doesn't respond)
                    info = motor.get_motor_info()
                    found_motors.append(motor_id)
                    print(f" ✓ FOUND")
            except Exception as e:
                print(f" -")
                # Motor not found or error
                pass
        
        return found_motors
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return []

def scan_motors_mit(can_interface='can0', max_id=15):
    """Scan for motors using MIT protocol (11-bit standard frames)"""
    print("\n" + "="*70)
    print(f"Scanning Motors - MIT Protocol (Standard CAN)")
    print("="*70)
    print(f"CAN Interface: {can_interface}")
    print(f"Testing IDs: 1-{max_id}\n")
    
    try:
        from robstride import RobStrideMotor, ProtocolType
        
        found_motors = []
        
        for motor_id in range(1, max_id + 1):
            print(f"  Testing Motor ID {motor_id}...", end='', flush=True)
            try:
                motor = RobStrideMotor(
                    can_id=motor_id,
                    interface=can_interface,
                    protocol=ProtocolType.MIT
                )
                
                with motor:
                    # Try to enable (this will fail if motor doesn't respond)
                    motor.enable()
                    found_motors.append(motor_id)
                    print(f" ✓ FOUND")
                    motor.disable()
            except Exception as e:
                print(f" -")
                pass
        
        return found_motors
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return []

def test_motor_control(can_interface, motor_id):
    """Test controlling a found motor"""
    print("\n" + "="*70)
    print(f"Testing Motor Control - ID {motor_id}")
    print("="*70)
    
    try:
        from robstride import RobStrideMotor, ProtocolType
        
        motor = RobStrideMotor(
            can_id=motor_id,
            interface=can_interface,
            protocol=ProtocolType.PRIVATE
        )
        
        with motor:
            print(f"\n  Enabling motor...")
            motor.enable()
            
            print(f"  Getting motor info...")
            info = motor.get_motor_info()
            print(f"    {info}")
            
            print(f"  Setting position control...")
            motor.set_position_control(position=0.5, speed_limit=2.0)
            
            print(f"  Reading position: {motor.position:.3f} rad")
            
            print(f"  Disabling motor...")
            motor.disable()
            
            print(f"\n  ✓ Motor control test successful!")
            return True
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test RobStride SDK')
    parser.add_argument('interface', nargs='?', default='can0', help='CAN interface (default: can0)')
    parser.add_argument('--install', action='store_true', help='Install SDK first')
    parser.add_argument('--scan', action='store_true', help='Scan for motors')
    parser.add_argument('--test-id', type=int, help='Test specific motor ID')
    parser.add_argument('--protocol', choices=['private', 'mit', 'both'], default='both', help='Protocol to use')
    
    args = parser.parse_args()
    
    print("="*70)
    print("RobStride SDK Test")
    print("Based on: https://github.com/LyraLiu1208/robstride-sdk")
    print("="*70)
    
    # Install if requested
    if args.install:
        if not install_sdk():
            print("\n[ERROR] SDK installation failed")
            return
    
    # Test import
    if not test_sdk_import():
        print("\n[ERROR] SDK not available. Try: python3 test_robstride_sdk.py --install")
        return
    
    # Scan for motors
    if args.scan or args.test_id:
        all_found = []
        
        if args.protocol in ['private', 'both']:
            found = scan_motors_private(args.interface, max_id=15)
            all_found.extend(found)
        
        if args.protocol in ['mit', 'both']:
            found = scan_motors_mit(args.interface, max_id=15)
            all_found.extend([m for m in found if m not in all_found])
        
        print("\n" + "="*70)
        print("SCAN RESULTS")
        print("="*70)
        if all_found:
            unique_found = sorted(set(all_found))
            print(f"\n  Found {len(unique_found)} motor(s): {unique_found}")
            print(f"  Still missing: {15 - len(unique_found)} motors")
        else:
            print("\n  ✗ No motors found")
    
    # Test specific motor
    if args.test_id:
        test_motor_control(args.interface, args.test_id)
    
    print("\n" + "="*70)
    print("USAGE EXAMPLES")
    print("="*70)
    print("""
# Scan for motors:
python3 test_robstride_sdk.py can0 --scan

# Test specific motor:
python3 test_robstride_sdk.py can0 --test-id 1

# Use MIT protocol only:
python3 test_robstride_sdk.py can0 --scan --protocol mit

# Use CLI tool:
python3 robstride-sdk/robstride_cli.py --interface can0 --motor_id 0x01 info
    """)

if __name__ == '__main__':
    main()

