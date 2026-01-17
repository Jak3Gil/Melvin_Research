#!/usr/bin/env python3
"""
Analyze Motor Groups - Detailed Analysis
Tests individual IDs to determine how many UNIQUE physical motors exist
"""
import sys
sys.path.insert(0, '/home/melvin')

from jetson_motor_interface import JetsonMotorController
import time

def test_individual_ids(controller, ids_to_test):
    """Test specific IDs and ask user which motor moved"""
    motor_map = {}
    
    print("="*70)
    print("  INDIVIDUAL ID TESTING")
    print("="*70)
    print()
    print("We'll test specific IDs to see if they control DIFFERENT motors")
    print()
    
    for test_id in ids_to_test:
        print(f"\n{'='*70}")
        print(f"  Testing ID {test_id}")
        print(f"{'='*70}")
        print()
        print(">>> WATCH YOUR ROBOT! <<<")
        print(f"Motor ID {test_id} will pulse 3 times...")
        print()
        
        input("Press Enter to pulse this motor...")
        
        # Pulse the motor
        controller.pulse_motor(test_id, pulses=3, duration=0.5)
        
        print()
        print("Which motor moved?")
        print("  Enter a number (1-15) or description")
        print("  Or 'same' if same as previous motor")
        print("  Or 'skip' to skip")
        
        location = input("Motor: ").strip()
        
        if location.lower() not in ['skip', '']:
            motor_map[test_id] = location
            print(f"  ✓ ID {test_id} = Motor {location}")
        
        print()
    
    return motor_map

def main():
    print("="*70)
    print("  DETAILED MOTOR GROUP ANALYSIS")
    print("="*70)
    print()
    print("Goal: Determine how many UNIQUE physical motors exist")
    print()
    print("Strategy:")
    print("  1. Test IDs at the START of each suspected group")
    print("  2. See if they control DIFFERENT physical motors")
    print("  3. Count unique motors")
    print()
    
    with JetsonMotorController() as controller:
        # Scan for motors
        print("Scanning for motors...")
        motors = controller.scan_motors(start_id=1, end_id=127)
        
        print(f"✓ Found {len(motors)} responding IDs")
        print(f"  IDs: {motors}")
        print()
        
        # Based on your findings, test these specific IDs:
        # These are likely the START of each motor's ID range
        test_ids = [8, 16, 21, 24, 31, 32, 64, 72]
        
        print("="*70)
        print("  HYPOTHESIS")
        print("="*70)
        print()
        print("Based on typical RobStride motor behavior:")
        print()
        print("Suspected motor groups:")
        print("  Motor 1: IDs 8-15   (test ID 8)")
        print("  Motor 2: IDs 16-20  (test ID 16)")
        print("  Motor 3: IDs 21-23  (test ID 21)")
        print("  Motor 4: IDs 24-31  (test ID 24 or 31)")
        print("  Motor 5: IDs 32-39  (test ID 32)")
        print("  Motor 6: IDs 64-71  (test ID 64)")
        print("  Motor 7: IDs 72-79  (test ID 72)")
        print()
        print("We'll test these specific IDs to see if they're different motors")
        print()
        
        available_test_ids = [id for id in test_ids if id in motors]
        
        if not available_test_ids:
            print("✗ None of the test IDs are responding!")
            return
        
        print(f"Testing IDs: {available_test_ids}")
        print()
        
        input("Press Enter to start testing...")
        print()
        
        # Test each ID
        motor_map = test_individual_ids(controller, available_test_ids)
        
        # Analyze results
        print()
        print("="*70)
        print("  ANALYSIS RESULTS")
        print("="*70)
        print()
        
        if not motor_map:
            print("No motors were identified")
            return
        
        # Count unique motors
        unique_motors = set(motor_map.values())
        
        print(f"IDs tested: {len(motor_map)}")
        print(f"Unique motors found: {len(unique_motors)}")
        print()
        
        print("Motor Identification:")
        for test_id, location in sorted(motor_map.items()):
            print(f"  ID {test_id:3d} → Motor {location}")
        
        print()
        print("="*70)
        print("  CONCLUSION")
        print("="*70)
        print()
        
        if len(unique_motors) < 15:
            print(f"⚠️  Found only {len(unique_motors)} unique motors, expected 15")
            print()
            print("Possible reasons:")
            print("  1. Not all motors are powered on")
            print("  2. Some motors not connected to this CAN bus")
            print("  3. Need to test more IDs to find all motors")
            print("  4. Some motors may be at IDs we haven't tested")
            print()
            print("RECOMMENDATIONS:")
            print("  1. Check if all 15 motors have power (LED on)")
            print("  2. Test more IDs in the 40-63 range")
            print("  3. Test IDs in the 80-127 range")
            print("  4. Check if some motors on different CAN bus")
        else:
            print(f"✓ Found all {len(unique_motors)} motors!")
            print()
            print("NEXT STEP: Reconfigure each motor to single ID")
        
        # Save results
        with open('motor_analysis_results.txt', 'w') as f:
            f.write("Motor Analysis Results\n")
            f.write("="*50 + "\n\n")
            f.write(f"IDs tested: {len(motor_map)}\n")
            f.write(f"Unique motors: {len(unique_motors)}\n\n")
            
            f.write("Motor Map:\n")
            for test_id, location in sorted(motor_map.items()):
                f.write(f"  ID {test_id:3d} → Motor {location}\n")
        
        print()
        print("✓ Results saved to: motor_analysis_results.txt")
        print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

