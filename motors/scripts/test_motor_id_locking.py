#!/usr/bin/env python3
"""
Test if motors can be "locked" to single IDs after rapid activation
Tests various approaches to configure motors individually
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

def build_custom_cmd(cmd_byte, can_id, data):
    """Build custom command with specific command byte"""
    cmd = bytearray([0x41, 0x54, cmd_byte, 0x07, 0xe8, can_id])
    cmd.extend(data)
    cmd.extend([0x0d, 0x0a])
    return bytes(cmd)

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

def rapid_activation_sequence(ser, max_id=100):
    """Run the rapid activation sequence that wakes up motors"""
    print("Running rapid activation sequence...")
    for can_id in range(1, max_id + 1):
        send_command(ser, build_activate_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    
    for can_id in range(1, max_id + 1):
        send_command(ser, build_load_params_cmd(can_id), timeout=0.1)
        time.sleep(0.01)
    time.sleep(0.2)
    print("  [OK] Activation complete")

def test_which_ids_respond(ser, test_range):
    """Test which IDs respond after activation"""
    responding = []
    for can_id in test_range:
        has_response, _ = send_command(ser, build_activate_cmd(can_id), timeout=0.2)
        if has_response:
            responding.append(can_id)
        time.sleep(0.05)
    return responding

def test_1_single_activation_lock(ser):
    """Test 1: Try activating a single ID multiple times to 'claim' it"""
    print("\n" + "="*70)
    print("TEST 1: Single ID Repeated Activation (Claim/Lock)")
    print("="*70)
    
    # Deactivate all
    print("Deactivating all...")
    for can_id in range(1, 100):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.005)
    time.sleep(0.3)
    
    # Activate only ID 8 multiple times
    print("\nActivating ONLY ID 8 multiple times (attempting to 'lock' it)...")
    for i in range(10):
        send_command(ser, build_activate_cmd(8), timeout=0.1)
        time.sleep(0.05)
        send_command(ser, build_load_params_cmd(8), timeout=0.1)
        time.sleep(0.05)
    
    time.sleep(0.3)
    
    # Test what responds
    print("Testing which IDs respond...")
    responding = test_which_ids_respond(ser, range(1, 32))
    print(f"  IDs responding: {responding}")
    
    if len(responding) == 1 and 8 in responding:
        print("\n[SUCCESS] ID 8 locked! Only ID 8 responds")
        return True
    else:
        print(f"\n[FAIL] Multiple IDs still respond: {responding}")
        return False

def test_2_configuration_commands(ser):
    """Test 2: Try various command bytes that might configure motors"""
    print("\n" + "="*70)
    print("TEST 2: Configuration Command Bytes")
    print("="*70)
    print("Testing various command bytes that might configure motor IDs...")
    
    # Common configuration command bytes to test
    config_commands = [
        (0x10, "0x10 - Set ID?"),
        (0x11, "0x11 - Configure?"),
        (0x12, "0x12 - Set Address?"),
        (0x21, "0x21 - Save Config?"),
        (0x30, "0x30 - Write EEPROM?"),
        (0x40, "0x40 - Set Parameter?"),
        (0x50, "0x50 - Configuration Mode?"),
        (0x60, "0x60 - Set CAN ID?"),
        (0x70, "0x70 - Lock ID?"),
        (0x80, "0x80 - Unlock ID?"),
        (0xA0, "0xA0 - Enable?"),
        (0xA1, "0xA1 - Disable?"),
        (0xB0, "0xB0 - Set Address?"),
        (0xC0, "0xC0 - Reset?"),
        (0xF0, "0xF0 - Factory Reset?"),
    ]
    
    rapid_activation_sequence(ser, 50)
    
    # Test each command byte with ID 8
    print("\nTesting configuration commands on ID 8...")
    print("Format: AT <cmd_byte> 07 e8 08 <data> \\r\\n")
    
    working_commands = []
    
    for cmd_byte, description in config_commands:
        print(f"\n  Testing {description} (0x{cmd_byte:02X})...", end='', flush=True)
        
        # Try with different data payloads
        test_data = [
            bytes([0x01, 0x00, 0x08, 0x00]),  # Set ID 8?
            bytes([0x08, 0x00, 0x00, 0x00]),  # ID 8 as data
            bytes([0x00, 0x08, 0x00, 0x00]),  # ID 8 as second byte
            bytes([0x08]),                     # Just ID
        ]
        
        found_response = False
        for data in test_data:
            cmd = build_custom_cmd(cmd_byte, 8, data)
            has_response, response = send_command(ser, cmd, timeout=0.2)
            if has_response:
                print(f" ✓ Response received")
                working_commands.append((cmd_byte, description, data, response))
                found_response = True
                break
            time.sleep(0.05)
        
        if not found_response:
            print(" -")
    
    if working_commands:
        print(f"\n[SUCCESS] Found {len(working_commands)} command(s) that respond:")
        for cmd_byte, desc, data, resp in working_commands:
            print(f"  {desc}: Data={data.hex(' ')}, Response={resp.hex(' ')[:40]}...")
    else:
        print("\n[FAIL] No configuration commands responded")
    
    return working_commands

def test_3_isolated_activation(ser):
    """Test 3: Try activating one ID, then testing if others still respond"""
    print("\n" + "="*70)
    print("TEST 3: Isolated Activation Test")
    print("="*70)
    
    # Deactivate all
    print("Deactivating all...")
    for can_id in range(1, 100):
        send_command(ser, build_deactivate_cmd(can_id), timeout=0.1)
        time.sleep(0.005)
    time.sleep(0.5)
    
    # Activate ONLY ID 8, very slowly
    print("\nActivating ONLY ID 8 (slow, isolated)...")
    send_command(ser, build_activate_cmd(8), timeout=0.2)
    time.sleep(0.5)
    send_command(ser, build_load_params_cmd(8), timeout=0.2)
    time.sleep(0.5)
    
    # Test what responds
    print("Testing which IDs respond (should only be 8)...")
    responding = test_which_ids_respond(ser, range(1, 32))
    print(f"  IDs responding: {responding}")
    
    if responding == [8]:
        print("\n[SUCCESS] Only ID 8 responds! Isolation worked")
        return True
    elif 8 in responding:
        print(f"\n[PARTIAL] ID 8 responds, but so do: {[x for x in responding if x != 8]}")
        return False
    else:
        print(f"\n[FAIL] ID 8 doesn't respond, but these do: {responding}")
        return False

def test_4_parameter_variations(ser):
    """Test 4: Try different load params values to configure motors"""
    print("\n" + "="*70)
    print("TEST 4: Parameter Variations")
    print("="*70)
    
    rapid_activation_sequence(ser, 50)
    
    print("Testing different load params values...")
    print("Current: AT 20 07 e8 <id> 08 00 c4 00 00 00 00 00 00 0d 0a")
    
    # Try variations of load params command
    variations = [
        (bytes([0x08, 0x00, 0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08]), "Set ID 8 in params"),
        (bytes([0x08, 0x00, 0xc4, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00]), "ID 8 in different position"),
        (bytes([0x08, 0x00, 0xc4, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00]), "ID 8 in byte 4"),
        (bytes([0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08]), "ID 8 at end"),
    ]
    
    for data, description in variations:
        print(f"\n  Testing: {description}...", end='', flush=True)
        cmd = build_custom_cmd(0x20, 8, data)
        has_response, response = send_command(ser, cmd, timeout=0.2)
        if has_response:
            print(f" ✓ Response")
        else:
            print(" -")
        time.sleep(0.1)
    
    # Test if any of these changed which IDs respond
    print("\nTesting which IDs respond after parameter variations...")
    responding = test_which_ids_respond(ser, range(1, 32))
    print(f"  IDs responding: {responding}")

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("Motor ID Locking Investigation")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud Rate: {baud}")
    print("\nThis will test various methods to lock motors to single IDs:")
    print("  1. Single ID repeated activation")
    print("  2. Configuration command bytes")
    print("  3. Isolated activation")
    print("  4. Parameter variations")
    print("="*70)
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    print("\n[OK] Serial port opened\n")
    
    results = {}
    
    results['single_lock'] = test_1_single_activation_lock(ser)
    results['config_cmds'] = test_2_configuration_commands(ser)
    results['isolated'] = test_3_isolated_activation(ser)
    test_4_parameter_variations(ser)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if results.get('single_lock'):
        print("\n✓ Single ID repeated activation can lock motors")
    else:
        print("\n✗ Single ID repeated activation does NOT lock motors")
    
    if results.get('config_cmds'):
        print(f"\n✓ Found {len(results['config_cmds'])} configuration commands that respond")
    else:
        print("\n✗ No configuration commands found")
    
    if results.get('isolated'):
        print("\n✓ Isolated activation works (only one ID responds)")
    else:
        print("\n✗ Isolated activation does NOT work")
    
    ser.close()
    print("\n[OK] Investigation complete")

if __name__ == '__main__':
    main()

