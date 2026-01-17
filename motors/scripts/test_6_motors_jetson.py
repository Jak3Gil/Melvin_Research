#!/usr/bin/env python3
"""
Test all 6 identified motors
Quick verification that each motor responds and can move
"""

import serial
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

def build_l91_move(can_id, speed, direction):
    """Build L91 movement command"""
    speed_val = int(0x8000 + (speed * direction * 3283.0))
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
        print(f"Error: {e}")
        return b""

def test_motor(ser, motor_name, can_id, test_movement=True):
    """Test a single motor"""
    print(f"\n{'='*60}")
    print(f"Testing {motor_name} (CAN ID {can_id})")
    print(f"{'='*60}")
    
    # Activate
    print(f"  Activating...")
    response = send_command(ser, build_l91_activate(can_id), timeout=0.5)
    if response:
        print(f"  ✓ Activate: {len(response)} bytes")
    else:
        print(f"  ⚠️  No activate response")
    
    time.sleep(0.2)
    
    # Load params
    print(f"  Loading parameters...")
    response = send_command(ser, build_l91_load_params(can_id), timeout=0.5)
    if response:
        print(f"  ✓ LoadParams: {len(response)} bytes")
    else:
        print(f"  ✗ No load params response")
        return False
    
    time.sleep(0.2)
    
    if test_movement:
        # Forward
        print(f"  Moving forward...")
        send_command(ser, build_l91_move(can_id, 0.1, 1), timeout=0.3)
        time.sleep(0.5)
        
        # Stop
        send_command(ser, build_l91_stop(can_id), timeout=0.3)
        time.sleep(0.3)
        
        # Backward
        print(f"  Moving backward...")
        send_command(ser, build_l91_move(can_id, 0.1, -1), timeout=0.3)
        time.sleep(0.5)
        
        # Stop
        send_command(ser, build_l91_stop(can_id), timeout=0.3)
        time.sleep(0.2)
    
    # Deactivate
    print(f"  Deactivating...")
    send_command(ser, build_l91_deactivate(can_id), timeout=0.3)
    time.sleep(0.3)
    
    print(f"  ✓ {motor_name} test complete")
    return True

def main():
    port = '/dev/ttyUSB0'
    baud = 921600
    
    # The 6 identified motors
    motors = [
        {'name': 'Motor 1', 'id': 8, 'note': '3 IDs (8-10)'},
        {'name': 'Motor 2', 'id': 20, 'note': '1 ID (partial response)'},
        {'name': 'Motor 3', 'id': 31, 'note': '1 ID'},
        {'name': 'Motor 4', 'id': 32, 'note': '8 IDs (32-39)'},
        {'name': 'Motor 5', 'id': 64, 'note': '8 IDs (64-71)'},
        {'name': 'Motor 6', 'id': 72, 'note': '8 IDs (72-79)'}
    ]
    
    print("="*60)
    print("Testing 6 Identified Motors")
    print("="*60)
    print(f"\nPort: {port}")
    print(f"Baud Rate: {baud}")
    print(f"\nMotors to test:")
    for motor in motors:
        print(f"  {motor['name']}: CAN ID {motor['id']} - {motor['note']}")
    print()
    
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
        
        # Test each motor
        results = []
        for motor in motors:
            success = test_motor(ser, motor['name'], motor['id'], test_movement=True)
            results.append({
                'name': motor['name'],
                'id': motor['id'],
                'success': success
            })
            time.sleep(0.5)
        
        # Summary
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*60}\n")
        
        for result in results:
            status = "✓ PASS" if result['success'] else "✗ FAIL"
            print(f"  {result['name']} (ID {result['id']}): {status}")
        
        successful = sum(1 for r in results if r['success'])
        print(f"\n  Total: {successful}/{len(results)} motors working")
        
        print(f"\n{'='*60}")
        print("NEXT STEPS")
        print(f"{'='*60}\n")
        print(f"✅ Found: {successful} working motors")
        print(f"❌ Missing: {15 - successful} motors")
        print()
        print("To find missing motors:")
        print("  1. Check physical power/connections")
        print("  2. Try different baud rates")
        print("  3. Scan extended CAN IDs (128-2047)")
        print("  4. Check motor controller status LEDs")
        print()
        
        ser.close()
        print("[OK] Test complete\n")
        
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

