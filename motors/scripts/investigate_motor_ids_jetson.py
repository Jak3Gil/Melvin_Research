#!/usr/bin/env python3
"""
Comprehensive Motor ID Investigation for Jetson
Tests all CAN IDs and identifies which physical motors are responding
"""

import serial
import struct
import time
import sys

def build_l91_activate(can_id):
    """Build L91 activate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_l91_deactivate(can_id):
    """Build L91 deactivate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_l91_load_params(can_id):
    """Build L91 load params command"""
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_l91_move_small(can_id, direction=1):
    """Build L91 small movement command for testing"""
    # Small speed value for testing
    if direction > 0:
        speed_val = int(0x8000 + (0.1 * 3283.0))  # Small forward
    else:
        speed_val = int(0x8000 - (0.1 * 3283.0))  # Small backward
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, 1 if direction > 0 else 0])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def build_l91_stop(can_id):
    """Build L91 stop command"""
    speed_val = 0x7fff
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, 0])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd, timeout=0.5):
    """Send command and read response"""
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
                time.sleep(0.05)
            else:
                time.sleep(0.02)
        
        return response
    except Exception as e:
        print(f"Error sending command: {e}")
        return b""

def test_can_id(ser, can_id, test_movement=False):
    """Test if a CAN ID responds"""
    # Try activate
    response1 = send_command(ser, build_l91_activate(can_id), timeout=0.6)
    time.sleep(0.2)
    
    # Try load params
    response2 = send_command(ser, build_l91_load_params(can_id), timeout=0.6)
    time.sleep(0.2)
    
    has_response = (len(response1) > 4) or (len(response2) > 4)
    
    if has_response and test_movement:
        # Test with small movement
        print(f"    Testing movement on CAN ID {can_id}...")
        send_command(ser, build_l91_move_small(can_id, 1), timeout=0.3)
        time.sleep(0.3)
        send_command(ser, build_l91_stop(can_id), timeout=0.3)
        time.sleep(0.2)
    
    # Deactivate
    send_command(ser, build_l91_deactivate(can_id), timeout=0.3)
    time.sleep(0.1)
    
    return has_response, response1, response2

def scan_all_ids(ser, start=1, end=127):
    """Scan all CAN IDs in range"""
    print(f"\n{'='*70}")
    print(f"Scanning CAN IDs {start} to {end}")
    print(f"{'='*70}\n")
    
    responding_ids = []
    
    for can_id in range(start, end + 1):
        print(f"Testing CAN ID {can_id:3d} (0x{can_id:02X})...", end=" ")
        sys.stdout.flush()
        
        has_response, resp1, resp2 = test_can_id(ser, can_id, test_movement=False)
        
        if has_response:
            print(f"✓ RESPONDS")
            responding_ids.append(can_id)
            if resp1:
                print(f"    Activate response: {resp1.hex(' ')}")
            if resp2:
                print(f"    LoadParams response: {resp2.hex(' ')}")
        else:
            print("✗")
        
        time.sleep(0.1)
    
    return responding_ids

def group_consecutive_ids(ids):
    """Group consecutive CAN IDs into ranges"""
    if not ids:
        return []
    
    groups = []
    current_group = [ids[0]]
    
    for i in range(1, len(ids)):
        if ids[i] == current_group[-1] + 1:
            current_group.append(ids[i])
        else:
            groups.append(current_group)
            current_group = [ids[i]]
    
    groups.append(current_group)
    return groups

