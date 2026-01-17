#!/usr/bin/env python3
"""
Quick Motor Test - Test specific IDs to verify motor mapping
Usage: python3 quick_motor_test.py /dev/ttyUSB0 921600 <CAN_ID>
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

def build_move_jog_cmd(can_id, speed=0.0, flag=1):
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = int(0x8000 + (speed * 3283.0))
    else:
        speed_val = int(0x7fff + (speed * 3283.0))
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, flag])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd):
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.05)

def test_motor(ser, can_id, num_pulses=3):
    """Test motor with specified number of pulses"""
    print(f"\nTesting CAN ID {can_id} (0x{can_id:02X})")
    print(f"Pattern: {num_pulses} pulse(s)")
    print("Watch which motor moves!\n")
    
    # Activate
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    # Execute pattern
    for i in range(num_pulses):
        print(f"  Pulse {i+1}/{num_pulses}...")
        send_command(ser, build_move_jog_cmd(can_id, 0.08, 1))
        time.sleep(0.4)
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.3)
    
    # Deactivate
    send_command(ser, build_deactivate_cmd(can_id))
    print("\nTest complete.")

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 quick_motor_test.py <PORT> <BAUD> <CAN_ID> [NUM_PULSES]")
        print("\nExamples:")
        print("  python3 quick_motor_test.py /dev/ttyUSB0 921600 8")
        print("  python3 quick_motor_test.py /dev/ttyUSB0 921600 21 5")
        print("\nKnown IDs:")
        print("  IDs 8-15: Motor group 1")
        print("  IDs 16-20: Motor group 2")
        print("  IDs 21-30: Motor 3 (per user)")
        print("  IDs 31-39: Motor group 4")
        print("  IDs 64-71: Motor 8 (ID 64 per user)")
        print("  IDs 72-79: Motor 9 (ID 73 per user)")
        sys.exit(1)
    
    port = sys.argv[1]
    baud = int(sys.argv[2])
    can_id = int(sys.argv[3])
    num_pulses = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    
    print("="*60)
    print("  Quick Motor Test")
    print("="*60)
    print(f"Port: {port}")
    print(f"Baud: {baud}")
    print(f"CAN ID: {can_id} (0x{can_id:02X})")
    print(f"Pulses: {num_pulses}")
    print("="*60)
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        
        # Send detection command
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        ser.flush()
        time.sleep(0.3)
        
        test_motor(ser, can_id, num_pulses)
        
        ser.close()
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

