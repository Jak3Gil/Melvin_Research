#!/usr/bin/env python3
"""
Find correct byte encodings for Motors 7 and 9
We discovered:
- Byte 0x70 moves Motor 14 (not Motor 7!)
- Byte 0x58 moves Motor 11 (not Motor 9!)

Now need to test likely bytes to find the real Motors 7 and 9
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

def test_byte_for_motor(ser, byte_val, motor_id):
    """Test if a byte value controls a specific motor"""
    speed = 0.05
    print(f"  Testing byte 0x{byte_val:02x}...", end=' ', flush=True)
    
    activate_motor(ser, byte_val)
    time.sleep(0.3)
    
    # Move forward briefly
    move_motor_jog(ser, byte_val, speed, 1)
    time.sleep(0.5)
    
    stop_motor(ser, byte_val)
    time.sleep(0.3)
    
    print("[Sent]")
    return True

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    try:
        ser = serial.Serial(port, 921600, timeout=2.0)
        print("="*70)
        print("Finding Correct Bytes for Motors 7 and 9")
        print("="*70)
        print()
        print("CORRECTED FINDINGS:")
        print("  Byte 0x70 -> Moves Motor 14 (NOT Motor 7!)")
        print("  Byte 0x58 -> Moves Motor 11 (NOT Motor 9!)")
        print()
        print("Motor 7 query uses byte 0x3c (long format)")
        print("Motor 9 query uses byte 0x4c (long format)")
        print()
        print("Let's test likely bytes for movement commands...")
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        print("="*70)
        print("TESTING MOTOR 7")
        print("="*70)
        print("Watch Motor 7 during these tests!")
        print()
        
        # Test bytes around Motor 7 pattern (0x3c)
        motor_7_candidates = [0x3c, 0x7c, 0x5c, 0x2c, 0x6c, 0xbc]
        
        found_motor_7 = None
        for byte_val in motor_7_candidates:
            print(f"Byte 0x{byte_val:02x}: ", end='', flush=True)
            test_byte_for_motor(ser, byte_val, 7)
            print("  -> Did Motor 7 move? Or did a different motor move?")
            print()
            time.sleep(1)
        
        print("="*70)
        print("TESTING MOTOR 9")
        print("="*70)
        print("Watch Motor 9 during these tests!")
        print()
        
        # Test bytes around Motor 9 pattern (0x4c)
        motor_9_candidates = [0x4c, 0x8c, 0x6c, 0x5c, 0xac]
        
        found_motor_9 = None
        for byte_val in motor_9_candidates:
            print(f"Byte 0x{byte_val:02x}: ", end='', flush=True)
            test_byte_for_motor(ser, byte_val, 9)
            print("  -> Did Motor 9 move? Or did a different motor move?")
            print()
            time.sleep(1)
        
        ser.close()
        
        print("="*70)
        print("Please tell me which bytes moved which motors!")
        print("="*70)
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

