#!/usr/bin/env python3
"""
Identify Motors - Move motors one at a time with unique patterns
Since all motors respond to all IDs, we'll use timing/sequence to identify them
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
        time.sleep(0.05)
        return True
    except:
        return False

def identify_motor_sequence(ser, motor_number):
    """
    Create a unique movement pattern for each motor so you can identify it
    Pattern: motor_number short movements in quick succession
    """
    # Use any CAN ID since they all respond (we'll use ID 8)
    test_can_id = 8
    
    print(f"\n{'='*60}")
    print(f"IDENTIFYING MOTOR {motor_number}")
    print(f"{'='*60}")
    print(f"\nWatch for a motor that moves {motor_number} times in quick succession!")
    print(f"This motor will be Motor {motor_number}")
    input("\nPress Enter when ready to start...")
    
    # Activate
    send_command(ser, build_activate_cmd(test_can_id))
    time.sleep(0.3)
    send_command(ser, build_load_params_cmd(test_can_id))
    time.sleep(0.3)
    
    # Move motor_number times with short movements
    for i in range(motor_number):
        print(f"  Movement {i+1} of {motor_number}...")
        send_command(ser, build_move_jog_cmd(test_can_id, 0.05, 1))
        time.sleep(0.4)
        send_command(ser, build_move_jog_cmd(test_can_id, 0.0, 0))
        time.sleep(0.3)
        
        send_command(ser, build_move_jog_cmd(test_can_id, -0.05, 1))
        time.sleep(0.4)
        send_command(ser, build_move_jog_cmd(test_can_id, 0.0, 0))
        time.sleep(0.3)
    
    # Stop
    send_command(ser, build_move_jog_cmd(test_can_id, 0.0, 0))
    send_command(ser, build_deactivate_cmd(test_can_id))
    
    response = input(f"\nDid you identify Motor {motor_number}? (y/n): ")
    return response.lower() == 'y'

def main():
    port = "COM3"
    baud = 921600
    
    print("="*60)
    print("MOTOR IDENTIFICATION TOOL")
    print("="*60)
    print("\nThis tool will help you identify motors by making each")
    print("motor move with a unique pattern (number of movements).")
    print("\nSince all motors currently respond to the same commands,")
    print("we'll use timing/sequence to identify them.")
    print("\nNOTE: This assumes motors respond in order or you can")
    print("visually identify which motor moves.")
    
    input("\nPress Enter to start identification...")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened")
        
        # Identify motors 1-15
        identified = {}
        
        for motor_num in range(1, 16):
            if identify_motor_sequence(ser, motor_num):
                # Ask which CAN ID this motor should have
                print(f"\nMotor {motor_num} identified!")
                print("\nWhat CAN ID should this motor be configured to?")
                print("(Suggested: Motor 1-7 -> IDs 16-22, Motor 8-15 -> IDs 8-15)")
                try:
                    can_id = int(input("CAN ID (1-31, or 0 to skip): "))
                    if can_id > 0 and can_id <= 31:
                        identified[motor_num] = can_id
                        print(f"[OK] Motor {motor_num} will be configured to CAN ID {can_id}")
                except:
                    print(f"[SKIP] Motor {motor_num} skipped")
            
            input("\nPress Enter to continue to next motor...")
        
        # Summary
        print("\n" + "="*60)
        print("IDENTIFICATION SUMMARY")
        print("="*60)
        if identified:
            print("\nMotors identified:")
            for motor_num, can_id in sorted(identified.items()):
                print(f"  Physical Motor {motor_num} -> CAN ID {can_id} (0x{can_id:02X})")
        else:
            print("\nNo motors were identified.")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

