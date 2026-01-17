#!/usr/bin/env python3
"""
EMERGENCY STOP - Disable All Motors Immediately
Run this to stop all motors!
"""
import serial
import time

PORT = '/dev/ttyUSB0'
BAUD = 921600

def build_deactivate_cmd(can_id):
    """Build L91 deactivate command"""
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_stop_cmd(can_id):
    """Build L91 stop command (speed = 0)"""
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, 0x01])
    cmd.extend([0x00, 0x00, 0x0d, 0x0a])  # Speed = 0
    return bytes(cmd)

def emergency_stop(ser):
    """Emergency stop - disable all known motors"""
    print("EMERGENCY STOP - Disabling all motors...")
    
    # Known motor IDs from scan
    motor_ids = list(range(40, 64)) + list(range(80, 120))
    
    # First, try to stop (speed = 0) on primary IDs
    primary_ids = [40, 80]
    for motor_id in primary_ids:
        print(f"Stopping motor at ID {motor_id}...")
        try:
            # Stop command (speed = 0)
            cmd = build_stop_cmd(motor_id)
            ser.write(cmd)
            time.sleep(0.1)
        except:
            pass
    
    # Then disable all motors
    print("Disabling all motors...")
    for motor_id in motor_ids:
        try:
            cmd = build_deactivate_cmd(motor_id)
            ser.write(cmd)
            time.sleep(0.01)  # Small delay
        except:
            pass
    
    time.sleep(0.2)
    
    # Disable primary IDs again to be sure
    for motor_id in primary_ids:
        try:
            cmd = build_deactivate_cmd(motor_id)
            ser.write(cmd)
            time.sleep(0.05)
        except:
            pass
    
    print("✓ Emergency stop complete")

def main():
    print("="*70)
    print("  EMERGENCY STOP - ALL MOTORS")
    print("="*70)
    print()
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"✓ Connected to {PORT}")
        print()
        
        emergency_stop(ser)
        
        ser.close()
        print()
        print("All motors should now be stopped and disabled.")
        print()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        print("Try unplugging USB-to-CAN adapter to stop motors!")
        print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

