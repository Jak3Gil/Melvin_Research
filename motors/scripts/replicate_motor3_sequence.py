#!/usr/bin/env python3
"""
Replicate Exact Method 3 Sequence That Made Motor 3 Appear
This script replicates the exact sequence step-by-step and logs what happens
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

def send_command(ser, cmd, show_response=False):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.05)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.3:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        
        if show_response and response:
            return response.hex(' ')
        return len(response) > 4
    except:
        return False

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("Replicate Method 3 Sequence - Step by Step")
    print("="*70)
    print("\nThis will replicate the EXACT sequence that made Motor 3 appear")
    print("Watch which physical motors move at each step!\n")
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("[OK] Serial port opened\n")
    
    # STEP 1: Rapidly activate ALL IDs (1-31) - This is the key step
    print("="*70)
    print("STEP 1: Rapidly Activating ALL CAN IDs (1-31)")
    print("="*70)
    print("Watch which motors move during this activation sequence...\n")
    
    print("Activating IDs 1-31 rapidly (0.05s delays)...")
    for can_id in range(1, 32):
        send_command(ser, build_activate_cmd(can_id))
        time.sleep(0.05)  # Small delay between activations
        if can_id % 5 == 0:
            print(f"  Activated IDs 1-{can_id}...")
    
    print("\n[STEP 1 COMPLETE]")
    print("  Note: Watch which motors moved during activation sequence")
    time.sleep(1.0)
    
    # STEP 2: Load params on ALL IDs
    print("\n" + "="*70)
    print("STEP 2: Loading Parameters on ALL CAN IDs (1-31)")
    print("="*70)
    print("Loading params on all IDs...\n")
    
    for can_id in range(1, 32):
        send_command(ser, build_load_params_cmd(can_id))
        time.sleep(0.05)
        if can_id % 10 == 0:
            print(f"  Loaded params on IDs 1-{can_id}...")
    
    print("\n[STEP 2 COMPLETE]")
    time.sleep(1.0)
    
    # STEP 3: Test each ID individually with movement
    print("\n" + "="*70)
    print("STEP 3: Testing Each CAN ID with Movement")
    print("="*70)
    print("Testing each ID sequentially - watch which motors move!\n")
    
    motor_mapping = {}
    print("Starting tests in 2 seconds...")
    time.sleep(2.0)
    
    for can_id in range(1, 32):
        print(f"Testing CAN ID {can_id} (0x{can_id:02X})...", end='', flush=True)
        
        # Send activate again
        send_command(ser, build_activate_cmd(can_id))
        time.sleep(0.2)
        
        # Small forward movement
        send_command(ser, build_move_jog_cmd(can_id, 0.08))
        time.sleep(0.6)
        
        # Stop
        send_command(ser, build_move_jog_cmd(can_id, 0.0))
        time.sleep(0.3)
        
        # Small backward movement
        send_command(ser, build_move_jog_cmd(can_id, -0.08))
        time.sleep(0.6)
        
        # Stop
        send_command(ser, build_move_jog_cmd(can_id, 0.0))
        time.sleep(0.3)
        
        # Check if motor responded
        response = send_command(ser, build_activate_cmd(can_id))
        motor_mapping[can_id] = "responded" if response else "no_response"
        print(" ✓" if response else " -")
        
        time.sleep(0.2)
    
    # Cleanup - deactivate all
    print("\n" + "="*70)
    print("CLEANUP: Deactivating All Motors")
    print("="*70)
    for can_id in range(1, 32):
        send_command(ser, build_deactivate_cmd(can_id))
        time.sleep(0.02)
    
    # Results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    responding_ids = [can_id for can_id, status in motor_mapping.items() if status == "responded"]
    
    print(f"\nCAN IDs that responded: {len(responding_ids)}")
    print(f"Responding IDs: {responding_ids}")
    
    print(f"\nCAN IDs that did NOT respond: {len(motor_mapping) - len(responding_ids)}")
    non_responding = [can_id for can_id, status in motor_mapping.items() if status == "no_response"]
    print(f"Non-responding IDs: {non_responding}")
    
    print("\n" + "="*70)
    print("OBSERVATION REQUIRED")
    print("="*70)
    print("\nPlease observe which PHYSICAL motors moved during this sequence:")
    print("  - During Step 1 (rapid activation): Which motors moved?")
    print("  - During Step 2 (load params): Which motors moved?")
    print("  - During Step 3 (individual tests): Which motors moved for each ID?")
    print("\nThis will help identify which CAN IDs control which physical motors.")
    
    ser.close()
    print("\n[OK] Sequence complete")

if __name__ == '__main__':
    main()

