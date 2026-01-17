#!/usr/bin/env python3
"""
Test a SINGLE motor ID to see if only one motor moves
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
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.1)
        return True
    except:
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_single_motor.py <CAN_ID>")
        print("Example: python test_single_motor.py 8")
        sys.exit(1)
    
    can_id = int(sys.argv[1])
    port = "COM3"
    baud = 921600
    
    print("="*60)
    print(f"Testing ONLY Motor CAN ID {can_id} (0x{can_id:02X})")
    print("="*60)
    print("\nWARNING: Watch ALL motors carefully!")
    print(f"This will ONLY send commands to CAN ID {can_id}")
    print("\nPress Enter to continue...")
    input()
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print(f"\n[OK] Serial port opened")
        
        # First, deactivate ALL possible motor IDs to make sure only one responds
        print("\n[Deactivating all motors first...]")
        for test_id in range(1, 32):
            send_command(ser, build_deactivate_cmd(test_id))
        time.sleep(0.5)
        
        # Now activate ONLY the target motor
        print(f"\n[Activating ONLY Motor ID {can_id}...]")
        send_command(ser, build_activate_cmd(can_id))
        time.sleep(0.3)
        
        print(f"[Loading parameters for Motor ID {can_id}...]")
        send_command(ser, build_load_params_cmd(can_id))
        time.sleep(0.3)
        
        print(f"\n[Moving Motor ID {can_id} FORWARD (small movement)...]")
        print("Watch which physical motor(s) move!")
        send_command(ser, build_move_jog_cmd(can_id, 0.03, 1))
        time.sleep(1.0)
        
        print("[Stopping...]")
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.5)
        
        print(f"\n[Moving Motor ID {can_id} BACKWARD (small movement)...]")
        print("Watch which physical motor(s) move!")
        send_command(ser, build_move_jog_cmd(can_id, -0.03, 1))
        time.sleep(1.0)
        
        print("[Stopping...]")
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.5)
        
        print(f"\n[Deactivating Motor ID {can_id}...]")
        send_command(ser, build_deactivate_cmd(can_id))
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
        print(f"\nWhich physical motor(s) moved when testing CAN ID {can_id}?")
        print("(If ALL motors moved, they might all be configured to the same ID)")
        print("(If NO motors moved, that ID might not exist)")
        print("(If ONE motor moved, that's correct!)")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

