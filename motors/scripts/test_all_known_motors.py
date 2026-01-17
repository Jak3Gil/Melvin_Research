#!/usr/bin/env python3
"""
Test all known motors using the protocols that work:
- L91 protocol (0xAA 0x55) for motors 1, 2, 4, 8, 9
- Motor Studio AT commands for motors 5, 6, 7, 10, 11, 12, 13, 14
"""
import serial
import struct
import time
import sys

def activate_motor_l91(ser, motor_id):
    """Send L91 activation command"""
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    
    ser.write(packet)
    time.sleep(0.3)
    response = ser.read(100)
    return response

def initialize_motor_studio(ser):
    """Initialize Motor Studio adapter with AT+AT"""
    cmd = bytes.fromhex("41542b41540d0a")  # AT+AT + CRLF
    ser.write(cmd)
    time.sleep(0.3)
    response = ser.read(100)
    return response

def activate_motor_at(ser, motor_id):
    """Send Motor Studio AT activation command"""
    # Format: AT + 00 07 + e8 + [motor_id] + 01 00 + CRLF
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    time.sleep(0.3)
    response = ser.read(100)
    return response

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    try:
        ser = serial.Serial(port, 921600, timeout=0.5)
        print("="*70)
        print("TESTING ALL KNOWN MOTORS")
        print("="*70)
        print(f"Port: {port} at 921600 baud\n")
        
        # Motors that work with L91 protocol
        l91_motors = [1, 2, 4, 8, 9]
        # Motors visible in Motor Studio (CANopen/AT protocol)
        at_motors = [5, 6, 7, 10, 11, 12, 13, 14]
        
        found_l91 = []
        found_at = []
        
        # Test L91 motors
        print("Testing L91 Protocol Motors (1, 2, 4, 8, 9):")
        print("-" * 70)
        for motor_id in l91_motors:
            print(f"Motor {motor_id:2d}: ", end='', flush=True)
            response = activate_motor_l91(ser, motor_id)
            if response and len(response) > 0:
                print(f"RESPONDED! ({len(response)} bytes: {response.hex()[:50]}...)")
                found_l91.append(motor_id)
            else:
                print("No response")
            time.sleep(0.2)
        
        print()
        
        # Initialize Motor Studio adapter
        print("Initializing Motor Studio adapter (AT+AT)...")
        init_response = initialize_motor_studio(ser)
        if init_response:
            print(f"  Adapter initialized ({len(init_response)} bytes)")
        else:
            print("  No initialization response (may still work)")
        print()
        
        # Test AT motors
        print("Testing Motor Studio AT Protocol Motors (5, 6, 7, 10, 11, 12, 13, 14):")
        print("-" * 70)
        for motor_id in at_motors:
            print(f"Motor {motor_id:2d}: ", end='', flush=True)
            response = activate_motor_at(ser, motor_id)
            if response and len(response) > 0:
                print(f"RESPONDED! ({len(response)} bytes: {response.hex()[:50]}...)")
                found_at.append(motor_id)
            else:
                print("No response")
            time.sleep(0.2)
        
        ser.close()
        
        # Summary
        print("\n" + "="*70)
        print("RESULTS SUMMARY")
        print("="*70)
        
        print(f"\nL91 Protocol Motors:")
        if found_l91:
            print(f"  Found {len(found_l91)}/{len(l91_motors)} motors:")
            for motor_id in found_l91:
                print(f"    - Motor {motor_id}")
        else:
            print(f"  No L91 motors responded")
        
        print(f"\nMotor Studio AT Protocol Motors:")
        if found_at:
            print(f"  Found {len(found_at)}/{len(at_motors)} motors:")
            for motor_id in found_at:
                print(f"    - Motor {motor_id}")
        else:
            print(f"  No AT protocol motors responded")
        
        total_found = len(found_l91) + len(found_at)
        total_test = len(l91_motors) + len(at_motors)
        print(f"\nTOTAL: {total_found}/{total_test} motors responded")
        
        if total_found == total_test:
            print("\nSUCCESS! All known motors are responding!")
        elif total_found > 0:
            print(f"\nPARTIAL: {total_found} motors responding, {total_test - total_found} not responding")
        else:
            print("\nWARNING: No motors responded - check connections and port")
        
    except serial.SerialException as e:
        print(f"Error: Cannot open {port}: {e}")
        print("\nTroubleshooting:")
        print("  1. Is the USB-to-CAN adapter connected?")
        print("  2. Is COM6 the correct port?")
        print("  3. Close Motor Studio if it's using the port")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

