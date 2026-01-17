#!/usr/bin/env python3
"""
Find the missing 9 motors
Tries multiple strategies:
1. Extended CAN IDs (128-255)
2. Different baud rates
3. Alternative command formats
4. Broadcast wake-up sequences
"""

import serial
import time
import sys
import argparse

def build_l91_activate(can_id):
    """Build L91 activate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_l91_load_params(can_id):
    """Build L91 load params command"""
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

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
        return b""

def test_can_id(ser, can_id):
    """Test if a CAN ID responds"""
    response1 = send_command(ser, build_l91_activate(can_id), timeout=0.6)
    time.sleep(0.1)
    response2 = send_command(ser, build_l91_load_params(can_id), timeout=0.6)
    time.sleep(0.1)
    
    has_response = (len(response1) > 4) or (len(response2) > 4)
    return has_response, response1, response2

def scan_range(ser, start, end, description):
    """Scan a range of CAN IDs"""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"Scanning CAN IDs {start} to {end}")
    print(f"{'='*70}\n")
    
    found = []
    for can_id in range(start, end + 1):
        if can_id % 10 == 0:
            print(f"Progress: Testing ID {can_id}...")
        
        has_response, resp1, resp2 = test_can_id(ser, can_id)
        
        if has_response:
            print(f"\n✓ FOUND: CAN ID {can_id} (0x{can_id:02X}) responds!")
            if resp1:
                print(f"  Activate: {resp1.hex(' ')}")
            if resp2:
                print(f"  LoadParams: {resp2.hex(' ')}")
            found.append(can_id)
        
        time.sleep(0.05)
    
    return found

def try_different_baud_rates(port):
    """Try scanning with different baud rates"""
    baud_rates = [115200, 250000, 500000, 1000000]
    
    print(f"\n{'='*70}")
    print("Trying Different Baud Rates")
    print(f"{'='*70}\n")
    
    all_found = {}
    
    for baud in baud_rates:
        print(f"\n--- Testing Baud Rate: {baud} ---")
        try:
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
            
            # Quick scan of standard range
            found = []
            for can_id in [8, 16, 24, 32, 64, 72, 80, 88, 96, 104, 112, 120]:
                has_response, _, _ = test_can_id(ser, can_id)
                if has_response:
                    found.append(can_id)
            
            if found:
                print(f"  ✓ Found {len(found)} motors at {baud} baud: {found}")
                all_found[baud] = found
            else:
                print(f"  ✗ No motors found at {baud} baud")
            
            ser.close()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ✗ Error at {baud} baud: {e}")
    
    return all_found

def broadcast_wake_sequence(ser):
    """Try broadcast commands to wake up motors"""
    print(f"\n{'='*70}")
    print("Broadcast Wake-Up Sequence")
    print(f"{'='*70}\n")
    
    # Try various broadcast IDs
    broadcast_ids = [0x00, 0xFF, 0x7F]
    
    for bid in broadcast_ids:
        print(f"Sending broadcast to ID 0x{bid:02X}...")
        send_command(ser, build_l91_activate(bid), timeout=1.0)
        time.sleep(0.3)
    
    print("Broadcast sequence complete. Testing if new motors respond...")
    time.sleep(0.5)

def main():
    parser = argparse.ArgumentParser(description='Find missing 9 motors')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--baud', type=int, default=921600, help='Baud rate')
    parser.add_argument('--extended-only', action='store_true', 
                       help='Only scan extended range (128-255)')
    parser.add_argument('--baud-test', action='store_true',
                       help='Test different baud rates')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Finding Missing 9 Motors")
    print("="*70)
    print(f"\nPort: {args.port}")
    print(f"Baud Rate: {args.baud}")
    print()
    print("Known motors (6 found):")
    print("  Motor 1: CAN ID 8")
    print("  Motor 2: CAN ID 20")
    print("  Motor 3: CAN ID 31")
    print("  Motor 4: CAN ID 32")
    print("  Motor 5: CAN ID 64")
    print("  Motor 6: CAN ID 72")
    print()
    print("Searching for 9 missing motors...")
    print("="*70)
    
    if args.baud_test:
        # Test different baud rates
        results = try_different_baud_rates(args.port)
        
        print(f"\n{'='*70}")
        print("BAUD RATE TEST RESULTS")
        print(f"{'='*70}\n")
        
        for baud, motors in results.items():
            print(f"  {baud} baud: {len(motors)} motors - {motors}")
        
        return
    
    try:
        # Open serial port
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
        
        # Strategy 1: Broadcast wake-up
        if not args.extended_only:
            broadcast_wake_sequence(ser)
            time.sleep(0.5)
        
        # Strategy 2: Scan extended range (128-255)
        found_extended = scan_range(ser, 128, 255, "Strategy 1: Extended CAN IDs (128-255)")
        all_found.extend(found_extended)
        
        # Strategy 3: Scan gaps in standard range
        if not args.extended_only:
            found_gaps = scan_range(ser, 80, 127, "Strategy 2: Re-scan 80-127")
            all_found.extend(found_gaps)
        
        # Strategy 4: Scan very high IDs
        found_high = scan_range(ser, 256, 511, "Strategy 3: Very High CAN IDs (256-511)")
        all_found.extend(found_high)
        
        # Summary
        print(f"\n{'='*70}")
        print("SEARCH RESULTS")
        print(f"{'='*70}\n")
        
        if all_found:
            print(f"✓ Found {len(all_found)} new motor(s)!")
            print(f"  CAN IDs: {sorted(set(all_found))}")
            print()
            print(f"Total motors: {6 + len(set(all_found))}")
            print(f"Still missing: {15 - 6 - len(set(all_found))} motors")
        else:
            print("✗ No new motors found in extended ranges")
            print()
            print("Possible reasons:")
            print("  1. Motors not powered on")
            print("  2. Motors not connected to CAN bus")
            print("  3. Motors using different baud rate")
            print("  4. Motors in error/fault state")
            print("  5. Only 6 motors actually connected")
            print()
            print("Next steps:")
            print("  1. Check physical connections and power")
            print("  2. Run with --baud-test to try different baud rates")
            print("  3. Check motor controller status LEDs")
            print("  4. Verify you actually have 15 motors connected")
        
        ser.close()
        print("\n[OK] Search complete\n")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
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

