#!/usr/bin/env python3
"""
Emergency Stop - Deactivate and stop ALL motors
Sends stop commands to all CAN IDs to unfreeze motors
"""

import serial
import sys
import time

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_stop_cmd(can_id):
    """Stop movement command"""
    speed_val = 0x7fff  # Zero speed
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, 0])  # flag=0 for stop
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd):
    try:
        ser.write(cmd)
        ser.flush()
        time.sleep(0.02)
    except:
        pass

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("EMERGENCY STOP - Stopping and Deactivating ALL Motors")
    print("="*70)
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.2)
        print("\n[OK] Serial port opened\n")
        
        # Send stop commands to all possible IDs
        print("Sending STOP commands to all CAN IDs (1-31)...")
        for can_id in range(1, 32):
            send_command(ser, build_stop_cmd(can_id))
        
        time.sleep(0.5)
        print("  [DONE] Stop commands sent")
        
        # Send deactivate commands to all IDs
        print("\nSending DEACTIVATE commands to all CAN IDs (1-31)...")
        for can_id in range(1, 32):
            send_command(ser, build_deactivate_cmd(can_id))
        
        time.sleep(0.5)
        print("  [DONE] Deactivate commands sent")
        
        # Send stop commands again for good measure
        print("\nSending STOP commands again...")
        for can_id in range(1, 32):
            send_command(ser, build_stop_cmd(can_id))
        
        time.sleep(0.5)
        print("  [DONE] Second stop commands sent")
        
        # Deactivate again
        print("\nSending DEACTIVATE commands again...")
        for can_id in range(1, 32):
            send_command(ser, build_deactivate_cmd(can_id))
        
        time.sleep(0.5)
        
        ser.close()
        
        print("\n" + "="*70)
        print("[OK] All motors should now be stopped and deactivated")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

