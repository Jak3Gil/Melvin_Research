#!/usr/bin/env python3
"""
Test Individual CAN IDs with Detailed Observation
Tests each ID one at a time to see which physical motors respond
Focuses on the problematic ranges (67-79, 73, etc.)
"""

import serial
import sys
import time

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0):
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = int(0x8000 + (speed * 3283.0))
    else:
        speed_val = int(0x7fff + (speed * 3283.0))
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, 1])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.1)
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.3:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        return len(response) > 4
    except:
        return False

def test_single_id(ser, can_id):
    """Test a single CAN ID with proper cleanup"""
    # Activate
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.3)
    
    # Load params
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.3)
    
    # Forward
    send_command(ser, build_move_jog_cmd(can_id, 0.1))
    time.sleep(1.0)
    
    # Stop
    send_command(ser, build_move_jog_cmd(can_id, 0.0))
    time.sleep(0.5)
    
    # Backward
    send_command(ser, build_move_jog_cmd(can_id, -0.1))
    time.sleep(1.0)
    
    # Stop and deactivate
    send_command(ser, build_move_jog_cmd(can_id, 0.0))
    time.sleep(0.5)
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.5)

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    start_id = int(sys.argv[3]) if len(sys.argv) > 3 else 64
    end_id = int(sys.argv[4]) if len(sys.argv) > 4 else 80
    
    print("="*70)
    print("Individual CAN ID Testing")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud Rate: {baud}")
    print(f"Testing CAN IDs: {start_id} to {end_id}")
    print("\nThis will test each ID individually")
    print("Watch which PHYSICAL motors move for each ID!")
    print("="*70)
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("\n[OK] Serial port opened\n")
    
    # First, activate all IDs in range (like the successful sequence)
    print("Step 1: Activating all IDs in range first...")
    for can_id in range(start_id, end_id + 1):
        send_command(ser, build_activate_cmd(can_id))
        time.sleep(0.05)
    
    time.sleep(0.5)
    
    print("Step 2: Loading params on all IDs...")
    for can_id in range(start_id, end_id + 1):
        send_command(ser, build_load_params_cmd(can_id))
        time.sleep(0.05)
    
    time.sleep(1.0)
    print("\n[OK] Pre-activation complete\n")
    
    # Now test each ID individually
    mapping = {}
    
    for can_id in range(start_id, end_id + 1):
        print(f"\n{'='*70}")
        print(f"Testing CAN ID {can_id} (0x{can_id:02X})")
        print(f"{'='*70}")
        print("Watch which physical motor(s) move...")
        print("(This motor will move forward then backward)")
        input("Press Enter to test this ID...")
        
        test_single_id(ser, can_id)
        
        print("\nWhich physical motor(s) moved?")
        print("  Enter motor number(s): 1, 2, 3, etc.")
        print("  If multiple motors: 8,9")
        print("  If none: none")
        
        response = input("Motor(s): ").strip().lower()
        
        if response == 'none':
            mapping[can_id] = []
        else:
            try:
                motors = [int(x.strip()) for x in response.split(',')]
                mapping[can_id] = motors
                print(f"  [OK] CAN ID {can_id} controls: {motors}")
            except:
                mapping[can_id] = []
                print(f"  [SKIP] Invalid input for CAN ID {can_id}")
        
        time.sleep(0.5)
    
    # Results
    print("\n" + "="*70)
    print("DETAILED MAPPING RESULTS")
    print("="*70)
    
    print("\nBy CAN ID:")
    for can_id in sorted(mapping.keys()):
        motors = mapping[can_id]
        if motors:
            print(f"  CAN ID {can_id:3d} (0x{can_id:02X}): Motor(s) {motors}")
        else:
            print(f"  CAN ID {can_id:3d} (0x{can_id:02X}): No motor")
    
    # Group by motor
    motor_to_ids = {}
    for can_id, motors in mapping.items():
        for motor in motors:
            if motor not in motor_to_ids:
                motor_to_ids[motor] = []
            motor_to_ids[motor].append(can_id)
    
    print("\nBy Physical Motor:")
    for motor in sorted(motor_to_ids.keys()):
        ids = sorted(motor_to_ids[motor])
        print(f"  Motor {motor}: CAN IDs {ids}")
    
    ser.close()
    print("\n[OK] Test complete")

if __name__ == '__main__':
    main()

