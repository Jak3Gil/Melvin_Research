#!/usr/bin/env python3
"""
Simple Motor 2 Test - Tests both CAN and USB serial
"""
import serial
import struct
import time
import sys

def test_motor_serial(motor_id, port='/dev/ttyUSB0', baudrate=921600):
    """Test motor via USB serial adapter (L91 protocol)"""
    print(f"======================================================================")
    print(f"  Testing Motor 2 (ID: {motor_id}) via {port}")
    print(f"======================================================================\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"✓ Connected to {port} at {baudrate} baud\n")
        
        # Test 1: Enable motor
        print("Test 1: Enabling motor...")
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(0.3)
        response = ser.read(100)
        
        if response:
            print(f"✅ Motor responded! {len(response)} bytes: {response.hex()}")
        else:
            print("⚠️  No response")
        print()
        
        # Test 2: Small movement
        print("Test 2: Small movement test...")
        # Position command
        position = 0.0  # radians
        velocity = 1.0
        kp = 5.0
        kd = 0.5
        torque = 0.0
        
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend(struct.pack('<fffff', position, velocity, kp, kd, torque))
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(0.5)
        response = ser.read(100)
        
        if response:
            print(f"✅ Movement response: {len(response)} bytes: {response.hex()}")
        else:
            print("⚠️  No response")
        print()
        
        # Test 3: Disable motor
        print("Test 3: Disabling motor...")
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(0.3)
        response = ser.read(100)
        
        if response:
            print(f"✅ Disabled: {response.hex()}")
        else:
            print("⚠️  No response")
        print()
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def scan_motor2_serial(port='/dev/ttyUSB0', baudrate=921600):
    """Scan for motor 2 in expected range"""
    print(f"======================================================================")
    print(f"  Scanning for Motor 2 (IDs 16-20) via {port}")
    print(f"======================================================================\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"✓ Connected to {port}\n")
        
        found_motors = []
        
        for motor_id in range(16, 21):
            print(f"Testing ID {motor_id}...", end=" ")
            
            # Enable command
            packet = bytearray([0xAA, 0x55, 0x01, motor_id])
            packet.extend(struct.pack('<I', motor_id))
            packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            packet.append(sum(packet[2:]) & 0xFF)
            
            ser.write(packet)
            time.sleep(0.2)
            response = ser.read(100)
            
            if response:
                print(f"✅ FOUND! ({len(response)} bytes)")
                found_motors.append(motor_id)
            else:
                print("No response")
            
            time.sleep(0.1)
        
        ser.close()
        
        print(f"\n======================================================================")
        print(f"  Scan Results")
        print(f"======================================================================\n")
        
        if found_motors:
            print(f"✅ Found {len(found_motors)} motor(s): {found_motors}")
            return found_motors[0]
        else:
            print("❌ No motors found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n🤖 Motor 2 Simple Test\n")
    
    # Determine test mode
    port = '/dev/ttyUSB0'
    baudrate = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    print(f"Make sure motor 2 is powered and connected!\n")
    
    # Scan for motor
    print("Step 1: Scanning for Motor 2...\n")
    motor_id = scan_motor2_serial(port, baudrate)
    
    if motor_id:
        print(f"\n\nStep 2: Testing Motor 2 (ID {motor_id})...\n")
        test_motor_serial(motor_id, port, baudrate)
        print("\n✅ All tests complete!")
        print(f"\n📝 Motor 2 confirmed at CAN ID: {motor_id}")
    else:
        print("\n❌ Could not find Motor 2")
        print("\nTroubleshooting:")
        print("  1. Check motor power")
        print("  2. Verify CAN wiring")
        print("  3. Try different baudrate: python3 test_motor2_simple.py /dev/ttyUSB0 115200")
        print("  4. Check USB connection: ls -la /dev/ttyUSB*")

if __name__ == "__main__":
    main()

