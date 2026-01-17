#!/usr/bin/env python3
"""
Extended CAN ID Scanner
Scans a much wider range of CAN IDs (0-2047) to find all motors.
CAN standard supports IDs 0-2047 (0x000-0x7FF)
"""

import serial
import sys
import time
import argparse

def build_activate_cmd(can_id):
    """Build activate command - CAN ID can be 1-2 bytes"""
    # For IDs > 255, we might need extended format
    # Standard format: AT 00 07 e8 <id_low_byte> 01 00 0d 0a
    if can_id <= 255:
        return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    else:
        # Extended format for IDs > 255
        # Try with ID in lower byte (modulo 256)
        id_byte = can_id & 0xFF
        return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, id_byte, 0x01, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd, timeout=0.3):
    """Send command and check for response"""
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
        
        return len(response) > 4  # Motor responded
    except:
        return False

def scan_range(ser, start_id, end_id, progress_interval=100):
    """Scan a range of CAN IDs"""
    found = []
    total = end_id - start_id + 1
    
    print(f"Scanning CAN IDs {start_id} to {end_id} (total: {total})...")
    print(f"Progress updates every {progress_interval} IDs\n")
    
    for i, can_id in enumerate(range(start_id, end_id + 1)):
        cmd = build_activate_cmd(can_id)
        if send_command(ser, cmd):
            found.append(can_id)
            print(f"  ✓ Found: CAN ID {can_id} (0x{can_id:03X})")
        
        # Progress update
        if (i + 1) % progress_interval == 0:
            progress = ((i + 1) / total) * 100
            print(f"  Progress: {i+1}/{total} ({progress:.1f}%) - Found {len(found)} so far...")
        
        time.sleep(0.01)  # Small delay between tests
    
    return found

def main():
    parser = argparse.ArgumentParser(description='Extended CAN ID Scanner')
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('baud', type=int, nargs='?', default=921600, help='Baud rate')
    parser.add_argument('--start', type=int, default=0, help='Start CAN ID (default: 0)')
    parser.add_argument('--end', type=int, default=2047, help='End CAN ID (default: 2047)')
    parser.add_argument('--chunk', type=int, default=500, help='Scan in chunks of this size')
    parser.add_argument('--save', type=str, help='Save results to file')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Extended CAN ID Scanner")
    print("="*70)
    print(f"\nPort: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print(f"Scanning CAN IDs: {args.start} to {args.end} (total: {args.end - args.start + 1})")
    print(f"Standard CAN supports IDs 0-2047 (0x000-0x7FF)")
    print("\nThis may take a while...")
    print("="*70)
    
    try:
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
        print("\n[OK] Serial port opened\n")
        
        all_found = []
        
        # Scan in chunks if specified
        if args.chunk > 0:
            chunks = []
            for start in range(args.start, args.end + 1, args.chunk):
                chunk_end = min(start + args.chunk - 1, args.end)
                chunks.append((start, chunk_end))
            
            print(f"Scanning in {len(chunks)} chunk(s) of ~{args.chunk} IDs each...\n")
            
            for i, (chunk_start, chunk_end) in enumerate(chunks):
                print(f"\n{'='*70}")
                print(f"Chunk {i+1}/{len(chunks)}: IDs {chunk_start} to {chunk_end}")
                print(f"{'='*70}")
                found = scan_range(ser, chunk_start, chunk_end, progress_interval=min(100, args.chunk//5))
                all_found.extend(found)
                print(f"\n[Chunk {i+1}] Found {len(found)} motor(s) in this range")
        else:
            all_found = scan_range(ser, args.start, args.end)
        
        # Final summary
        print("\n" + "="*70)
        print("SCAN COMPLETE")
        print("="*70)
        all_found_sorted = sorted(all_found)
        print(f"\nTotal motors found: {len(all_found_sorted)}")
        if all_found_sorted:
            print(f"\nCAN IDs responding:")
            for can_id in all_found_sorted:
                print(f"  CAN ID {can_id:4d} (0x{can_id:03X})")
            
            # Group by ranges
            print(f"\nGrouped by ranges:")
            ranges = []
            if all_found_sorted:
                start = all_found_sorted[0]
                end = all_found_sorted[0]
                for can_id in all_found_sorted[1:]:
                    if can_id == end + 1:
                        end = can_id
                    else:
                        ranges.append((start, end))
                        start = can_id
                        end = can_id
                ranges.append((start, end))
            
            for start, end in ranges:
                if start == end:
                    print(f"  ID {start} (0x{start:03X})")
                else:
                    print(f"  IDs {start}-{end} (0x{start:03X}-0x{end:03X}) - {end-start+1} IDs")
        else:
            print("\nNo motors found in this range")
        
        # Save to file if requested
        if args.save and all_found_sorted:
            with open(args.save, 'w') as f:
                f.write(f"CAN ID Scan Results\n")
                f.write(f"Range: {args.start} to {args.end}\n")
                f.write(f"Total found: {len(all_found_sorted)}\n\n")
                for can_id in all_found_sorted:
                    f.write(f"{can_id}\n")
            print(f"\nResults saved to: {args.save}")
        
        ser.close()
        print("\n[OK] Scan complete")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
        if all_found:
            print(f"\nFound so far: {sorted(all_found)}")
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