def test_physical_motors(ser, responding_ids):
    """Test which CAN IDs control the same physical motor"""
    print(f"\n{'='*70}")
    print("Testing Physical Motor Mapping")
    print(f"{'='*70}\n")
    
    print("This will test each responding CAN ID with a small movement.")
    print("Watch the motors and note which ones move for each CAN ID.\n")
    
    for can_id in responding_ids:
        input(f"Press Enter to test CAN ID {can_id}...")
        
        # Activate
        send_command(ser, build_l91_activate(can_id), timeout=0.5)
        time.sleep(0.2)
        send_command(ser, build_l91_load_params(can_id), timeout=0.5)
        time.sleep(0.2)
        
        # Move forward
        print(f"  Moving CAN ID {can_id} forward...")
        send_command(ser, build_l91_move_small(can_id, 1), timeout=0.3)
        time.sleep(0.5)
        
        # Stop
        send_command(ser, build_l91_stop(can_id), timeout=0.3)
        time.sleep(0.3)
        
        # Move backward
        print(f"  Moving CAN ID {can_id} backward...")
        send_command(ser, build_l91_move_small(can_id, -1), timeout=0.3)
        time.sleep(0.5)
        
        # Stop
        send_command(ser, build_l91_stop(can_id), timeout=0.3)
        time.sleep(0.2)
        
        # Deactivate
        send_command(ser, build_l91_deactivate(can_id), timeout=0.3)
        time.sleep(0.3)
        
        print(f"  Done testing CAN ID {can_id}\n")

def main():
    port = '/dev/ttyUSB0'
    baud = 921600
    
    print("="*70)
    print("Motor ID Investigation - Jetson")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud Rate: {baud}\n")
    
    try:
        # Open serial port
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            write_timeout=1.0
        )
        time.sleep(0.5)
        print("[OK] Serial port opened\n")
        
        # Scan standard range first (1-31)
        print("Phase 1: Scanning standard CAN ID range (1-31)")
        responding_standard = scan_all_ids(ser, 1, 31)
        
        # Scan extended range (32-127)
        print("\nPhase 2: Scanning extended CAN ID range (32-127)")
        responding_extended = scan_all_ids(ser, 32, 127)
        
        # Combine results
        all_responding = responding_standard + responding_extended
        
        # Summary
        print(f"\n{'='*70}")
        print("SCAN RESULTS SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"Total CAN IDs responding: {len(all_responding)}")
        print(f"CAN IDs: {all_responding}\n")
        
        if responding_standard:
            print(f"Standard range (1-31): {len(responding_standard)} IDs")
            groups = group_consecutive_ids(responding_standard)
            for group in groups:
                if len(group) > 1:
                    print(f"  Range: {group[0]}-{group[-1]} ({len(group)} IDs)")
                else:
                    print(f"  ID: {group[0]}")
        
        if responding_extended:
            print(f"\nExtended range (32-127): {len(responding_extended)} IDs")
            groups = group_consecutive_ids(responding_extended)
            for group in groups:
                if len(group) > 1:
                    print(f"  Range: {group[0]}-{group[-1]} ({len(group)} IDs)")
                else:
                    print(f"  ID: {group[0]}")
        
        # Physical motor test
        if all_responding:
            print(f"\n{'='*70}")
            print("PHYSICAL MOTOR MAPPING TEST")
            print(f"{'='*70}\n")
            
            response = input("Do you want to test physical motor mapping? (y/n): ")
            if response.lower() == 'y':
                test_physical_motors(ser, all_responding)
        
        # Analysis
        print(f"\n{'='*70}")
        print("ANALYSIS")
        print(f"{'='*70}\n")
        
        if len(all_responding) == 0:
            print("❌ No motors responding!")
            print("   - Check power connections")
            print("   - Verify CAN bus wiring")
            print("   - Try different baud rate")
        elif len(all_responding) < 15:
            print(f"⚠️  Only {len(all_responding)} CAN IDs responding (expected 15 motors)")
            print(f"   - {15 - len(all_responding)} motors may be offline or not configured")
            print("   - Check if multiple IDs control same physical motor")
            print("   - Verify all motors are powered and connected")
        else:
            print(f"✓ Found {len(all_responding)} responding CAN IDs")
            print("  - May include multiple IDs per motor")
            print("  - Run physical mapping test to identify unique motors")
        
        ser.close()
        print("\n[OK] Investigation complete\n")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        print("  - Check if /dev/ttyUSB0 exists")
        print("  - Verify user is in dialout group: sudo usermod -a -G dialout $USER")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if 'ser' in locals():
            ser.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

