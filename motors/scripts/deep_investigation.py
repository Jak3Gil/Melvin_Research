#!/usr/bin/env python3
"""
Deep Investigation - Multiple strategies to find all motors
Tests various hypotheses about missing motors
"""

import serial
import sys
import time
import subprocess

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

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

def strategy_1_selective_gaps(ser):
    """Strategy 1: Activate only gap ranges (0-7, 40-63)"""
    print("\n" + "="*70)
    print("STRATEGY 1: Selective Gap Activation")
    print("="*70)
    print("Activating ONLY gap ranges (0-7, 40-63) to wake up missing motors...\n")
    
    # Deactivate all first
    for can_id in range(0, 256):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.05)
        time.sleep(0.001)
    time.sleep(0.5)
    
    # Activate ONLY gaps
    gap_ranges = [
        (0, 7, "IDs 0-7"),
        (40, 63, "IDs 40-63"),
    ]
    
    for start, end, desc in gap_ranges:
        print(f"  Activating {desc}...")
        for can_id in range(start, end + 1):
            send_command(ser, build_activate_cmd(can_id), timeout=0.05)
            time.sleep(0.01)
        time.sleep(0.2)
        
        for can_id in range(start, end + 1):
            send_command(ser, build_load_params_cmd(can_id), timeout=0.05)
            time.sleep(0.01)
        time.sleep(0.2)
    
    # Test what responds
    print("\n  Testing all IDs...")
    responding = []
    for can_id in range(0, 256):
        has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.15)
        if has_resp:
            responding.append(can_id)
        time.sleep(0.02)
        if can_id % 50 == 0:
            print(f"    Progress: {can_id}/255 ({len(responding)} found)")
    
    print(f"\n  Found {len(responding)} responding IDs")
    return responding

def strategy_2_reverse_order(ser):
    """Strategy 2: Activate in reverse order (255 down to 0)"""
    print("\n" + "="*70)
    print("STRATEGY 2: Reverse Order Activation")
    print("="*70)
    print("Activating IDs in reverse order (255→0)...\n")
    
    # Deactivate all
    for can_id in range(0, 256):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.05)
        time.sleep(0.001)
    time.sleep(0.5)
    
    # Activate in reverse
    print("  Activating IDs 255→0...")
    for can_id in range(255, -1, -1):
        send_command(ser, build_activate_cmd(can_id), timeout=0.05)
        time.sleep(0.01)
        if can_id % 50 == 0:
            print(f"    Progress: {can_id}/0")
    time.sleep(0.3)
    
    for can_id in range(255, -1, -1):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.05)
        time.sleep(0.01)
    time.sleep(0.3)
    
    # Test
    print("  Testing all IDs...")
    responding = []
    for can_id in range(0, 256):
        has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.15)
        if has_resp:
            responding.append(can_id)
        time.sleep(0.02)
    
    print(f"  Found {len(responding)} responding IDs")
    return responding

def strategy_3_powers_of_two(ser):
    """Strategy 3: Activate powers of 2 first, then fill in"""
    print("\n" + "="*70)
    print("STRATEGY 3: Powers of 2 Activation")
    print("="*70)
    print("Activating powers of 2 first, then filling in...\n")
    
    # Deactivate all
    for can_id in range(0, 256):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.05)
        time.sleep(0.001)
    time.sleep(0.5)
    
    # Powers of 2: 1, 2, 4, 8, 16, 32, 64, 128
    powers = [2**i for i in range(8)]
    print(f"  Activating powers of 2: {powers}...")
    for can_id in powers:
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.1)
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.1)
    time.sleep(0.5)
    
    # Then activate all
    print("  Activating all remaining IDs...")
    for can_id in range(0, 256):
        if can_id not in powers:
            send_command(ser, build_activate_cmd(can_id), timeout=0.05)
            time.sleep(0.01)
    time.sleep(0.3)
    
    for can_id in range(0, 256):
        if can_id not in powers:
            send_command(ser, build_load_params_cmd(can_id), timeout=0.05)
            time.sleep(0.01)
    time.sleep(0.3)
    
    # Test
    responding = []
    for can_id in range(0, 256):
        has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.15)
        if has_resp:
            responding.append(can_id)
        time.sleep(0.02)
    
    print(f"  Found {len(responding)} responding IDs")
    return responding

