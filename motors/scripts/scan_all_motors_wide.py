#!/usr/bin/env python3
"""
Comprehensive Motor Scanner - Scan IDs 1-127 to find ALL motors
Based on your findings: M3 at 21-30, M8 at 64, M9 at 73
"""

import serial
import sys
import time
import argparse

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd, description="", show_response=False):
    """Send L91 command and check for response"""
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.15)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        
        if show_response and response:
            print(f"  Response: {response.hex(' ')}")
        
        return response, len(response) > 4
    except Exception as e:
        if show_response:
            print(f"  Error: {e}")
        return b"", False

def scan_motor_range(ser, start_id, end_id, verbose=False):
    """Scan a range of motor IDs"""
    found_motors = []
    
    for can_id in range(start_id, end_id + 1):
        if verbose:
            print(f"Testing ID {can_id:3d} (0x{can_id:02X})...", end='', flush=True)
        
        # Try activate
        cmd = build_activate_cmd(can_id)
        response, has_response = send_command(ser, cmd, show_response=False)
        
        if has_response:
            # Verify with load params
            cmd = build_load_params_cmd(can_id)
            response2, has_response2 = send_command(ser, cmd, show_response=False)
            
            # Deactivate
            send_command(ser, build_deactivate_cmd(can_id), show_response=False)
            time.sleep(0.1)
            
            if has_response2:
                found_motors.append(can_id)
                if verbose:
                    print(f" ✓ FOUND")
                else:
                    print(f"  Found: CAN ID {can_id:3d} (0x{can_id:02X})")
            else:
                if verbose:
                    print(f" (partial response)")
        else:
            if verbose:
                print(f" -")
    
    return found_motors

def group_consecutive_ids(ids):
    """Group consecutive IDs into ranges"""
    if not ids:
        return []
    
    ranges = []
    start = ids[0]
    end = ids[0]
    
    for i in range(1, len(ids)):
        if ids[i] == end + 1:
            end = ids[i]
        else:
            ranges.append((start, end))
            start = ids[i]
            end = ids[i]
    
    ranges.append((start, end))
    return ranges

def main():
    parser = argparse.ArgumentParser(description='Comprehensive Motor Scanner (IDs 1-127)')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', 
                       help='Serial port (default: /dev/ttyUSB0)')
    parser.add_argument('baud', type=int, nargs='?', default=921600, 
                       help='Baud rate (default: 921600)')
    parser.add_argument('--start', type=int, default=1, 
                       help='Start CAN ID (default: 1)')
    parser.add_argument('--end', type=int, default=127, 
                       help='End CAN ID (default: 127)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Show all IDs being tested')
    parser.add_argument('--quick', action='store_true',
                       help='Quick scan of known ranges only')
    
    args = parser.parse_args()
    
    print("="*70)
    print("  Comprehensive Motor Scanner")
    print("="*70)
    print()
    print(f"Port: {args.port}")
    print(f"Baud Rate: {args.baud}")
    
    if args.quick:
        print("Mode: Quick scan (known ranges)")
        scan_ranges = [
            (1, 31, "Low range (1-31)"),
            (32, 63, "Mid range (32-63)"),
            (64, 95, "High range (64-95)"),
            (96, 127, "Very high range (96-127)")
        ]
    else:
        print(f"Scanning: CAN IDs {args.start} to {args.end}")
        scan_ranges = [(args.start, args.end, f"Full scan ({args.start}-{args.end})")]
    
    print()
    
    try:
        # Open serial port
        print(f"Opening serial port {args.port}...")
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            write_timeout=1.0
        )
        time.sleep(0.5)
        print("[OK] Serial port opened\n")
        
        # Send detection command
        print("Sending detection command (AT+AT)...")
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        send_command(ser, detect_cmd)
        time.sleep(0.5)
        print()
        
        all_found = []
        
        # Scan each range
        for start_id, end_id, description in scan_ranges:
            print(f"Scanning {description}...")
            print("-" * 70)
            
            found = scan_motor_range(ser, start_id, end_id, verbose=args.verbose)
            all_found.extend(found)
            
            if found:
                print(f"  Found {len(found)} motor(s) in this range")
            else:
                print(f"  No motors found in this range")
            print()
        
        # Display results
        print("="*70)
        print("SCAN RESULTS")
        print("="*70)
        
        if all_found:
            print(f"\n✓ Found {len(all_found)} responding CAN ID(s):\n")
            
            # Group into ranges
            ranges = group_consecutive_ids(sorted(all_found))
            
            print("CAN ID Ranges:")
            for start, end in ranges:
                if start == end:
                    print(f"  • ID {start} (0x{start:02X})")
                else:
                    print(f"  • IDs {start}-{end} (0x{start:02X}-0x{end:02X}) [{end-start+1} IDs]")
            
            print("\nAll CAN IDs:")
            for can_id in sorted(all_found):
                print(f"  • CAN ID {can_id:3d} (0x{can_id:02X})")
            
            # Analysis
            print("\n" + "="*70)
            print("ANALYSIS")
            print("="*70)
            
            print(f"\nTotal responding IDs: {len(all_found)}")
            print(f"ID ranges found: {len(ranges)}")
            
            # Check for known patterns
            print("\nKnown motor patterns:")
            if any(8 <= id <= 15 for id in all_found):
                ids_8_15 = [id for id in all_found if 8 <= id <= 15]
                print(f"  • IDs 8-15: {len(ids_8_15)} IDs found - Likely Motor 1 or Motors 8-15")
            
            if any(16 <= id <= 31 for id in all_found):
                ids_16_31 = [id for id in all_found if 16 <= id <= 31]
                print(f"  • IDs 16-31: {len(ids_16_31)} IDs found - Likely Motor 2 or Motors 1-7")
            
            if any(21 <= id <= 30 for id in all_found):
                ids_21_30 = [id for id in all_found if 21 <= id <= 30]
                print(f"  • IDs 21-30: {len(ids_21_30)} IDs found - Motor 3 (per your info)")
            
            if 64 in all_found:
                print(f"  • ID 64: Motor 8 (per your info)")
            
            if 73 in all_found:
                print(f"  • ID 73: Motor 9 (per your info)")
            
            print("\n⚠️  WARNING:")
            print("Multiple IDs may control the same physical motor.")
            print("Run 'verify_motor_mapping.py' to determine physical motor mapping.")
            
        else:
            print("\n✗ No motors found")
            print("\nTroubleshooting:")
            print("  1. Check USB-to-CAN adapter connection")
            print("  2. Verify motors are powered on")
            print("  3. Check CAN bus wiring (CAN-H, CAN-L)")
            print("  4. Try different baud rate (115200)")
        
        ser.close()
        print("\n[OK] Scan complete")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if 'ser' in locals():
            ser.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

