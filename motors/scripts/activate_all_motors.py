#!/usr/bin/env python3
"""
Activate All Motors - Try different methods to wake up/enable all motors
Since hardware is fine, motors likely need software activation/enabling
"""

import serial
import sys
import time

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0, flag=1):
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = int(0x8000 + (speed * 3283.0))
    else:
        speed_val = int(0x7fff + (speed * 3283.0))
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, flag])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.05)
        return True
    except:
        return False

def activate_motor_full_sequence(ser, can_id):
    """Full activation sequence - activate, load params, verify"""
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.3)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.3)
    return True

def test_motor_movement(ser, can_id):
    """Test if motor responds to movement command"""
    activate_motor_full_sequence(ser, can_id)
    
    send_command(ser, build_move_jog_cmd(can_id, 0.04, 1))
    time.sleep(0.6)
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
    time.sleep(0.2)
    
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.2)

def method1_activate_all_at_once(ser):
    """Method 1: Activate all motors at once (IDs 1-31)"""
    print("\nMethod 1: Activating ALL motors at once (IDs 1-31)")
    print("-" * 70)
    
    # Deactivate all first
    print("Deactivating all motors...")
    for can_id in range(1, 32):
        send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.5)
    
    # Activate all
    print("Activating all motors simultaneously...")
    for can_id in range(1, 32):
        send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.5)
    
    # Load params for all
    print("Loading parameters for all motors...")
    for can_id in range(1, 32):
        send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.5)
    
    print("[OK] Activation sequence complete")
    return True

def method2_activate_in_groups(ser):
    """Method 2: Activate motors in groups"""
    print("\nMethod 2: Activating motors in groups")
    print("-" * 70)
    
    groups = [
        (1, 7, "Group 1 (IDs 1-7)"),
        (8, 15, "Group 2 (IDs 8-15)"),
        (16, 22, "Group 3 (IDs 16-22)"),
        (23, 31, "Group 4 (IDs 23-31)"),
    ]
    
    for start, end, desc in groups:
        print(f"\nActivating {desc}...")
        for can_id in range(start, end + 1):
            send_command(ser, build_activate_cmd(can_id))
            time.sleep(0.1)
        time.sleep(0.3)
        
        print(f"Loading parameters for {desc}...")
        for can_id in range(start, end + 1):
            send_command(ser, build_load_params_cmd(can_id))
            time.sleep(0.1)
        time.sleep(0.3)
    
    print("[OK] Group activation complete")
    return True

def method3_individual_activation_with_delay(ser):
    """Method 3: Activate each motor individually with longer delays"""
    print("\nMethod 3: Individual activation with extended delays")
    print("-" * 70)
    
    for can_id in range(1, 32):
        print(f"Activating ID {can_id}...", end=' ', flush=True)
        send_command(ser, build_activate_cmd(can_id))
        time.sleep(0.5)  # Longer delay
        
        send_command(ser, build_load_params_cmd(can_id))
        time.sleep(0.5)  # Longer delay
        
        print("OK")
    
    print("[OK] Individual activation complete")
    return True

def method4_broadcast_enable(ser):
    """Method 4: Try broadcast/enable all command (if supported)"""
    print("\nMethod 4: Attempting broadcast enable (ID 0 or 0xFF)")
    print("-" * 70)
    
    # Try ID 0 (broadcast)
    broadcast_cmds = [
        bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00, 0x01, 0x00, 0x0d, 0x0a]),  # Activate ID 0
        bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0xFF, 0x01, 0x00, 0x0d, 0x0a]),  # Activate ID 255
    ]
    
    for cmd in broadcast_cmds:
        print(f"Trying broadcast command: {cmd.hex(' ')}")
        send_command(ser, cmd)
        time.sleep(0.5)
    
    print("[OK] Broadcast commands sent")
    return True

def test_after_activation(ser):
    """Test motors after activation attempts"""
    print("\n" + "="*70)
    print("TESTING MOTORS AFTER ACTIVATION")
    print("="*70)
    
    print("\nTesting various CAN IDs to see which motors respond...")
    print("Watch for movements from motors that weren't moving before!")
    
    input("\nPress Enter to start testing...")
    
    test_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    responses = {}
    
    for can_id in test_ids:
        print(f"\nTesting CAN ID {can_id} (0x{can_id:02X})...")
        test_motor_movement(ser, can_id)
        
        motor_info = input("Which physical motor(s) moved? (1-15, 'none', 'same'): ").strip().lower()
        responses[can_id] = motor_info
    
    # Count unique motors
    unique_motors = set()
    for motor_info in responses.values():
        if motor_info and motor_info != 'none' and motor_info != 'same':
            try:
                unique_motors.add(int(motor_info))
            except:
                pass
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\nUnique motors responding: {len(unique_motors)}")
    if unique_motors:
        print(f"Motor numbers: {sorted(unique_motors)}")
    
    if len(unique_motors) > 2:
        print("\n[SUCCESS] More motors are responding!")
        print("Activation method worked!")
    elif len(unique_motors) == 2:
        print("\n[NO CHANGE] Still only 2 motors responding")
        print("Activation methods didn't enable additional motors")
    else:
        print("\n[WARNING] Fewer motors responding than before")
    
    return responses

def main():
    port = "COM3"
    baud = 921600
    
    print("="*70)
    print("ACTIVATE ALL MOTORS - Software Activation Methods")
    print("="*70)
    print("\nThis script tries different software methods to activate/enable")
    print("all motors, since hardware is confirmed working.")
    print("\nMethods to try:")
    print("  1. Activate all motors at once")
    print("  2. Activate motors in groups")
    print("  3. Individual activation with delays")
    print("  4. Broadcast enable commands")
    
    input("\nPress Enter to start...")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened")
        
        # Try each activation method
        methods = [
            ("Activate All at Once", method1_activate_all_at_once),
            ("Activate in Groups", method2_activate_in_groups),
            ("Individual with Delays", method3_individual_activation_with_delay),
            ("Broadcast Enable", method4_broadcast_enable),
        ]
        
        for method_name, method_func in methods:
            print(f"\n{'='*70}")
            print(f"Trying: {method_name}")
            print(f"{'='*70}")
            method_func(ser)
            time.sleep(1.0)
        
        # Test after all activation methods
        test_after_activation(ser)
        
        print("\n" + "="*70)
        print("ACTIVATION ATTEMPTS COMPLETE")
        print("="*70)
        print("\nIf more motors are now responding, the activation worked!")
        print("If still only 2 motors, they may need:")
        print("  - Different activation command format")
        print("  - Motor-specific initialization sequence")
        print("  - Configuration/enable via motor software")
        print("  - Hardware enable switches/buttons")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

