#!/usr/bin/env python3
"""
Investigate why 10 motors are missing
Tests various hypotheses about why motors aren't responding
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

def build_detect_cmd():
    return bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])  # AT+AT

def send_command(ser, cmd, timeout=0.3):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.05)
        response = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.01)
        return len(response) > 4, response
    except:
        return False, b""

def test_hypothesis_1_daisy_chain_order(ser):
    """Hypothesis 1: Motors need to be activated in physical daisy-chain order"""
    print("="*70)
    print("HYPOTHESIS 1: Daisy-Chain Physical Order")
    print("="*70)
    print("Testing if motors need activation in physical order...")
    print("Activating known motors first, then testing gaps...\n")
    
    # Deactivate all
    for can_id in range(1, 256):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.05)
        time.sleep(0.001)
    time.sleep(0.5)
    
    # Activate known motors in order: 1, 2, 3, 4, 8
    print("Step 1: Activating known motors in sequence...")
    known_motor_ranges = [
        (1, 15, "Motor 1"),
        (16, 20, "Motor 2"),
        (21, 30, "Motor 3"),
        (31, 39, "Motor 4"),
    ]
    
    for start, end, name in known_motor_ranges:
        print(f"  Activating {name} (IDs {start}-{end})...")
        for can_id in range(start, end + 1):
            send_command(ser, build_activate_cmd(can_id), timeout=0.05)
            time.sleep(0.01)
            send_command(ser, build_load_params_cmd(can_id), timeout=0.05)
            time.sleep(0.01)
        time.sleep(0.2)
    
    print("\nStep 2: Testing gaps between known motors...")
    gap_ranges = [
        (40, 63, "Between Motor 4 and Motor 8"),
        (80, 100, "After Motor 8"),
    ]
    
    for start, end, desc in gap_ranges:
        print(f"\n  Testing {desc} (IDs {start}-{end})...")
        found = []
        for can_id in range(start, end + 1):
            has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.15)
            if has_resp:
                found.append(can_id)
            time.sleep(0.05)
        if found:
            print(f"    [FOUND] {len(found)} IDs: {found}")
        else:
            print(f"    [NOT FOUND] No responses")

def test_hypothesis_2_power_state(ser):
    """Hypothesis 2: Missing motors need power cycle or different power state"""
    print("\n" + "="*70)
    print("HYPOTHESIS 2: Power State Issues")
    print("="*70)
    print("Testing if missing motors need different power state...\n")
    
    # Try activating ALL IDs 1-255 slowly to wake up all motors
    print("Activating ALL IDs 1-255 slowly (power-up sequence)...")
    for can_id in range(1, 256):
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.05)
        if can_id % 50 == 0:
            print(f"  Progress: {can_id}/255")
    
    time.sleep(1.0)
    
    print("\nLoading params for ALL IDs...")
    for can_id in range(1, 256):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.05)
        if can_id % 50 == 0:
            print(f"  Progress: {can_id}/255")
    
    time.sleep(1.0)
    
    print("\nTesting which IDs respond after full activation...")
    responding = []
    for can_id in range(1, 256):
        has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.15)
        if has_resp:
            responding.append(can_id)
        time.sleep(0.02)
        if can_id % 50 == 0:
            print(f"  Progress: {can_id}/255 ({len(responding)} found so far)")
    
    print(f"\nTotal responding IDs: {len(responding)}")
    if len(responding) > 48:  # More than the ~48 we found before
        print("[SUCCESS] More motors found with slow activation!")
    else:
        print("[FAIL] Same number of motors found")

def test_hypothesis_3_broadcast(ser):
    """Hypothesis 3: Missing motors respond to broadcast (ID 0)"""
    print("\n" + "="*70)
    print("HYPOTHESIS 3: Broadcast Commands (ID 0)")
    print("="*70)
    print("Testing if motors respond to broadcast ID 0...\n")
    
    # Try broadcast activation (ID 0)
    print("Sending broadcast activate (ID 0)...")
    has_resp, resp = send_command(ser, build_activate_cmd(0), timeout=0.5)
    print(f"  Response: {has_resp} (len: {len(resp)})")
    
    time.sleep(0.5)
    
    # Try AT+AT detect command
    print("\nSending AT+AT detect command...")
    has_resp, resp = send_command(ser, build_detect_cmd(), timeout=0.5)
    print(f"  Response: {has_resp}, Data: {resp.hex(' ') if resp else 'none'}")

def test_hypothesis_4_individual_activation(ser):
    """Hypothesis 4: Each missing motor needs individual slow activation"""
    print("\n" + "="*70)
    print("HYPOTHESIS 4: Individual Slow Activation")
    print("="*70)
    print("Activating each ID individually with longer delays...\n")
    
    # Deactivate all
    for can_id in range(1, 256):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.05)
        time.sleep(0.001)
    time.sleep(1.0)
    
    # Test IDs in gaps individually
    test_ids = list(range(40, 64)) + list(range(80, 101))
    
    print(f"Testing {len(test_ids)} IDs individually...")
    found = []
    
    for can_id in test_ids:
        print(f"  Testing ID {can_id:3d}...", end='', flush=True)
        
        # Slow individual activation
        send_command(ser, build_activate_cmd(can_id), timeout=0.2)
        time.sleep(0.3)
        send_command(ser, build_load_params_cmd(can_id), timeout=0.2)
        time.sleep(0.3)
        
        # Test response
        has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.3)
        if has_resp:
            found.append(can_id)
            print(" [FOUND]")
        else:
            print(" [NO]")
        
        time.sleep(0.2)
    
    if found:
        print(f"\n[SUCCESS] Found {len(found)} IDs: {found}")
    else:
        print(f"\n[FAIL] No additional IDs found with individual activation")

def test_hypothesis_5_physical_disconnection(ser):
    """Hypothesis 5: Missing motors might be physically disconnected"""
    print("\n" + "="*70)
    print("HYPOTHESIS 5: Physical Connection Check")
    print("="*70)
    print("Testing if daisy-chain might be broken...\n")
    
    # If motors are daisy-chained, activating motors beyond a break won't work
    # Test if we can activate motors sequentially and see where chain breaks
    
    print("Testing sequential activation to find chain breaks...")
    
    # Activate all known working motors first
    print("Step 1: Activating known working motors...")
    for can_id in range(1, 40):
        send_command(ser, build_activate_cmd(can_id), timeout=0.05)
        time.sleep(0.01)
        send_command(ser, build_load_params_cmd(can_id), timeout=0.05)
        time.sleep(0.01)
    time.sleep(0.5)
    
    # Now try to activate IDs beyond
    print("\nStep 2: Testing if motors beyond ID 40 can be activated...")
    beyond_ids = list(range(40, 100))
    
    found_beyond = []
    for can_id in beyond_ids:
        has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.15)
        if has_resp:
            found_beyond.append(can_id)
        time.sleep(0.05)
    
    if found_beyond:
        print(f"  [OK] Found {len(found_beyond)} IDs beyond 40: {found_beyond[:10]}...")
    else:
        print("  [WARNING] No IDs found beyond 40 - possible daisy-chain break!")

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("Missing Motors Investigation")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}")
    print("\nTesting hypotheses about why 10 motors are missing...")
    print("Known: 5 motors found (Motors 1, 2, 3, 4, 8)")
    print("Missing: 10 motors")
    print("="*70)
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("\n[OK] Serial port opened\n")
    
    test_hypothesis_1_daisy_chain_order(ser)
    test_hypothesis_2_power_state(ser)
    test_hypothesis_3_broadcast(ser)
    test_hypothesis_4_individual_activation(ser)
    test_hypothesis_5_physical_disconnection(ser)
    
    print("\n" + "="*70)
    print("INVESTIGATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Check physical connections on daisy-chain")
    print("  2. Verify all motors are powered")
    print("  3. Check if motors need hardware ID configuration")
    print("  4. Verify CAN bus termination")
    print("  5. Check motor firmware version")
    
    ser.close()
    print("\n[OK] Investigation complete")

if __name__ == '__main__':
    main()

