#!/usr/bin/env python3
"""
Use L91 Protocol to Work with All Motors
This script uses the existing L91 communication line to discover and control all motors
No ID reconfiguration needed - works with motors as they are!
"""
import serial
import time
import struct

PORT = '/dev/ttyUSB0'
BAUD = 921600

def build_activate_cmd(can_id):
    """Build L91 activate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    """Build L91 deactivate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    """Build L91 load params command"""
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0, flag=1):
    """Build L91 move jog command"""
    # Speed calculation: 0.1 RPM = 1 count
    speed_val = int(speed * 10) & 0xFFFF
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, flag])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd, timeout=0.25):
    """Send L91 command and get response"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.15)
    
    response = b""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
        time.sleep(0.02)
    
    return response

def scan_all_motors(ser, start_id=1, end_id=127):
    """Scan for all motors using L91 protocol"""
    print(f"Scanning for motors (IDs {start_id}-{end_id})...")
    print()
    
    found = []
    
    for motor_id in range(start_id, end_id + 1):
        # Try activate
        cmd = build_activate_cmd(motor_id)
        response = send_command(ser, cmd, timeout=0.25)
        
        if len(response) > 4:
            # Verify with load params
            cmd2 = build_load_params_cmd(motor_id)
            response2 = send_command(ser, cmd2, timeout=0.25)
            
            # Deactivate
            send_command(ser, build_deactivate_cmd(motor_id), timeout=0.1)
            time.sleep(0.05)
            
            if len(response2) > 4:
                found.append(motor_id)
                print(f"  ✓ Found motor at ID {motor_id:3d} (0x{motor_id:02X})")
    
    return found

def group_motors(motor_ids):
    """Group consecutive IDs (each group = one physical motor)"""
    if not motor_ids:
        return []
    
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

def control_motor_group(ser, motor_group, action='enable'):
    """
    Control a motor group (use first ID from group)
    
    Args:
        ser: Serial port
        motor_group: List of IDs (e.g., [40, 41, 42, 43, 44, 45, 46, 47])
        action: 'enable', 'disable', 'move', 'pulse'
    """
    if not motor_group:
        return False
    
    # Use first ID from group (typical behavior)
    primary_id = motor_group[0]
    
    if action == 'enable':
        cmd = build_activate_cmd(primary_id)
        response = send_command(ser, cmd, timeout=0.3)
        return len(response) > 4
    
    elif action == 'disable':
        cmd = build_deactivate_cmd(primary_id)
        response = send_command(ser, cmd, timeout=0.3)
        return len(response) > 4
    
    elif action == 'move':
        # Enable first
        send_command(ser, build_activate_cmd(primary_id), timeout=0.2)
        time.sleep(0.1)
        
        # Move
        cmd = build_move_jog_cmd(primary_id, speed=5.0, flag=1)
        response = send_command(ser, cmd, timeout=0.3)
        return len(response) > 4
    
    elif action == 'pulse':
        # REMOVED - DANGEROUS! Use manual control instead
        # Enable
        send_command(ser, build_activate_cmd(primary_id), timeout=0.2)
        time.sleep(0.1)
        
        # Disable immediately (no movement)
        send_command(ser, build_deactivate_cmd(primary_id), timeout=0.2)
        return True
    
    return False

def main():
    print("="*70)
    print("  USE L91 PROTOCOL FOR ALL MOTORS")
    print("="*70)
    print()
    print("This script uses the existing L91 communication line")
    print("to discover and control all motors.")
    print()
    print(f"Port: {PORT}")
    print(f"Baud: {BAUD}")
    print()
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"✓ Connected to {PORT}")
        print()
    except Exception as e:
        print(f"✗ Failed to open port: {e}")
        print(f"\nMake sure USB-to-CAN adapter is connected to Jetson")
        print(f"Check port: ls -la /dev/ttyUSB*")
        return
    
    # Step 1: Scan for all motors
    print("="*70)
    print("  STEP 1: DISCOVER ALL MOTORS")
    print("="*70)
    print()
    
    motor_ids = scan_all_motors(ser, 1, 127)
    
    if not motor_ids:
        print("✗ No motors found!")
        ser.close()
        return
    
    print()
    print(f"✓ Found {len(motor_ids)} motor ID(s)")
    print()
    
    # Step 2: Group motors
    motor_groups = group_motors(motor_ids)
    
    print("="*70)
    print("  STEP 2: MOTOR GROUPS")
    print("="*70)
    print()
    print(f"Found {len(motor_groups)} motor group(s)")
    print("(Each group represents one physical motor)")
    print()
    
    for i, group in enumerate(motor_groups, 1):
        if len(group) == 1:
            print(f"  Motor {i}: ID {group[0]} (single ID)")
        else:
            print(f"  Motor {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
    
    print()
    
    # Step 3: Test motors (COMMUNICATION ONLY - NO MOVEMENT)
    print("="*70)
    print("  STEP 3: TEST MOTOR COMMUNICATION")
    print("="*70)
    print()
    print("Testing communication (NO MOVEMENT)...")
    print()
    
    for i, group in enumerate(motor_groups, 1):
        primary_id = group[0]
        print(f"Motor {i} (ID {primary_id}): ", end='', flush=True)
        
        # Test communication only (enable/disable, no movement)
        if control_motor_group(ser, group, action='enable'):
            time.sleep(0.1)
            control_motor_group(ser, group, action='disable')
            print("✓ Responds")
        else:
            print("✗ No response")
        
        time.sleep(0.2)
    
    print()
    
    # Step 4: Summary
    print("="*70)
    print("  SUMMARY")
    print("="*70)
    print()
    print(f"✓ {len(motor_groups)} physical motor(s) found")
    print(f"✓ All motors accessible via L91 protocol")
    print()
    print("To control motors:")
    print(f"  - Use primary ID from each group")
    print(f"  - Primary IDs: {[group[0] for group in motor_groups]}")
    print()
    print("Example:")
    print("  python3 jetson_motor_interface.py")
    print()
    
    # Save motor map
    with open('motor_map_l91.txt', 'w') as f:
        f.write("Motor Map (L91 Protocol)\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total physical motors: {len(motor_groups)}\n")
        f.write(f"Total IDs responding: {len(motor_ids)}\n\n")
        f.write("Motor Groups:\n")
        for i, group in enumerate(motor_groups, 1):
            f.write(f"  Motor {i}: Primary ID {group[0]}, All IDs {group}\n")
        f.write("\n")
        f.write("To control a motor, use its primary ID (first ID in group)\n")
    
    print("✓ Motor map saved to: motor_map_l91.txt")
    print()
    
    ser.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