def strategy_4_slow_individual(ser):
    """Strategy 4: Slow individual activation with long delays"""
    print("\n" + "="*70)
    print("STRATEGY 4: Slow Individual Activation")
    print("="*70)
    print("Activating each ID individually with long delays...\n")
    
    # Deactivate all
    for can_id in range(0, 256):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.05)
        time.sleep(0.001)
    time.sleep(1.0)
    
    print("  Activating each ID individually (slow)...")
    responding = []
    
    for can_id in range(0, 256):
        # Individual slow activation
        send_command(ser, build_activate_cmd(can_id), timeout=0.2)
        time.sleep(0.2)
        send_command(ser, build_load_params_cmd(can_id), timeout=0.2)
        time.sleep(0.2)
        
        # Test immediately after activation
        has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.3)
        if has_resp:
            responding.append(can_id)
            print(f"    ID {can_id:3d}: ✓")
        
        time.sleep(0.1)
        
        if can_id % 50 == 0:
            print(f"    Progress: {can_id}/255 ({len(responding)} found)")
    
    print(f"  Found {len(responding)} responding IDs")
    return responding

def strategy_5_higher_bitrates(ser):
    """Strategy 5: Try different baud rates"""
    print("\n" + "="*70)
    print("STRATEGY 5: Different Baud Rates")
    print("="*70)
    print("Testing if different baud rates reveal more motors...\n")
    
    baud_rates = [115200, 460800, 921600, 1000000]
    results = {}
    
    for baud in baud_rates:
        print(f"  Testing {baud} baud...")
        try:
            # Close and reopen at new baud rate
            ser.close()
            time.sleep(0.5)
            new_ser = serial.Serial(ser.port, baud, timeout=0.1)
            time.sleep(0.5)
            
            # Rapid activation
            for can_id in range(0, 100):
                send_command(new_ser, build_activate_cmd(can_id), timeout=0.05)
                time.sleep(0.01)
            time.sleep(0.2)
            
            for can_id in range(0, 100):
                send_command(new_ser, build_load_params_cmd(can_id), timeout=0.05)
                time.sleep(0.01)
            time.sleep(0.2)
            
            # Test sample IDs
            found = []
            for can_id in [0, 1, 2, 8, 40, 41, 42, 64, 100]:
                has_resp, _ = send_command(new_ser, build_activate_cmd(can_id), timeout=0.15)
                if has_resp:
                    found.append(can_id)
            
            results[baud] = found
            print(f"    Found IDs: {found}")
            
            new_ser.close()
            # Reopen at original baud
            ser.open()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Error: {e}")
            results[baud] = []
    
    return results

def strategy_6_broadcast_commands(ser):
    """Strategy 6: Test broadcast commands (ID 0, 255)"""
    print("\n" + "="*70)
    print("STRATEGY 6: Broadcast Commands")
    print("="*70)
    print("Testing broadcast IDs (0, 255) and special commands...\n")
    
    # Deactivate all first
    for can_id in range(0, 256):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.05)
        time.sleep(0.001)
    time.sleep(0.5)
    
    # Test broadcast ID 0
    print("  Testing broadcast ID 0...")
    send_command(ser, build_activate_cmd(0), timeout=0.5)
    time.sleep(0.5)
    send_command(ser, build_load_params_cmd(0), timeout=0.5)
    time.sleep(0.5)
    
    # Test ID 255
    print("  Testing ID 255...")
    send_command(ser, build_activate_cmd(255), timeout=0.5)
    time.sleep(0.5)
    send_command(ser, build_load_params_cmd(255), timeout=0.5)
    time.sleep(0.5)
    
    # Test AT+AT detect command
    print("  Testing AT+AT detect...")
    detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
    has_resp, resp = send_command(ser, detect_cmd, timeout=0.5)
    if has_resp:
        print(f"    Response: {resp.hex(' ')}")
    else:
        print("    No response")
    
    # Test all IDs after broadcast
    print("\n  Testing all IDs after broadcast...")
    responding = []
    for can_id in range(0, 256):
        has_resp, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.15)
        if has_resp:
            responding.append(can_id)
        time.sleep(0.02)
    
    print(f"  Found {len(responding)} responding IDs")
    return responding

