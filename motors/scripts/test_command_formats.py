#!/usr/bin/env python3
"""
Test Different Command Formats
Tests both:
1. Different address combinations (instead of 0x07 0xE8)
2. Formats without address bytes (direct CAN ID format)
"""

import serial
import sys
import time
import argparse

def build_activate_cmd_with_address(can_id, addr_high, addr_low):
    """Build activate command with custom address bytes"""
    return bytes([0x41, 0x54, 0x00, addr_high, addr_low, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_activate_direct(can_id):
    """Try direct format: AT 00 <can_id> 01 00 0d 0a (no address bytes)"""
    return bytes([0x41, 0x54, 0x00, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_activate_can_as_address(can_id):
    """Try using CAN ID as address: AT 00 00 <can_id> 01 00 0d 0a"""
    return bytes([0x41, 0x54, 0x00, 0x00, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_activate_swapped(can_id):
    """Try swapped format: AT 00 <can_id> 07 e8 01 00 0d 0a"""
    return bytes([0x41, 0x54, 0x00, can_id, 0x07, 0xe8, 0x01, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd, timeout=0.5, show_response=False):
    try:
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
        
        if show_response and response:
            print(f"    Response: {response.hex(' ')}")
        return len(response) > 4  # Motor responded
    except:
        return False

def test_address_combination(ser, can_id, addr_high, addr_low, description):
    """Test a specific address combination"""
    cmd = build_activate_cmd_with_address(can_id, addr_high, addr_low)
    return send_command(ser, cmd), cmd

def test_alternative_formats(ser, can_id):
    """Test alternative command formats"""
    formats = []
    
    # Format 1: Direct (no address bytes)
    formats.append(("Direct format (no address)", build_activate_direct(can_id)))
    
    # Format 2: CAN ID as address
    formats.append(("CAN ID as address", build_activate_can_as_address(can_id)))
    
    # Format 3: Swapped (CAN ID before address)
    formats.append(("Swapped format", build_activate_swapped(can_id)))
    
    # Format 4: Extended with length byte
    formats.append(("Extended with length", bytes([0x41, 0x54, 0x00, 0x08, can_id, 0x01, 0x00, 0x00, 0x00, 0x0d, 0x0a])))
    
    return formats

def main():
    parser = argparse.ArgumentParser(description='Test Different Command Formats')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('baud', type=int, nargs='?', default=921600, help='Baud rate')
    parser.add_argument('--can-id', type=int, default=8, help='CAN ID to test with (default: 8)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Test Different Command Formats")
    print("="*70)
    print(f"\nPort: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print(f"Testing with CAN ID: {args.can_id}")
    print("\nTesting both:")
    print("  1. Different address combinations (instead of 0x07 0xE8)")
    print("  2. Alternative formats (without address bytes, etc.)")
    print("="*70)
    
    ser = serial.Serial(args.port, args.baud, timeout=0.1)
    time.sleep(0.5)
    print("\n[OK] Serial port opened\n")
    
    # ========================================================================
    # TEST 1: Different Address Combinations
    # ========================================================================
    print("="*70)
    print("TEST 1: Different Address Combinations")
    print("="*70)
    print("Testing if 0x07 0xE8 can be replaced with other addresses\n")
    
    test_addresses = [
        # Current (known working) - baseline
        (0x07, 0xE8, "Current (0x07 0xE8) - BASELINE"),
        
        # All zeros/ones
        (0x00, 0x00, "All zeros (0x00 0x00)"),
        (0xFF, 0xFF, "All ones (0xFF 0xFF)"),
        
        # Single byte variations
        (0x01, 0x00, "0x01 0x00"),
        (0x00, 0x01, "0x00 0x01"),
        (0xFF, 0x00, "0xFF 0x00"),
        (0x00, 0xFF, "0x00 0xFF"),
        
        # Variations around 0x07E8
        (0x07, 0xDF, "0x07 0xDF (close)"),
        (0x07, 0xE7, "0x07 0xE7 (close)"),
        (0x07, 0xE9, "0x07 0xE9 (close)"),
        (0x07, 0xF0, "0x07 0xF0 (close)"),
        (0x08, 0xE8, "0x08 0xE8"),
        (0x06, 0xE8, "0x06 0xE8"),
        
        # Common CAN diagnostic/service addresses
        (0x7E, 0x08, "0x7E 0x08 (OBD diagnostic)"),
        (0x7D, 0xF0, "0x7D 0xF0"),
        (0x60, 0x00, "0x60 0x00"),
        (0x70, 0x00, "0x70 0x00"),
        
        # Using CAN ID in address position
        (args.can_id, 0x00, f"CAN ID {args.can_id} as high byte"),
        (0x00, args.can_id, f"CAN ID {args.can_id} as low byte"),
    ]
    
    working_addresses = []
    
    for addr_high, addr_low, description in test_addresses:
        print(f"  Testing {description:40} (0x{addr_high:02X} 0x{addr_low:02X})...", end='', flush=True)
        
        worked, cmd = test_address_combination(ser, args.can_id, addr_high, addr_low, description)
        
        if worked:
            working_addresses.append((addr_high, addr_low, description, cmd))
            print(" ✓ WORKS")
        else:
            print(" - No response")
        
        time.sleep(0.2)
    
    # ========================================================================
    # TEST 2: Alternative Formats (No Address Bytes)
    # ========================================================================
    print("\n" + "="*70)
    print("TEST 2: Alternative Command Formats")
    print("="*70)
    print("Testing formats without address bytes or different structures\n")
    
    formats = test_alternative_formats(ser, args.can_id)
    working_formats = []
    
    for format_name, cmd in formats:
        print(f"  Testing {format_name:40}...", end='', flush=True)
        print(f"  Hex: {cmd.hex(' ')}")
        
        if send_command(ser, cmd):
            working_formats.append((format_name, cmd))
            print("    ✓ WORKS")
        else:
            print("    - No response")
        
        time.sleep(0.2)
    
    # ========================================================================
    # RESULTS
    # ========================================================================
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    print("\n1. Address Combinations:")
    if working_addresses:
        print(f"   Found {len(working_addresses)} working address(es):")
        for addr_high, addr_low, desc, cmd in working_addresses:
            print(f"     {desc:40} : 0x{addr_high:02X} 0x{addr_low:02X}")
            print(f"       Command: {cmd.hex(' ')}")
    else:
        print("   No alternative addresses work - 0x07 0xE8 appears to be correct/required")
    
    print("\n2. Alternative Formats:")
    if working_formats:
        print(f"   Found {len(working_formats)} working format(s):")
        for format_name, cmd in working_formats:
            print(f"     {format_name:40}")
            print(f"       Command: {cmd.hex(' ')}")
    else:
        print("   No alternative formats work - address bytes appear to be required")
    
    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    
    if len(working_addresses) == 1:
        print("\n[CONCLUSION] Only 0x07 0xE8 works")
        print("  - This is likely the correct/protocol-specific address")
        print("  - Cannot be changed - it's part of the L91 protocol specification")
    elif len(working_addresses) > 1:
        print(f"\n[CONCLUSION] {len(working_addresses)} addresses work")
        print("  - Address might not be critical")
        print("  - Motors accept multiple address formats")
        print("  - May indicate address is for adapter, not motors")
    else:
        print("\n[CONCLUSION] None work (unexpected - check connections)")
    
    if working_formats:
        print(f"\n[IMPORTANT] Alternative format(s) work without 0x07 0xE8!")
        print("  - We might be using the wrong command format")
        print("  - Standard format might not need address bytes")
        print("  - Consider switching to working alternative format")
    
    ser.close()
    print("\n[OK] Test complete")

if __name__ == '__main__':
    main()

