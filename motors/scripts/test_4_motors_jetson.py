#!/usr/bin/env python3
"""
Quick test script for the 4 identified motors
Tests each motor individually with a small movement
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
    # Speed range: -1.0 to 1.0
    # Convert to motor speed value
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

def test_motor(ser, motor_num, can_id):
    """Test a single motor with movement"""
    print(f"\n{'='*60}")
    print(f"Testing Motor {motor_num} (CAN ID {can_id})")
    print(f"{'='*60}")
    
    # Activate
    print(f"  Activating motor...")
    response = send_command(ser, build_l91_activate(can_id), timeout=0.5)
    if response:
        print(f"  ✓ Activate response: {len(response)} bytes")
    else:
        print(f"  ✗ No activate response")
        return False
    
    time.sleep(0.2)
    
    # Load params
    print(f"  Loading parameters...")
    response = send_command(ser, build_l91_load_params(can_id), timeout=0.5)
    if response:
        print(f"  ✓ LoadParams response: {len(response)} bytes")
    else:
        print(f"  ✗ No load params response")
    
    time.sleep(0.2)
    
    # Small forward movement
    print(f"  Moving forward (0.1 speed)...")
    send_command(ser, build_l91_move(can_id, 0.1, 1), timeout=0.3)
    time.sleep(0.5)
    
    # Stop
    print(f"  Stopping...")
    send_command(ser, build_l91_stop(can_id), timeout=0.3)
    time.sleep(0.3)
    
    # Small backward movement
    print(f"  Moving backward (0.1 speed)...")
    send_command(ser, build_l91_move(can_id, 0.1, -1), timeout=0.3)
    time.sleep(0.5)
    
    # Stop
    print(f"  Stopping...")
    send_command(ser, build_l91_stop(can_id), timeout=0.3)
    time.sleep(0.2)
    
    # Deactivate
    print(f"  Deactivating motor...")
    send_command(ser, build_l91_deactivate(can_id), timeout=0.3)
    time.sleep(0.3)
    
    print(f"  ✓ Motor {motor_num} test complete")
    return True

def main():
    port = '/dev/ttyUSB0'
    baud = 921600
    
    # The 4 identified motors
    motors = [
        {'num': 1, 'can_id': 8},
        {'num': 2, 'can_id': 16},
        {'num': 3, 'can_id': 24},
        {'num': 4, 'can_id': 32}
    ]
    
    print("="*60)
    print("Testing 4 Identified Motors")
    print("="*60)
    print(f"\nPort: {port}")
    print(f"Baud Rate: {baud}")
    print(f"\nThis will test each of the 4 identified motors:")
    for motor in motors:
        print(f"  Motor {motor['num']}: CAN ID {motor['can_id']}")
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
            success = test_motor(ser, motor['num'], motor['can_id'])
            results.append({'motor': motor['num'], 'success': success})
            time.sleep(0.5)
        
        # Summary
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*60}\n")
        
        for result in results:
            status = "✓ PASS" if result['success'] else "✗ FAIL"
            print(f"  Motor {result['motor']}: {status}")
        
        successful = sum(1 for r in results if r['success'])
        print(f"\n  Total: {successful}/{len(results)} motors working")
        
        ser.close()
        print("\n[OK] Test complete\n")
        
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

