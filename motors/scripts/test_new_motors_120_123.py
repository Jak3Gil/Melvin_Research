#!/usr/bin/env python3
"""
Test New Motors (IDs 120-123) with Back and Forth Movement
Makes motors move clearly so you can see them
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

def move_motor_back_and_forth(ser, can_id, cycles=3, speed=0.1):
    """Move motor back and forth multiple times"""
    print(f"\n{'='*70}")
    print(f"Testing CAN ID {can_id} (0x{can_id:02X})")
    print(f"{'='*70}")
    print(f"\n👀 WATCH YOUR MOTORS! Which one moves?\n")
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"Starting in {i}...", flush=True)
        time.sleep(1)
    
    print("\n🔄 MOVING NOW!\n")
    
    # Activate
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    # Move back and forth
    for cycle in range(cycles):
        print(f"  Cycle {cycle+1}/{cycles}:")
        
        # Forward
        print(f"    → Forward...", flush=True)
        send_command(ser, build_move_jog_cmd(can_id, speed, 1))
        time.sleep(1.0)
        
        # Stop
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.3)
        
        # Backward
        print(f"    ← Backward...", flush=True)
        send_command(ser, build_move_jog_cmd(can_id, -speed, 1))
        time.sleep(1.0)
        
        # Stop
        send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
        time.sleep(0.3)
    
    # Final stop
    print("    ⏹ Stopping...")
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
    time.sleep(0.2)
    
    # Deactivate
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.3)
    
    print("\n✅ Test complete for ID {}\n".format(can_id))
    time.sleep(1)

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("  Test New Motors (IDs 120-123) - Back and Forth Movement")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}")
    print("\nThis will test each motor ID with clear back-and-forth movement.")
    print("Watch carefully to see which physical motors move!")
    print("="*70)
    
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    
    try:
        # Open serial port
        print(f"\nOpening serial port {port}...")
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("✓ Serial port opened\n")
        
        # Send detection command
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        ser.flush()
        time.sleep(0.5)
        
        # Test each new motor ID
        new_motor_ids = [120, 121, 122, 123]
        
        for motor_id in new_motor_ids:
            move_motor_back_and_forth(ser, motor_id, cycles=3, speed=0.1)
            
            # Pause between motors
            if motor_id != new_motor_ids[-1]:
                print("⏸️  Pausing 2 seconds before next motor...\n")
                time.sleep(2)
        
        # Summary
        print("\n" + "="*70)
        print("ALL TESTS COMPLETE")
        print("="*70)
        print("\nTested motor IDs:")
        for motor_id in new_motor_ids:
            print(f"  • CAN ID {motor_id} (0x{motor_id:02X})")
        
        print("\n" + "="*70)
        print("QUESTIONS TO ANSWER:")
        print("="*70)
        print("\n1. Did you see any motors move?")
        print("2. How many DIFFERENT motors moved?")
        print("3. Did multiple IDs move the SAME motor?")
        print("\nPlease note which physical motors moved for each ID!")
        
        ser.close()
        print("\n[COMPLETE]")
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        if 'ser' in locals():
            # Emergency stop
            for motor_id in [120, 121, 122, 123]:
                try:
                    ser.write(build_deactivate_cmd(motor_id))
                    ser.flush()
                except:
                    pass
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

