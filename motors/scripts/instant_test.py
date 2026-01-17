#!/usr/bin/env python3
"""Instant Motor 2 test via USB-to-CAN (L91 protocol)"""
import serial, struct, time

# Motor 2 is expected to be at CAN ID 16-20 (likely 16)
MOTOR_ID = 16

try:
    ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0.5)
    print(f"Testing Motor 2 (ID {MOTOR_ID}) at 921600 baud via L91...")
    print()

    # Enable motor 2
    print("1. Enabling motor...")
    packet = bytearray([0xAA, 0x55, 0x01, MOTOR_ID])
    packet.extend(struct.pack('<I', MOTOR_ID))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)

    ser.write(packet)
    time.sleep(0.3)
    response = ser.read(100)

    if response:
        print(f"   ✅ MOTOR 2 RESPONDED! {len(response)} bytes: {response.hex()}")
        print()
        
        # Try a small movement
        print("2. Testing small movement...")
        packet = bytearray([0xAA, 0x55, 0x01, MOTOR_ID])
        packet.extend(struct.pack('<I', MOTOR_ID))
        # Position=0.0, Velocity=1.0, Kp=5.0, Kd=0.5, Torque=0.0
        packet.extend(struct.pack('<fffff', 0.0, 1.0, 5.0, 0.5, 0.0))
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(0.5)
        response = ser.read(100)
        
        if response:
            print(f"   ✅ Movement response: {response.hex()}")
        print()
        
        # Disable motor
        print("3. Disabling motor...")
        packet = bytearray([0xAA, 0x55, 0x01, MOTOR_ID])
        packet.extend(struct.pack('<I', MOTOR_ID))
        packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(0.2)
        response = ser.read(100)
        print(f"   ✅ Motor disabled")
        print()
        
        print("🎉 MOTOR 2 IS WORKING!")
        print(f"   Motor 2 confirmed at CAN ID: {MOTOR_ID}\n")
    else:
        print("   ❌ No response from Motor 2")
        print(f"   Trying to scan IDs 16-20...\n")
        
        # Scan for motor 2
        for test_id in range(16, 21):
            print(f"   Testing ID {test_id}...", end=" ")
            packet = bytearray([0xAA, 0x55, 0x01, test_id])
            packet.extend(struct.pack('<I', test_id))
            packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            packet.append(sum(packet[2:]) & 0xFF)
            
            ser.write(packet)
            time.sleep(0.2)
            response = ser.read(100)
            
            if response:
                print(f"✅ FOUND! ({len(response)} bytes)")
                print(f"\n   Motor 2 is at CAN ID: {test_id}\n")
                break
            else:
                print("No response")
            time.sleep(0.1)

    ser.close()

except serial.SerialException as e:
    print(f"❌ Cannot open /dev/ttyUSB0: {e}")
    print()
    print("Troubleshooting:")
    print("  1. Is USB-to-CAN adapter plugged into Jetson?")
    print("  2. Check: ls -la /dev/ttyUSB*")
    print("  3. Check permissions: sudo chmod 666 /dev/ttyUSB0")
    print()

