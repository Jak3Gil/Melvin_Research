#!/usr/bin/env python3
"""Scan wider CAN ID range to find all motors"""

import serial
import sys
import time

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def send_command(ser, cmd):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.2)
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.3:
            if ser.in_waiting > 0:
                response += ser.read(ser.in_waiting)
                time.sleep(0.02)
        return len(response) > 4
    except:
        return False

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    start_id = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    end_id = int(sys.argv[4]) if len(sys.argv) > 4 else 31
    
    print(f"Scanning CAN IDs {start_id} to {end_id} on {port} at {baud} baud...")
    
    ser = serial.Serial(port, baud, timeout=0.1)
    time.sleep(0.5)
    
    found = []
    for can_id in range(start_id, end_id + 1):
        cmd = build_activate_cmd(can_id)
        if send_command(ser, cmd):
            found.append(can_id)
            print(f"  Found: CAN ID {can_id} (0x{can_id:02X})")
    
    ser.close()
    
    print(f"\nFound {len(found)} motor(s): {found}")
    return 0

if __name__ == '__main__':
    sys.exit(main())

