#!/usr/bin/env python3
"""
Activate All 15 Motors - Wake Up and Enable
Sends broadcast and individual wake-up commands to find all motors
"""
import serial
import time
import struct

PORT = '/dev/ttyUSB1'
BAUD = 921600

def send_broadcast_wake_up(ser):
    """Send broadcast wake-up commands"""
    print("Sending broadcast wake-up commands...")
    
    # Method 1: Broadcast enable (0xFF address)
    cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(cmd)
    time.sleep(0.3)
    
    # Method 2: Broadcast reset
    cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x02, 0x00, 0x0d, 0x0a])
    ser.write(cmd)
    time.sleep(0.3)
    
    # Method 3: Broadcast unlock
    cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x03, 0x00, 0x0d, 0x0a])
    ser.write(cmd)
    time.sleep(0.3)
    
    print("✓ Broadcast commands sent")

def scan_extended_range(ser, start, end):
    """Scan for motors in extended range"""
    found = []
    
    print(f"\nScanning IDs {start}-{end}...")
    
    for motor_id in range(start, end + 1):
        # Try activate command
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.15)
        
        # Read response
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        
        if len(response) > 4:
            # Verify with load params
            cmd2 = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
                         0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
            ser.reset_input_buffer()
            ser.write(cmd2)
            ser.flush()
            time.sleep(0.15)
            
            response2 = b""
            start_time = time.time()
            while time.time() - start_time < 0.25:
                if ser.in_waiting > 0:
                    response2 += ser.read(ser.in_waiting)
                    time.sleep(0.02)
            
            if len(response2) > 4:
                found.append(motor_id)
                print(f"  Found: ID {motor_id:3d} (0x{motor_id:02X})")
    
    return found

def main():
    print("="*70)
    print("  ACTIVATE ALL 15 MOTORS")
    print("="*70)
    print()
    print("This script will:")
    print("  1. Send broadcast wake-up commands")
    print("  2. Scan ALL possible ID ranges (1-255)")
    print("  3. Try to activate motors in different modes")
    print()
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"✓ Connected to {PORT} at {BAUD} baud")
        print()
    except Exception as e:
        print(f"✗ Failed to open serial port: {e}")
        return
    
    # Send wake-up commands
    send_broadcast_wake_up(ser)
    print()
    
    # Scan in chunks
    all_found = []
    
    ranges = [
        (1, 50, "Low range"),
        (51, 100, "Mid range"),
        (101, 150, "High range"),
        (151, 200, "Very high range"),
        (201, 255, "Extended range")
    ]
    
    for start, end, name in ranges:
        print(f"\n{'='*70}")
        print(f"  {name}: {start}-{end}")
        print(f"{'='*70}")
        
        found = scan_extended_range(ser, start, end)
        all_found.extend(found)
        
        if found:
            print(f"✓ Found {len(found)} motor(s) in this range")
        else:
            print(f"  No motors in this range")
    
    ser.close()
    
    # Results
    print()
    print("="*70)
    print("  RESULTS")
    print("="*70)
    print()
    print(f"Total motors found: {len(all_found)}")
    print()
    
    if all_found:
        print("Motor IDs:")
        for motor_id in all_found:
            print(f"  • ID {motor_id:3d} (0x{motor_id:02X})")
        print()
        
        # Analyze groups
        if len(all_found) > 1:
            groups = []
            current_group = [all_found[0]]
            
            for i in range(1, len(all_found)):
                if all_found[i] == all_found[i-1] + 1:
                    current_group.append(all_found[i])
                else:
                    groups.append(current_group)
                    current_group = [all_found[i]]
            groups.append(current_group)
            
            print(f"Motor groups: {len(groups)}")
            for i, group in enumerate(groups, 1):
                print(f"  Group {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
            print()
    
    print("="*70)
    print("  ANALYSIS")
    print("="*70)
    print()
    
    if len(all_found) < 15:
        estimated_motors = len([g for g in groups if len(g) >= 4]) if all_found else 0
        
        print(f"⚠️  Expected 15 motors, found {estimated_motors} motor groups")
        print()
        print("Possible reasons for missing motors:")
        print()
        print("1. **Motors in configuration mode:**")
        print("   - Need Motor Studio to activate")
        print("   - Won't respond to normal commands")
        print("   - Must be configured before use")
        print()
        print("2. **Motors at non-standard IDs:**")
        print("   - Might be at IDs > 255")
        print("   - Or using extended CAN IDs")
        print("   - Need Motor Studio to find")
        print()
        print("3. **Motors on different protocol:**")
        print("   - Some might use CANopen")
        print("   - Some might use different command format")
        print("   - Need manufacturer tool")
        print()
        print("4. **Motors not initialized:**")
        print("   - Brand new motors need initial setup")
        print("   - Must use Motor Studio first time")
        print("   - Then will respond normally")
        print()
        print("RECOMMENDATION:")
        print("  → Use Motor Studio to scan and configure all motors")
        print("  → Motor Studio can find motors in any mode")
        print("  → Can initialize new/unconfigured motors")
        print()
    else:
        print("✓ Found all expected motors!")
        print()
        print("NEXT STEP:")
        print("  → Run identify_motors_interactive.py")
        print("  → Map which ID controls which physical motor")
        print("  → Then reconfigure to single IDs")
        print()
    
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

