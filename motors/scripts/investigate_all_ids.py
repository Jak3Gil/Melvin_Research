#!/usr/bin/env python3
"""
Comprehensive CAN ID Investigation
Tests all possible IDs using both L91 protocol and direct CAN
"""

import serial
import sys
import time
import argparse
from threading import Thread, Lock

# L91 Protocol Functions
def build_activate_cmd_l91(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_load_params_cmd_l91(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def send_l91_command(ser, cmd, timeout=0.3):
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

def scan_l91_protocol(serial_port, baud_rate, start_id=0, end_id=255):
    """Scan using L91 protocol over serial"""
    print("="*70)
    print(f"L91 Protocol Scan: IDs {start_id}-{end_id}")
    print("="*70)
    
    try:
        # Try different serial configurations
        try:
            ser = serial.Serial(serial_port, baud_rate, timeout=0.1, 
                               bytesize=serial.EIGHTBITS,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE)
        except:
            # Try with write timeout
            ser = serial.Serial(serial_port, baud_rate, timeout=0.1, 
                               write_timeout=1.0)
        time.sleep(0.5)
        print(f"[OK] Opened {serial_port} at {baud_rate} baud\n")
    except Exception as e:
        print(f"[ERROR] Failed to open {serial_port}: {e}")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Try: sudo chmod 666 {serial_port}")
        print(f"  Or add user to dialout group: sudo usermod -a -G dialout $USER\n")
        return []
    
    found_ids = []
    
    # Rapid activation sequence first
    print("Running rapid activation sequence...")
    for can_id in range(start_id, min(end_id + 1, 256)):
        send_l91_command(ser, build_activate_cmd_l91(can_id), timeout=0.05)
        time.sleep(0.01)
    time.sleep(0.2)
    
    for can_id in range(start_id, min(end_id + 1, 256)):
        send_l91_command(ser, build_load_params_cmd_l91(can_id), timeout=0.05)
        time.sleep(0.01)
    time.sleep(0.2)
    
    # Now test each ID
    print(f"\nTesting IDs {start_id}-{end_id}...")
    for can_id in range(start_id, min(end_id + 1, 256)):
        has_response, _ = send_l91_command(ser, build_activate_cmd_l91(can_id), timeout=0.2)
        if has_response:
            found_ids.append(('L91', can_id))
            print(f"  ID {can_id:3d}: ✓")
        else:
            if can_id % 50 == 0:
                print(f"  Progress: {can_id}/{end_id} ({len(found_ids)} found)")
        time.sleep(0.02)
    
    ser.close()
    return found_ids

def scan_can_sdk(can_interface, start_id=0, end_id=255):
    """Scan using RobStride SDK via direct CAN"""
    print("\n" + "="*70)
    print(f"Direct CAN Scan (SDK): IDs {start_id}-{end_id}")
    print("="*70)
    print(f"CAN Interface: {can_interface}\n")
    
    found_ids = []
    
    try:
        from robstride import RobStrideMotor, MotorType
        
        # Try different motor types
        motor_types = [MotorType.RS05, MotorType.RS09, MotorType.RS03, MotorType.RS06]
        
        for can_id in range(start_id, min(end_id + 1, 256)):
            found = False
            for motor_type in motor_types:
                try:
                    motor = RobStrideMotor(
                        can_id=can_id,
                        interface=can_interface,
                        motor_type=motor_type,
                        timeout=0.3
                    )
                    
                    motor.connect()
                    device_id = motor.get_device_id()
                    
                    if device_id:
                        found_ids.append(('CAN', can_id, motor_type.name))
                        print(f"  ID {can_id:3d} ({motor_type.name}): ✓")
                        motor.disconnect()
                        found = True
                        break
                    
                    motor.disconnect()
                except Exception as e:
                    # Silently continue to next motor type
                    pass
                
            if not found and can_id % 50 == 0:
                print(f"  Progress: {can_id}/{end_id} ({len(found_ids)} found)")
            
            time.sleep(0.05)
            
    except ImportError:
        print("[SKIP] RobStride SDK not available")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    return found_ids

def scan_can_raw(can_interface, start_id=0, end_id=255):
    """Scan using raw CAN commands (cansend/candump)"""
    print("\n" + "="*70)
    print(f"Raw CAN Scan: IDs {start_id}-{end_id}")
    print("="*70)
    print("[NOTE] Raw CAN scan requires manual monitoring")
    print("Run in another terminal: candump " + can_interface)
    print("="*70)
    
    import subprocess
    
    found_ids = []
    
    # Test RobStride protocol frame format
    # Control frame: 0x200 + motor_id (29-bit extended)
    # Status request: 0x300 + motor_id
    
    print(f"\nSending test frames...")
    for can_id in range(start_id, min(end_id + 1, 256)):
        # Try control frame (0x200 + id)
        frame_id_control = 0x200 + can_id
        
        try:
            # Send empty frame to test
            cmd = f"timeout 0.1 cansend {can_interface} {frame_id_control:03X}#0000000000000000 2>/dev/null"
            subprocess.run(cmd, shell=True, capture_output=True)
            
            if can_id % 50 == 0:
                print(f"  Progress: {can_id}/{end_id} (check candump for responses)")
            
            time.sleep(0.05)
        except:
            pass
    
    print(f"\n[NOTE] Check candump output for responses")
    return found_ids

def rapid_activation_all(serial_port, baud_rate):
    """Rapid activation of all IDs to wake up motors"""
    print("\nRunning comprehensive rapid activation...")
    
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
        time.sleep(0.5)
    except:
        return False
    
    # Activate all possible IDs
    print("  Activating IDs 0-255...")
    for can_id in range(0, 256):
        send_l91_command(ser, build_activate_cmd_l91(can_id), timeout=0.05)
        time.sleep(0.005)
    time.sleep(0.3)
    
    print("  Loading params for IDs 0-255...")
    for can_id in range(0, 256):
        send_l91_command(ser, build_load_params_cmd_l91(can_id), timeout=0.05)
        time.sleep(0.005)
    time.sleep(0.5)
    
    ser.close()
    return True

def main():
    parser = argparse.ArgumentParser(description='Comprehensive CAN ID Investigation')
    parser.add_argument('--serial', default='/dev/ttyUSB0', help='Serial port for L91 (default: /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=921600, help='Serial baud rate (default: 921600)')
    parser.add_argument('--can-interface', default='can0', help='CAN interface for SDK (default: can0)')
    parser.add_argument('--start', type=int, default=0, help='Start ID (default: 0)')
    parser.add_argument('--end', type=int, default=255, help='End ID (default: 255)')
    parser.add_argument('--l91-only', action='store_true', help='Only test L91 protocol')
    parser.add_argument('--can-only', action='store_true', help='Only test CAN SDK')
    parser.add_argument('--skip-activation', action='store_true', help='Skip rapid activation sequence')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Comprehensive CAN ID Investigation")
    print("="*70)
    print(f"\nTesting IDs: {args.start}-{args.end}")
    print(f"L91: {args.serial} @ {args.baud} baud")
    print(f"CAN: {args.can_interface}")
    print("="*70)
    
    all_found = []
    
    # Rapid activation first (unless skipped)
    if not args.skip_activation and not args.can_only:
        print("\n" + "="*70)
        print("Pre-Scan Activation")
        print("="*70)
        if rapid_activation_all(args.serial, args.baud):
            print("[OK] Rapid activation complete")
        time.sleep(1.0)
    
    # L91 Protocol Scan
    if not args.can_only:
        l91_results = scan_l91_protocol(args.serial, args.baud, args.start, args.end)
        all_found.extend(l91_results)
    
    # CAN SDK Scan
    if not args.l91_only:
        can_results = scan_can_sdk(args.can_interface, args.start, args.end)
        all_found.extend(can_results)
    
    # Summary
    print("\n" + "="*70)
    print("INVESTIGATION RESULTS")
    print("="*70)
    
    l91_ids = [id for proto, id in all_found if proto == 'L91']
    can_ids = [id for items in all_found if items[0] == 'CAN' for id in [items[1]]]
    
    if l91_ids:
        print(f"\nL91 Protocol - Found {len(l91_ids)} ID(s):")
        print(f"  {sorted(l91_ids)}")
    
    if can_ids:
        print(f"\nCAN SDK - Found {len(can_ids)} ID(s):")
        print(f"  {sorted(set(can_ids))}")
    
    all_unique_ids = sorted(set([id if isinstance(id, int) else id[1] for id in all_found]))
    
    if all_unique_ids:
        print(f"\nTotal Unique IDs Found: {len(all_unique_ids)}")
        print(f"  {all_unique_ids}")
        
        # Group into ranges
        ranges = []
        if all_unique_ids:
            range_start = all_unique_ids[0]
            range_end = all_unique_ids[0]
            
            for can_id in all_unique_ids[1:]:
                if can_id == range_end + 1:
                    range_end = can_id
                else:
                    ranges.append((range_start, range_end))
                    range_start = can_id
                    range_end = can_id
            ranges.append((range_start, range_end))
        
        print(f"\nID Ranges: {len(ranges)}")
        for start, end in ranges:
            count = end - start + 1
            print(f"  IDs {start:3d}-{end:3d} ({count} IDs)")
        
        print(f"\nMotors Found: {len(ranges)}")
        print(f"Motors Missing: {15 - len(ranges)}")
    else:
        print("\n✗ No IDs found")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()

