#!/usr/bin/env python3
"""
Test L91 activation on motors 5-14
Try L91 commands directly - maybe they DO support L91!
"""
import serial
import struct
import time
import sys

def activate_motor_l91(ser, motor_id):
    """Send L91 activation command - same format as working motors"""
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    
    ser.write(packet)
    time.sleep(0.3)
    response = ser.read(100)
    return response

if __name__ == "__main__":
    port = 'COM6'  # Your COM port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    try:
        ser = serial.Serial(port, 921600, timeout=0.5)
        print("="*60)
        print("Testing L91 Activation on Motors 5-14")
        print("="*60)
        print(f"Port: {port} at 921600 baud\n")
        
        # Motors that Motor Studio sees (CANopen protocol)
        motor_studio_motors = [5, 6, 7, 10, 11, 12, 13, 14]
        
        found = []
        for motor_id in motor_studio_motors:
            print(f"Motor {motor_id:2d}: ", end='', flush=True)
            response = activate_motor_l91(ser, motor_id)
            if response and len(response) > 0:
                print(f"RESPONDED! ({len(response)} bytes: {response.hex()[:50]}...)")
                found.append(motor_id)
            else:
                print("No response")
            time.sleep(0.2)
        
        ser.close()
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        if found:
            print(f"\nSUCCESS! {len(found)} motor(s) responded to L91:")
            for motor_id in found:
                print(f"  - Motor {motor_id}")
            print("\nThese motors DO support L91 protocol!")
        else:
            print("\nNo motors responded to L91 commands.")
            print("They may only support CANopen protocol.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

