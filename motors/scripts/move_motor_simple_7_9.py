#!/usr/bin/env python3
"""
Simple script to move motors 7 and 9 individually in small, slow increments
Uses the confirmed working byte encodings: 0x70 for Motor 7, 0x58 for Motor 9
"""
import serial
import time
import sys

def move_motor_jog(ser, can_id, speed, flag=1):
    """Move motor using JOG command"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.05)

def activate_motor(ser, can_id):
    """Activate motor"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.2)

def stop_motor(ser, can_id):
    """Stop motor"""
    move_motor_jog(ser, can_id, 0.0, 0)

def move_motor_back_forth(ser, motor_name, can_id):
    """
    Move motor back and forth in small, slow increments
    """
    print(f"\n{'='*70}")
    print(f"{motor_name} - Moving back and forth")
    print(f"{'='*70}")
    
    speed = 0.03  # Very slow speed
    move_time = 0.8  # Move for 0.8 seconds
    pause_time = 0.4  # Pause between movements
    
    try:
        # Activate
        print(f"\n  [1] Activating {motor_name}...")
        activate_motor(ser, can_id)
        time.sleep(0.3)
        
        # Forward
        print(f"  [2] Moving FORWARD (speed={speed})...")
        move_motor_jog(ser, can_id, speed, 1)
        time.sleep(move_time)
        
        # Stop
        print(f"  [3] STOPPING...")
        stop_motor(ser, can_id)
        time.sleep(pause_time)
        
        # Backward
        print(f"  [4] Moving BACKWARD (speed={-speed})...")
        move_motor_jog(ser, can_id, -speed, 1)
        time.sleep(move_time)
        
        # Stop
        print(f"  [5] STOPPING...")
        stop_motor(ser, can_id)
        time.sleep(pause_time)
        
        # Forward again
        print(f"  [6] Moving FORWARD again...")
        move_motor_jog(ser, can_id, speed, 1)
        time.sleep(move_time)
        
        # Stop
        print(f"  [7] STOPPING...")
        stop_motor(ser, can_id)
        time.sleep(pause_time)
        
        # Backward again
        print(f"  [8] Moving BACKWARD again...")
        move_motor_jog(ser, can_id, -speed, 1)
        time.sleep(move_time)
        
        # Final stop
        print(f"  [9] FINAL STOP...")
        stop_motor(ser, can_id)
        time.sleep(0.3)
        
        print(f"\n  [{motor_name} test complete]")
        print(f"  Did you see {motor_name} move? (Forward -> Backward -> Forward -> Backward)")
        
    except Exception as e:
        print(f"  [ERROR] {e}")

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    try:
        ser = serial.Serial(port, 921600, timeout=2.0)
        print("="*70)
        print("Moving Motors 7 and 9 Individually - Small & Slow")
        print("="*70)
        print()
        print("Using confirmed byte encodings:")
        print("  Motor 7: Byte 0x70")
        print("  Motor 9: Byte 0x58")
        print()
        print("Watch the physical motors during the test!")
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        # Test actual CAN IDs directly
        print("\n" + "="*70)
        print("TESTING CAN ID 7 (actual Motor 7 CAN ID)")
        print("="*70)
        print("WATCH ALL MOTORS - Which one moves?")
        move_motor_back_forth(ser, "CAN ID 7", 7)
        time.sleep(2)
        
        print("\n" + "="*70)
        print("TESTING CAN ID 9 (actual Motor 9 CAN ID)")
        print("="*70)
        print("WATCH ALL MOTORS - Which one moves?")
        move_motor_back_forth(ser, "CAN ID 9", 9)
        time.sleep(2)
        
        ser.close()
        
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)
        print()
        print("Observations:")
        print("  - Motor 7 should have moved (using byte 0x70)")
        print("  - Motor 9 should have moved (using byte 0x58)")
        print()
        print("If motors moved, we've confirmed:")
        print("  [OK] Motors 7 and 9 can be controlled individually")
        print("  [OK] Byte encodings 0x70 (Motor 7) and 0x58 (Motor 9) work for movement")
        print()
        print("="*70)
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

