#!/usr/bin/env python3
"""
Interactive Motor Identification Tool
Helps you map CAN IDs to physical motor locations
"""
import sys
sys.path.insert(0, '/home/melvin')

from jetson_motor_interface import JetsonMotorController
import time

def main():
    print("="*70)
    print("  INTERACTIVE MOTOR IDENTIFICATION")
    print("="*70)
    print()
    print("This tool will help you identify which CAN ID controls")
    print("which physical motor on your robot.")
    print()
    
    motor_map = {}
    
    with JetsonMotorController() as controller:
        # Scan for motors
        print("Scanning for motors...")
        motors = controller.scan_motors(start_id=1, end_id=127)
        
        if not motors:
            print("❌ No motors found!")
            return
        
        print(f"\n✅ Found {len(motors)} motor IDs")
        print(f"IDs: {motors}")
        print()
        print("="*70)
        print()
        
        # Test each motor
        for i, motor_id in enumerate(motors, 1):
            print(f"\n{'='*70}")
            print(f"  Testing Motor ID {motor_id} ({i}/{len(motors)})")
            print(f"{'='*70}")
            print()
            print(f">>> WATCH YOUR ROBOT! <<<")
            print(f"Motor ID {motor_id} will pulse 3 times...")
            print()
            
            input("Press Enter to pulse this motor...")
            
            # Pulse the motor
            controller.pulse_motor(motor_id, pulses=3, duration=0.5)
            
            print()
            print("Did you see which motor moved?")
            print()
            
            # Get user input
            while True:
                location = input(f"Enter motor location (or 'skip' to skip): ").strip()
                
                if location.lower() == 'skip':
                    print("  Skipped")
                    break
                elif location:
                    motor_map[motor_id] = location
                    print(f"  ✓ Motor ID {motor_id} = {location}")
                    break
                else:
                    print("  Please enter a location or 'skip'")
            
            # Ask if user wants to continue
            if i < len(motors):
                print()
                cont = input("Continue to next motor? (y/n): ").strip().lower()
                if cont != 'y':
                    print("\nStopping identification...")
                    break
        
        # Show results
        print()
        print("="*70)
        print("  MOTOR IDENTIFICATION RESULTS")
        print("="*70)
        print()
        
        if motor_map:
            print("Motor Map:")
            print()
            for motor_id, location in sorted(motor_map.items()):
                print(f"  CAN ID {motor_id:3d} → {location}")
            print()
            
            # Save to file
            filename = "motor_map.txt"
            with open(filename, 'w') as f:
                f.write("Motor ID Mapping\n")
                f.write("="*50 + "\n\n")
                for motor_id, location in sorted(motor_map.items()):
                    f.write(f"ID {motor_id:3d} : {location}\n")
            
            print(f"✅ Motor map saved to: {filename}")
        else:
            print("No motors were identified.")
        
        print()
        print("="*70)
        print()
        print("NEXT STEPS:")
        print()
        print("1. Use Motor Studio on Windows to configure each motor")
        print("   to a single, unique CAN ID")
        print()
        print("2. Recommended ID assignment:")
        print("   - Left arm motors: IDs 1-4")
        print("   - Right arm motors: IDs 5-8")
        print("   - Head motors: IDs 9-10")
        print("   - Body motors: IDs 11+")
        print()
        print("3. After configuration, run this script again to verify")
        print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Stopping all motors...")
        with JetsonMotorController() as controller:
            controller.emergency_stop_all()
        print("✅ Stopped")

