#!/usr/bin/env python3
"""
Scan ALL CAN IDs (1-127) using correct AT protocol
"""
import serial
import sys
import time

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def main():
    print("\n🔍 Complete CAN ID Scanner - AT Protocol\n")
    
    port = '/dev/ttyUSB1'
    baudrate = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    print(f"Scanning: IDs 1-127\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"✓ Connected\n")
        
        # Send AT+AT
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        time.sleep(0.3)
        response = ser.read(100)
        if response:
            print(f"Adapter: {response.decode('utf-8', errors='ignore').strip()}\n")
        
        print("=" * 70)
        print("SCANNING...")
        print("=" * 70)
        
        found = []
        
        for can_id in range(1, 128):
            if can_id % 10 == 0:
                print(f"  Progress: {can_id}/127 ({int(can_id/127*100)}%)")
            
            ser.reset_input_buffer()
            cmd = build_activate_cmd(can_id)
            ser.write(cmd)
            ser.flush()
            time.sleep(0.15)
            
            response = ser.read(100)
            if response and len(response) > 0:
                print(f"\n  ✅ FOUND MOTOR at ID {can_id} (0x{can_id:02X})")
                print(f"     Response: {response.hex()}\n")
                found.append(can_id)
        
        ser.close()
        
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        
        if found:
            print(f"\n✅ Found {len(found)} motor(s): {found}")
            print(f"\nMotor 2 is at ID: {found[0] if found else 'NOT FOUND'}")
        else:
            print("\n❌ NO MOTORS FOUND")
            print("\nThis means:")
            print("  1. Motor is NOT powered")
            print("  2. CAN wiring is NOT connected (CAN-H, CAN-L, GND)")
            print("  3. Missing 120Ω termination resistor")
            print("  4. Motor is connected to different adapter/port")
            print("\nDouble-check:")
            print("  - Motor LED is ON")
            print("  - CAN-H wire connected")
            print("  - CAN-L wire connected")
            print("  - Ground wire connected")
            print("  - 120Ω resistor between CAN-H and CAN-L")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

