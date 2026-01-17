#!/usr/bin/env python3
"""
Example: Motor Control on Jetson
Demonstrates various ways to control motors via USB-to-CAN
"""
from jetson_motor_interface import JetsonMotorController
import time

def example_1_basic_scan():
    """Example 1: Basic motor scanning"""
    print("="*70)
    print("Example 1: Basic Motor Scanning")
    print("="*70)
    
    controller = JetsonMotorController()
    
    if controller.connect():
        motors = controller.scan_motors(start_id=1, end_id=127)
        print(f"\n✅ Found {len(motors)} motors")
        print(f"Motor IDs: {motors}")
        controller.disconnect()
    
    print()

def example_2_test_single_motor():
    """Example 2: Test a single motor"""
    print("="*70)
    print("Example 2: Test Single Motor")
    print("="*70)
    
    with JetsonMotorController() as controller:
        motor_id = 21  # Motor 3
        
        print(f"\nTesting motor {motor_id}...")
        print("Watch for movement!")
        
        controller.pulse_motor(motor_id, pulses=3, duration=0.4)
        
        print("✅ Test complete")
    
    print()

def example_3_manual_control():
    """Example 3: Manual motor control"""
    print("="*70)
    print("Example 3: Manual Motor Control")
    print("="*70)
    
    with JetsonMotorController() as controller:
        motor_id = 21
        
        print(f"\nManually controlling motor {motor_id}...")
        
        # Enable motor
        print("1. Enabling motor...")
        controller.enable_motor(motor_id)
        time.sleep(0.2)
        
        # Load parameters
        print("2. Loading parameters...")
        controller.load_params(motor_id)
        time.sleep(0.2)
        
        # Move forward
        print("3. Moving forward...")
        controller.move_motor(motor_id, speed=0.08, flag=1)
        time.sleep(0.5)
        
        # Stop
        print("4. Stopping...")
        controller.move_motor(motor_id, speed=0.0, flag=0)
        time.sleep(0.3)
        
        # Move backward
        print("5. Moving backward...")
        controller.move_motor(motor_id, speed=-0.08, flag=1)
        time.sleep(0.5)
        
        # Stop
        print("6. Stopping...")
        controller.move_motor(motor_id, speed=0.0, flag=0)
        time.sleep(0.2)
        
        # Disable motor
        print("7. Disabling motor...")
        controller.disable_motor(motor_id)
        
        print("✅ Manual control complete")
    
    print()

def example_4_multiple_motors():
    """Example 4: Control multiple motors"""
    print("="*70)
    print("Example 4: Control Multiple Motors")
    print("="*70)
    
    with JetsonMotorController() as controller:
        # Scan for motors
        motors = controller.scan_motors(start_id=8, end_id=31)
        
        if len(motors) < 3:
            print("⚠️  Need at least 3 motors for this demo")
            return
        
        # Test first 3 motors
        test_motors = motors[:3]
        
        print(f"\nTesting motors: {test_motors}")
        
        for motor_id in test_motors:
            print(f"\n→ Motor {motor_id}")
            controller.pulse_motor(motor_id, pulses=2, duration=0.3)
            time.sleep(0.5)
        
        print("\n✅ All motors tested")
    
    print()

def example_5_emergency_stop():
    """Example 5: Emergency stop"""
    print("="*70)
    print("Example 5: Emergency Stop")
    print("="*70)
    
    with JetsonMotorController() as controller:
        print("\nStarting motors...")
        
        # Enable and move multiple motors
        for motor_id in [8, 16, 21]:
            controller.enable_motor(motor_id)
            controller.load_params(motor_id)
            controller.move_motor(motor_id, speed=0.05, flag=1)
        
        print("Motors running...")
        time.sleep(1.0)
        
        # Emergency stop
        print("\n🛑 EMERGENCY STOP!")
        controller.emergency_stop_all()
        
        print("✅ All motors stopped")
    
    print()

def example_6_motor_info():
    """Example 6: Get motor information"""
    print("="*70)
    print("Example 6: Motor Information")
    print("="*70)
    
    with JetsonMotorController() as controller:
        # Scan motors
        motors = controller.scan_motors(start_id=1, end_id=127)
        
        # Get info
        info = controller.get_motor_info()
        
        print("\nConnection Information:")
        print(f"  Port: {info['port']}")
        print(f"  Baud Rate: {info['baud']}")
        print(f"  Connected: {info['connected']}")
        print(f"  Motors Found: {info['motors_found']}")
        print(f"  Motor IDs: {info['motor_ids']}")
        
        # Group motors by range
        if motors:
            print("\nMotor Ranges:")
            ranges = []
            start = motors[0]
            end = motors[0]
            
            for i in range(1, len(motors)):
                if motors[i] == end + 1:
                    end = motors[i]
                else:
                    ranges.append((start, end))
                    start = motors[i]
                    end = motors[i]
            
            ranges.append((start, end))
            
            for i, (start, end) in enumerate(ranges, 1):
                count = end - start + 1
                print(f"  Range {i}: IDs {start}-{end} ({count} IDs)")
    
    print()

def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  Jetson Motor Control Examples")
    print("="*70)
    print()
    
    try:
        # Run examples
        example_1_basic_scan()
        
        input("Press Enter to continue to Example 2 (test single motor)...")
        example_2_test_single_motor()
        
        input("Press Enter to continue to Example 3 (manual control)...")
        example_3_manual_control()
        
        input("Press Enter to continue to Example 4 (multiple motors)...")
        example_4_multiple_motors()
        
        input("Press Enter to continue to Example 5 (emergency stop)...")
        example_5_emergency_stop()
        
        input("Press Enter to continue to Example 6 (motor info)...")
        example_6_motor_info()
        
        print("="*70)
        print("  All Examples Complete!")
        print("="*70)
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Running emergency stop...")
        
        with JetsonMotorController() as controller:
            controller.emergency_stop_all()
        
        print("✅ Stopped")

if __name__ == '__main__':
    main()

