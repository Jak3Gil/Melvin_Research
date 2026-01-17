#!/usr/bin/env python3
"""
Deep scan using all possible strategies to find missing 9 motors
Tests:
1. All baud rates (115200, 250000, 500000, 921600, 1000000)
2. Broadcast wake-up commands
3. Different command formats
4. Listen-only mode to detect any CAN traffic
5. Alternative protocols
"""

import serial
import time
import sys

def build_l91_activate(can_id):
    """Build L91 activate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_l91_load_params(can_id):
    """Build L91 load params command"""
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_broadcast_activate():
    """Broadcast activate to all motors"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0x00, 0x01, 0x00, 0x0d, 0x0a])

def build_broadcast_reset():
    """Broadcast reset command"""
    return bytes([0x41, 0x54, 0xFF, 0x07, 0xe8, 0x00, 0xFF, 0xFF, 0x0d, 0x0a])

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

def listen_for_traffic(ser, duration=5.0):
    """Listen for any CAN traffic"""
    print(f"  Listening for {duration} seconds...")
    start_time = time.time()
    traffic = []
    
    while time.time() - start_time < duration:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            traffic.append((time.time() - start_time, data))
            print(f"    [{time.time() - start_time:.2f}s] Received {len(data)} bytes: {data.hex(' ')}")
        time.sleep(0.05)
    
    return traffic

def test_baud_rate(port, baud, test_ids):
    """Test a specific baud rate"""
    print(f"\n{'='*70}")
    print(f"Testing Baud Rate: {baud}")
    print(f"{'='*70}")
    
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
        print(f"  ✓ Port opened at {baud} baud")
        
        # Try broadcast commands first
        print(f"  Sending broadcast activate...")
        send_command(ser, build_broadcast_activate(), timeout=1.0)
        time.sleep(0.3)
        
        print(f"  Sending broadcast reset...")
        send_command(ser, build_broadcast_reset(), timeout=1.0)
        time.sleep(0.5)
        
        # Listen for any spontaneous traffic
        print(f"  Listening for spontaneous CAN traffic...")
        traffic = listen_for_traffic(ser, duration=2.0)
        
        # Test specific IDs
        found = []
        print(f"  Testing specific CAN IDs...")
        for can_id in test_ids:
            resp1 = send_command(ser, build_l91_activate(can_id), timeout=0.6)
            time.sleep(0.1)
            resp2 = send_command(ser, build_l91_load_params(can_id), timeout=0.6)
            time.sleep(0.1)
            
            if len(resp1) > 4 or len(resp2) > 4:
                print(f"    ✓ CAN ID {can_id} responds!")
                found.append(can_id)
        
        ser.close()
        
        if found:
            print(f"\n  ✅ Found {len(found)} motors at {baud} baud: {found}")
        else:
            print(f"  ✗ No motors found at {baud} baud")
        
        return found, len(traffic) > 0
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return [], False

def scan_all_ids_at_baud(port, baud, start=1, end=127):
    """Comprehensive scan at specific baud rate"""
    print(f"\n{'='*70}")
    print(f"Comprehensive Scan at {baud} baud (IDs {start}-{end})")
    print(f"{'='*70}")
    
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
        
        found = []
        for can_id in range(start, end + 1):
            if can_id % 20 == 0:
                print(f"  Progress: ID {can_id}/{end}...")
            
            resp1 = send_command(ser, build_l91_activate(can_id), timeout=0.6)
            time.sleep(0.1)
            resp2 = send_command(ser, build_l91_load_params(can_id), timeout=0.6)
            time.sleep(0.1)
            
            if len(resp1) > 4 or len(resp2) > 4:
                print(f"\n  ✓ FOUND: CAN ID {can_id}")
                if resp1:
                    print(f"    Activate: {resp1.hex(' ')}")
                if resp2:
                    print(f"    LoadParams: {resp2.hex(' ')}")
                found.append(can_id)
        
        ser.close()
        return found
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

def main():
    port = '/dev/ttyUSB0'
    
    # Common baud rates for CAN/motor controllers
    baud_rates = [115200, 250000, 500000, 921600, 1000000]
    
    # IDs to test quickly
    quick_test_ids = [8, 16, 20, 24, 31, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]
    
    print("="*70)
    print("DEEP MOTOR INVESTIGATION - All Strategies")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"\nKnown motors (6 found at 921600 baud):")
    print("  Motor 1: CAN ID 8")
    print("  Motor 2: CAN ID 20")
    print("  Motor 3: CAN ID 31")
    print("  Motor 4: CAN ID 32")
    print("  Motor 5: CAN ID 64")
    print("  Motor 6: CAN ID 72")
    print()
    print("Searching for 9 missing motors using all strategies...")
    print("="*70)
    
    all_results = {}
    
    # Strategy 1: Quick test all baud rates
    print("\n" + "="*70)
    print("STRATEGY 1: Quick Test All Baud Rates")
    print("="*70)
    
    for baud in baud_rates:
        found, has_traffic = test_baud_rate(port, baud, quick_test_ids)
        all_results[baud] = found
        time.sleep(0.5)
    
    # Strategy 2: Full scan at most promising baud rate
    print("\n" + "="*70)
    print("STRATEGY 2: Full Scan at 921600 baud")
    print("="*70)
    
    found_full = scan_all_ids_at_baud(port, 921600, 1, 127)
    
    # Strategy 3: Try other promising baud rates
    for baud in [115200, 250000, 500000]:
        if baud in all_results and len(all_results[baud]) > 0:
            print(f"\n  Found motors at {baud} baud, doing full scan...")
            found = scan_all_ids_at_baud(port, baud, 1, 127)
            all_results[f"{baud}_full"] = found
    
    # Final Summary
    print("\n" + "="*70)
    print("INVESTIGATION RESULTS")
    print("="*70)
    
    print("\nMotors found by baud rate:")
    for key, motors in all_results.items():
        if motors:
            print(f"  {key}: {len(motors)} motors - {motors}")
    
    # Count unique motors across all baud rates
    all_motors = set()
    for motors in all_results.values():
        all_motors.update(motors)
    
    print(f"\n{'='*70}")
    print(f"TOTAL UNIQUE MOTORS FOUND: {len(all_motors)}")
    print(f"{'='*70}")
    
    if len(all_motors) > 6:
        print(f"\n✅ SUCCESS! Found {len(all_motors) - 6} additional motors!")
        print(f"   New motors: {sorted(all_motors - {8, 20, 31, 32, 64, 72})}")
    elif len(all_motors) == 6:
        print(f"\n⚠️  Still only 6 motors found")
        print(f"   The 9 missing motors are likely:")
        print(f"   1. Not physically connected")
        print(f"   2. Not powered on")
        print(f"   3. In fault/error state")
        print(f"   4. Using different protocol")
    else:
        print(f"\n⚠️  Found fewer motors than before: {len(all_motors)}")
    
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS")
    print(f"{'='*70}")
    print()
    print("1. Check physical setup:")
    print("   - Count actual motors connected")
    print("   - Verify all have power")
    print("   - Check CAN bus wiring")
    print()
    print("2. Check motor controller LEDs:")
    print("   - Green = OK")
    print("   - Red = Error/Fault")
    print("   - Blinking = Different states")
    print()
    print("3. Try power cycling:")
    print("   - Turn off all motors")
    print("   - Wait 10 seconds")
    print("   - Turn on one at a time")
    print()
    print("4. Check documentation:")
    print("   - Verify expected motor count")
    print("   - Check if all motors are same model")
    print("   - Review configuration requirements")
    print()

if __name__ == '__main__':
    main()

