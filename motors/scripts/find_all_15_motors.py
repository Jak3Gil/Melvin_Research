#!/usr/bin/env python3
"""
Find All 15 Motors - Comprehensive Search
Helps locate all 15 physical motors
"""
import sys
sys.path.insert(0, '/home/melvin')

from jetson_motor_interface import JetsonMotorController
import time

def analyze_motor_groups(motor_ids):
    """Analyze motor IDs to estimate physical motor count"""
    if not motor_ids:
        return []
    
    # Group consecutive IDs
    groups = []
    current_group = [motor_ids[0]]
    
    for i in range(1, len(motor_ids)):
        if motor_ids[i] == motor_ids[i-1] + 1:
            current_group.append(motor_ids[i])
        else:
            groups.append(current_group)
            current_group = [motor_ids[i]]
    
    groups.append(current_group)
    
    return groups

def main():
    print("="*70)
    print("  FIND ALL 15 MOTORS - COMPREHENSIVE SEARCH")
    print("="*70)
    print()
    print("Expected: 15 physical motors")
    print("Goal: Find and identify all 15 motors")
    print()
    
    with JetsonMotorController() as controller:
        # Scan full range
        print("Scanning for motors (IDs 1-255)...")
        motors = controller.scan_motors(start_id=1, end_id=255)
        
        print(f"\n✓ Found {len(motors)} responding CAN IDs")
        print()
        
        # Analyze groups
        groups = analyze_motor_groups(motors)
        
        print("="*70)
        print(f"  MOTOR GROUPS DETECTED: {len(groups)}")
        print("="*70)
        print()
        
        for i, group in enumerate(groups, 1):
            print(f"Group {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
        
        print()
        print("="*70)
        print("  ANALYSIS")
        print("="*70)
        print()
        print(f"Responding ID groups: {len(groups)}")
        print(f"Expected motors: 15")
        print(f"Missing motors: {15 - len(groups)}")
        print()
        
        if len(groups) < 15:
            print("⚠️  NOT ALL MOTORS FOUND!")
            print()
            print("Possible reasons:")
            print("  1. Some motors on different CAN bus (can0 vs can1)")
            print("  2. Some motors not powered on")
            print("  3. Some motors not connected to USB-to-CAN")
            print("  4. Some motors need different communication protocol")
            print("  5. Some motors at IDs outside scanned range")
            print()
            print("TROUBLESHOOTING STEPS:")
            print()
            print("1. Check if motors are on CAN0 or CAN1:")
            print("   - USB-to-CAN usually connects to one CAN bus")
            print("   - Jetson has can0 and can1 interfaces")
            print("   - Some motors might be on the other bus")
            print()
            print("2. Verify all motors are powered:")
            print("   - Check power supply to all motors")
            print("   - Look for LED indicators on motors")
            print()
            print("3. Check CAN bus wiring:")
            print("   - Are all 15 motors wired to same CAN bus?")
            print("   - Or split between can0 and can1?")
            print()
            print("4. Test each motor group:")
            print("   - Let's test each group to see which physical motor it is")
            print()
        
        # Test each group
        print("="*70)
        print("  TESTING MOTOR GROUPS")
        print("="*70)
        print()
        print("This will test the FIRST ID from each group.")
        print("Watch which physical motor moves!")
        print()
        
        input("Press Enter to start testing...")
        print()
        
        motor_map = {}
        
        for i, group in enumerate(groups, 1):
            test_id = group[0]  # Test first ID in group
            
            print(f"\n{'='*70}")
            print(f"  GROUP {i}/{len(groups)}: Testing ID {test_id}")
            print(f"  (Group contains IDs: {group[0]}-{group[-1]})")
            print(f"{'='*70}")
            print()
            print(">>> WATCH YOUR ROBOT! <<<")
            print(f"Motor ID {test_id} will pulse {i} times...")
            print()
            
            input("Press Enter to pulse this motor...")
            
            # Pulse with unique pattern
            controller.pulse_motor(test_id, pulses=i, duration=0.5)
            
            print()
            location = input(f"Which motor moved? (or 'skip'): ").strip()
            
            if location.lower() != 'skip' and location:
                motor_map[i] = {
                    'ids': group,
                    'test_id': test_id,
                    'location': location
                }
                print(f"  ✓ Group {i} (ID {test_id}) = {location}")
            
            print()
        
        # Summary
        print("="*70)
        print("  MOTOR IDENTIFICATION RESULTS")
        print("="*70)
        print()
        
        if motor_map:
            print(f"Identified {len(motor_map)} motor groups:")
            print()
            for group_num, info in motor_map.items():
                print(f"Motor Group {group_num}:")
                print(f"  Location: {info['location']}")
                print(f"  IDs: {info['ids'][0]}-{info['ids'][-1]} ({len(info['ids'])} IDs)")
                print(f"  Use ID: {info['test_id']}")
                print()
            
            # Save to file
            with open('motor_groups_found.txt', 'w') as f:
                f.write("Motor Groups Found\n")
                f.write("="*50 + "\n\n")
                f.write(f"Total groups found: {len(groups)}\n")
                f.write(f"Expected motors: 15\n")
                f.write(f"Missing: {15 - len(groups)}\n\n")
                
                for group_num, info in motor_map.items():
                    f.write(f"Group {group_num}: {info['location']}\n")
                    f.write(f"  IDs: {info['ids'][0]}-{info['ids'][-1]}\n")
                    f.write(f"  Use: {info['test_id']}\n\n")
            
            print("✓ Results saved to: motor_groups_found.txt")
        
        print()
        print("="*70)
        print("  NEXT STEPS")
        print("="*70)
        print()
        
        if len(groups) < 15:
            print(f"⚠️  Found only {len(groups)} motor groups, need 15!")
            print()
            print("TO FIND MISSING MOTORS:")
            print()
            print("1. Check if motors are on different CAN bus:")
            print("   - Try scanning can0 directly")
            print("   - Try scanning can1 directly")
            print()
            print("2. Check motor power:")
            print("   - Verify all 15 motors have power")
            print("   - Check for LED indicators")
            print()
            print("3. Check CAN connections:")
            print("   - Verify CAN-H and CAN-L wiring")
            print("   - Check if all motors on same bus")
            print()
            print("4. Use Motor Studio:")
            print("   - Motor Studio can scan all buses")
            print("   - May find motors we're missing")
            print()
        else:
            print("✓ Found all expected motor groups!")
            print()
            print("NEXT: Reconfigure each motor to single ID")
            print("  - Use Motor Studio (recommended)")
            print("  - Or use configure_motor_ids.py")
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