def strategy_7_can_interface_setup():
    """Strategy 7: Try setting up CAN interface from USB adapter"""
    print("\n" + "="*70)
    print("STRATEGY 7: CAN Interface Setup")
    print("="*70)
    print("Trying to setup slcan0 from /dev/ttyUSB0...\n")
    
    # Stop existing
    subprocess.run("sudo pkill slcand", shell=True, capture_output=True)
    subprocess.run("sudo ip link set slcan0 down", shell=True, capture_output=True)
    time.sleep(1)
    
    # Try different bitrates
    bitrates = [500000, 1000000]
    
    for bitrate in bitrates:
        print(f"  Trying {bitrate} bps...")
        
        # Setup slcan
        result = subprocess.run(
            f"sudo slcand -o -c -s8 -S {bitrate} /dev/ttyUSB0 slcan0",
            shell=True, capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            time.sleep(2)
            
            # Bring up interface
            result2 = subprocess.run(
                f"sudo ip link set slcan0 up type can bitrate {bitrate}",
                shell=True, capture_output=True, text=True, timeout=5
            )
            
            if result2.returncode == 0:
                # Check status
                result3 = subprocess.run(
                    "ip link show slcan0",
                    shell=True, capture_output=True, text=True
                )
                
                if "UP" in result3.stdout:
                    print(f"    ✓ slcan0 is UP at {bitrate} bps")
                    return True
                else:
                    print(f"    ✗ slcan0 is DOWN")
            else:
                print(f"    ✗ Failed to bring up: {result2.stderr}")
        else:
            print(f"    ✗ Failed to setup: {result.stderr}")
    
    return False

def main():
    serial_port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud_rate = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("Deep Investigation - Finding Missing Motors")
    print("="*70)
    print(f"\nSerial Port: {serial_port}")
    print(f"Baud Rate: {baud_rate}")
    print("\nTesting multiple strategies...")
    print("="*70)
    
    # Open serial
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened\n")
    except Exception as e:
        print(f"\n[ERROR] Failed to open serial port: {e}")
        return
    
    all_results = {}
    
    # Run strategies
    all_results['strategy_1'] = strategy_1_selective_gaps(ser)
    all_results['strategy_2'] = strategy_2_reverse_order(ser)
    all_results['strategy_3'] = strategy_3_powers_of_two(ser)
    all_results['strategy_4'] = strategy_4_slow_individual(ser)
    all_results['strategy_5'] = strategy_5_higher_bitrates(ser)
    all_results['strategy_6'] = strategy_6_broadcast_commands(ser)
    
    # CAN interface (doesn't need serial)
    can_success = strategy_7_can_interface_setup()
    
    ser.close()
    
    # Summary
    print("\n" + "="*70)
    print("INVESTIGATION SUMMARY")
    print("="*70)
    
    for strategy, result in all_results.items():
        if isinstance(result, list):
            print(f"\n{strategy}: Found {len(result)} IDs")
            if result:
                print(f"  {result[:20]}..." if len(result) > 20 else f"  {result}")
        elif isinstance(result, dict):
            print(f"\n{strategy}:")
            for key, val in result.items():
                print(f"  {key}: {val}")
    
    print(f"\nCAN Interface Setup: {'✓ Success' if can_success else '✗ Failed'}")
    
    # Find unique IDs across all strategies
    all_unique = set()
    for result in all_results.values():
        if isinstance(result, list):
            all_unique.update(result)
        elif isinstance(result, dict):
            for ids in result.values():
                if isinstance(ids, list):
                    all_unique.update(ids)
    
    if all_unique:
        print(f"\nTotal Unique IDs Found: {len(all_unique)}")
        print(f"  {sorted(all_unique)}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()

