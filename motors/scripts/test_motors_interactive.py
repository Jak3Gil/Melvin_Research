#!/usr/bin/env python3
"""
Interactive Motor Tester
Test motors one at a time with keyboard controls

Controls:
  W / w - Move motor forward (small jog)
  S / s - Move motor backward (small jog)
  Space - Next motor
  Q / q - Quit
"""

import serial
import sys
import time
import msvcrt  # Windows-specific for keyboard input
import os

# L91 Protocol commands
def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0, flag=1):
    """Build move jog command with small speed (0.02 = very small movement)"""
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
    """Send command and clear response"""
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.05)  # Short delay
        
        # Clear any response
        start_time = time.time()
        while time.time() - start_time < 0.1:
            if ser.in_waiting > 0:
                ser.read(ser.in_waiting)
            time.sleep(0.01)
        return True
    except:
        return False

def activate_motor(ser, can_id):
    """Activate and initialize a motor"""
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)

def deactivate_motor(ser, can_id):
    """Deactivate a motor"""
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.1)

def move_motor(ser, can_id, speed):
    """Move motor with small speed (0.02 = very small, 0.05 = small)"""
    send_command(ser, build_move_jog_cmd(can_id, speed, 1))

def stop_motor(ser, can_id):
    """Stop motor"""
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))

def get_key():
    """Get a keypress (Windows)"""
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

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_status(motor_index, total_motors, can_id, physical_num):
    """Print current status"""
    clear_screen()
    print("="*60)
    print("INTERACTIVE MOTOR TESTER")
    print("="*60)
    print(f"\nTesting Motor {motor_index + 1} of {total_motors}")
    print(f"CAN ID: {can_id} (0x{can_id:02X})")
    print(f"Physical Motor Number: {physical_num}")
    print("\n" + "-"*60)
    print("CONTROLS:")
    print("  W / w - Move forward (small jog)")
    print("  S / s - Move backward (small jog)")
    print("  SPACE - Next motor")
    print("  Q / q - Quit")
    print("-"*60)
    print("\nWaiting for input...")

def main():
    port = "COM3"
    baud = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baud = int(sys.argv[2])
    
    # Motor IDs to test (8-15 and 16-22 = 15 motors)
    # Assuming: 16-22 are physical motors 1-7, 8-15 are physical motors 8-15
    motor_ids = list(range(16, 23)) + list(range(8, 16))  # IDs 16-22, then 8-15
    physical_numbers = list(range(1, 8)) + list(range(8, 16))  # Physical 1-7, then 8-15
    
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
        
        motor_index = 0
        move_speed = 0.02  # Very small speed (adjust if needed)
        move_duration = 0.3  # How long to move when key is pressed
        
        print("\n[OK] Serial port opened")
        print("Starting interactive motor tester...")
        time.sleep(1)
        
        while motor_index < len(motor_ids):
            can_id = motor_ids[motor_index]
            physical_num = physical_numbers[motor_index]
            
            # Activate current motor
            print_status(motor_index, len(motor_ids), can_id, physical_num)
            print(f"\n[Activating motor CAN ID {can_id}...]")
            activate_motor(ser, can_id)
            print("[Motor activated - Ready for input]\n")
            
            # Interactive loop for this motor
            while True:
                key = get_key()
                
                if key == 'SPACE':
                    # Stop and move to next motor
                    stop_motor(ser, can_id)
                    deactivate_motor(ser, can_id)
                    motor_index += 1
                    break
                    
                elif key == 'W':
                    # Move forward
                    print("  >> Moving FORWARD...")
                    move_motor(ser, can_id, move_speed)
                    time.sleep(move_duration)
                    stop_motor(ser, can_id)
                    print_status(motor_index, len(motor_ids), can_id, physical_num)
                    print("\nWaiting for input...")
                    
                elif key == 'S':
                    # Move backward
                    print("  << Moving BACKWARD...")
                    move_motor(ser, can_id, -move_speed)
                    time.sleep(move_duration)
                    stop_motor(ser, can_id)
                    print_status(motor_index, len(motor_ids), can_id, physical_num)
                    print("\nWaiting for input...")
                    
                elif key == 'Q':
                    # Quit
                    stop_motor(ser, can_id)
                    deactivate_motor(ser, can_id)
                    print("\n\n[Stopping all motors and exiting...]")
                    time.sleep(0.5)
                    ser.close()
                    print("[OK] Exited cleanly")
                    return
                
                time.sleep(0.05)  # Small delay to prevent CPU spinning
        
        # All motors tested
        clear_screen()
        print("="*60)
        print("ALL MOTORS TESTED")
        print("="*60)
        print("\n[OK] Test complete!")
        ser.close()
        
    except KeyboardInterrupt:
        print("\n\n[Interrupted - Stopping motors...]")
        if 'ser' in locals():
            for can_id in motor_ids:
                stop_motor(ser, can_id)
                deactivate_motor(ser, can_id)
            ser.close()
        print("[OK] Exited cleanly")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

