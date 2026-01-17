#!/usr/bin/env python3
"""
Replicate the sequence that made Motor 3 appear:
1. Activate ALL CAN IDs (1-31) rapidly
2. Load params on ALL IDs
3. Test each ID individually to see which motors respond
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
            print(f"    Response: {response.hex(' ')}")
        return len(response) > 4
    except:
        return False

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("Activate All Motors Then Test")
    print("="*70)
    print("\nReplicating the sequence that made Motor 3 appear:")
    print("1. Rapidly activate ALL CAN IDs (1-31)")
    print("2. Load params on ALL IDs")
    print("3. Test each ID to see which motors respond")
    print("="*70)
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("\n[OK] Serial port opened\n")
    
    # Step 1: Activate ALL IDs rapidly
    print("Step 1: Activating ALL CAN IDs (1-31)...")
    for can_id in range(1, 32):
        send_command(ser, build_activate_cmd(can_id))
        time.sleep(0.02)  # Very short delay
    
    time.sleep(0.5)
    print("  [DONE] All IDs activated")
    
    # Step 2: Load params on ALL IDs
    print("\nStep 2: Loading params on ALL CAN IDs...")
    for can_id in range(1, 32):
        send_command(ser, build_load_params_cmd(can_id))
        time.sleep(0.02)
    
    time.sleep(0.5)
    print("  [DONE] Params loaded on all IDs")
    
    # Step 3: Send AT+AT detection (this seemed to change behavior)
    print("\nStep 3: Sending AT+AT detection command...")
    detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
    ser.write(detect_cmd)
    ser.flush()
    time.sleep(0.5)
    response = ser.read(ser.in_waiting)
    if response:
        print(f"  Detection response: {response.hex(' ')}")
    
    # Step 4: Test each ID with movement
    print("\nStep 4: Testing each CAN ID with movement...")
    print("Watch which physical motors move!\n")
    
    found = []
    for can_id in range(1, 32):
        print(f"Testing CAN ID {can_id} (0x{can_id:02X})...", end='', flush=True)
        
        # Try to activate and move
        if send_command(ser, build_activate_cmd(can_id)):
            time.sleep(0.2)
            send_command(ser, build_load_params_cmd(can_id))
            time.sleep(0.2)
            
            # Small movement
            send_command(ser, build_move_jog_cmd(can_id, 0.08))
            time.sleep(0.5)
            send_command(ser, build_move_jog_cmd(can_id, 0.0))
            time.sleep(0.3)
            
            send_command(ser, build_deactivate_cmd(can_id))
            found.append(can_id)
            print(" ✓ Motor responded")
        else:
            print(" - No response")
        
        time.sleep(0.2)
    
    # Summary
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\nCAN IDs that responded: {found}")
    print(f"Total: {len(found)} motors")
    
    if len(found) > 2:
        print(f"\n[SUCCESS] Found more than 2 motors!")
    else:
        print(f"\n[LIMITED] Only found {len(found)} motors")
    
    ser.close()
    print("\n[OK] Test complete")

if __name__ == '__main__':
    main()

