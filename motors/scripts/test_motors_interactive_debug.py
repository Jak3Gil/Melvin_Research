#!/usr/bin/env python3
"""
Interactive Motor Tester - Debug Version (shows errors clearly)
"""

import serial
import sys
import time
import msvcrt
import os

# L91 Protocol commands (same as before)
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
        start_time = time.time()
        while time.time() - start_time < 0.1:
            if ser.in_waiting > 0:
                ser.read(ser.in_waiting)
            time.sleep(0.01)
        return True
    except Exception as e:
        print(f"Send command error: {e}")
        return False

def activate_motor(ser, can_id):
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)

def deactivate_motor(ser, can_id):
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.1)

def move_motor(ser, can_id, speed):
    send_command(ser, build_move_jog_cmd(can_id, speed, 1))

def stop_motor(ser, can_id):
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))

def get_key():
    if msvcrt.kbhit():
        key = msvcrt.getch()
        key_lower = key.lower()
        if key == b'\r':
            return 'ENTER'
        elif key == b' ':
            return 'SPACE'
        elif key_lower == b'w':
            return 'W'
        elif key_lower == b's':
            return 'S'
        elif key_lower == b'q':
            return 'Q'
    return None

def main():
    port = "COM3"
    baud = 921600
    
    print("="*60)
    print("INTERACTIVE MOTOR TESTER (Debug Version)")
    print("="*60)
    print(f"\nPort: {port}")
    print(f"Baud Rate: {baud}")
    print("\nAttempting to open serial port...")
    
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
        print("[OK] Serial port opened successfully!")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Failed to open serial port: {e}")
        print("\nMake sure:")
        print("  1. COM3 exists and is connected")
        print("  2. No other program is using COM3")
        print("  3. Drivers are installed")
        print("\nPress any key to exit...")
        try:
            msvcrt.getch()
        except:
            input()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print("\nPress any key to exit...")
        try:
            msvcrt.getch()
        except:
            input()
        sys.exit(1)
    
    # Motor IDs
    motor_ids = list(range(16, 23)) + list(range(8, 16))
    physical_numbers = list(range(1, 8)) + list(range(8, 16))
    
    motor_index = 0
    move_speed = 0.02
    move_duration = 0.3
    
    print("\nStarting motor testing...")
    print("Controls: W=forward, S=backward, SPACE=next, Q=quit")
    print("\nPress any key to start...")
    try:
        msvcrt.getch()
    except:
        input()
    
    try:
        while motor_index < len(motor_ids):
            can_id = motor_ids[motor_index]
            physical_num = physical_numbers[motor_index]
            
            # Clear screen and show status
            os.system('cls')
            print("="*60)
            print("INTERACTIVE MOTOR TESTER")
            print("="*60)
            print(f"\nTesting Motor {motor_index + 1} of {len(motor_ids)}")
            print(f"CAN ID: {can_id} (0x{can_id:02X})")
            print(f"Physical Motor Number: {physical_num}")
            print("\n" + "-"*60)
            print("CONTROLS:")
            print("  W / w - Move forward (small jog)")
            print("  S / s - Move backward (small jog)")
            print("  SPACE - Next motor")
            print("  Q / q - Quit")
            print("-"*60)
            
            print(f"\n[Activating motor CAN ID {can_id}...]")
            activate_motor(ser, can_id)
            print("[Motor activated - Ready for input]\n")
            
            while True:
                key = get_key()
                
                if key == 'SPACE':
                    stop_motor(ser, can_id)
                    deactivate_motor(ser, can_id)
                    motor_index += 1
                    break
                elif key == 'W':
                    print("  >> Moving FORWARD...")
                    move_motor(ser, can_id, move_speed)
                    time.sleep(move_duration)
                    stop_motor(ser, can_id)
                    print("  [Stopped]\n")
                elif key == 'S':
                    print("  << Moving BACKWARD...")
                    move_motor(ser, can_id, -move_speed)
                    time.sleep(move_duration)
                    stop_motor(ser, can_id)
                    print("  [Stopped]\n")
                elif key == 'Q':
                    stop_motor(ser, can_id)
                    deactivate_motor(ser, can_id)
                    print("\n\n[Stopping all motors and exiting...]")
                    time.sleep(0.5)
                    ser.close()
                    print("[OK] Exited cleanly")
                    return
                
                time.sleep(0.05)
        
        os.system('cls')
        print("="*60)
        print("ALL MOTORS TESTED")
        print("="*60)
        print("\n[OK] Test complete!")
        ser.close()
        
    except KeyboardInterrupt:
        print("\n\n[Interrupted - Stopping motors...]")
        for can_id in motor_ids:
            stop_motor(ser, can_id)
            deactivate_motor(ser, can_id)
        ser.close()
        print("[OK] Exited cleanly")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()
        print("\nPress any key to exit...")
        try:
            msvcrt.getch()
        except:
            input()

if __name__ == '__main__':
    main()

