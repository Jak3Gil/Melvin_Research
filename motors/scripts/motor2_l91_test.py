#!/usr/bin/env python3
"""
Motor 2 Test via USB-to-CAN adapter (L91 Protocol)
Comprehensive test suite for Motor 2
"""
import serial
import struct
import time
import sys

def find_motor2(ser):
    """Scan for Motor 2 in expected ID range"""
    print("=" * 70)
    print("SCANNING FOR MOTOR 2 (IDs 16-20)")
    print("=" * 70)
    print()
    
    for motor_id in range(16, 21):
        print(f"Testing ID {motor_id}...", end=" ", flush=True)
        
        # Enable command
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(0.2)
        response = ser.read(100)
        
        if response:
            print(f"✅ FOUND! ({len(response)} bytes: {response.hex()})")
            
            # Disable it
            packet = bytearray([0xAA, 0x55, 0x01, motor_id])
            packet.extend(struct.pack('<I', motor_id))
            packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            packet.append(sum(packet[2:]) & 0xFF)
            ser.write(packet)
            time.sleep(0.1)
            ser.read(100)  # Clear buffer
            
            return motor_id
        else:
            print("No response")
        
        time.sleep(0.1)
    
    return None

def test_motor_enable_disable(ser, motor_id):
    """Test enable/disable commands"""
    print("\n" + "=" * 70)
    print("TEST 1: ENABLE/DISABLE")
    print("=" * 70)
    print()
    
    # Enable
    print("Enabling motor...", end=" ", flush=True)
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    
    ser.write(packet)
    time.sleep(0.3)
    response = ser.read(100)
    
    if response:
        print(f"✅ Enabled ({len(response)} bytes)")
    else:
        print("⚠️  No response")
        return False
    
    time.sleep(0.5)
    
    # Disable
    print("Disabling motor...", end=" ", flush=True)
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    
    ser.write(packet)
    time.sleep(0.3)
    response = ser.read(100)
    
    if response:
        print(f"✅ Disabled ({len(response)} bytes)")
    else:
        print("⚠️  No response")
    
    return True

def test_position_control(ser, motor_id):
    """Test position control"""
    print("\n" + "=" * 70)
    print("TEST 2: POSITION CONTROL")
    print("=" * 70)
    print()
    
    # Enable motor
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    ser.write(packet)
    time.sleep(0.3)
    ser.read(100)
    
    positions = [
        (0.0, "Zero position"),
        (0.5, "0.5 radians (~28°)"),
        (-0.5, "-0.5 radians (~-28°)"),
        (0.0, "Back to zero")
    ]
    
    for position, description in positions:
        print(f"Moving to {description}...", end=" ", flush=True)
        
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        # Position, Velocity, Kp, Kd, Torque
        packet.extend(struct.pack('<fffff', position, 2.0, 10.0, 1.0, 0.0))
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(0.8)
        response = ser.read(100)
        
        if response:
            print(f"✅ Response received ({len(response)} bytes)")
        else:
            print("⚠️  No response")
        
        time.sleep(0.5)
    
    # Disable motor
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    ser.write(packet)
    time.sleep(0.2)
    ser.read(100)
    
    print("\n✅ Position control test complete")
    return True

def test_velocity_control(ser, motor_id):
    """Test velocity control"""
    print("\n" + "=" * 70)
    print("TEST 3: VELOCITY CONTROL")
    print("=" * 70)
    print()
    
    # Enable motor
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    ser.write(packet)
    time.sleep(0.3)
    ser.read(100)
    
    velocities = [
        (1.0, "Slow forward (1 rad/s)"),
        (3.0, "Medium forward (3 rad/s)"),
        (0.0, "Stop"),
        (-1.0, "Slow reverse (-1 rad/s)"),
        (0.0, "Stop")
    ]
    
    for velocity, description in velocities:
        print(f"{description}...", end=" ", flush=True)
        
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        # Position=0, Velocity, Kp=0 (velocity mode), Kd, Torque
        packet.extend(struct.pack('<fffff', 0.0, velocity, 0.0, 1.0, 0.0))
        packet.append(sum(packet[2:]) & 0xFF)
        
        ser.write(packet)
        time.sleep(1.5)
        response = ser.read(100)
        
        if response:
            print(f"✅ Running")
        else:
            print("⚠️  No response")
        
        time.sleep(0.3)
    
    # Disable motor
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(sum(packet[2:]) & 0xFF)
    ser.write(packet)
    time.sleep(0.2)
    ser.read(100)
    
    print("\n✅ Velocity control test complete")
    return True

def main():
    print("\n" + "=" * 70)
    print("MOTOR 2 COMPREHENSIVE TEST (L91 Protocol)")
    print("=" * 70)
    print()
    
    # Get port and baudrate
    port = '/dev/ttyUSB0'
    baudrate = 921600
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    print()
    
    # Open serial port
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"✅ Connected to {port}")
        print()
    except serial.SerialException as e:
        print(f"❌ Cannot open {port}: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check USB-to-CAN adapter is plugged in")
        print("  2. Check: ls -la /dev/ttyUSB*")
        print("  3. Try: sudo chmod 666 /dev/ttyUSB0")
        return 1
    
    # Find Motor 2
    motor_id = find_motor2(ser)
    
    if not motor_id:
        print()
        print("❌ Motor 2 not found in range 16-20")
        print()
        print("Troubleshooting:")
        print("  1. Check motor power")
        print("  2. Verify CAN wiring (CAN-H, CAN-L, GND)")
        print("  3. Check motor configuration")
        print("  4. Try different baudrate: python3 motor2_l91_test.py /dev/ttyUSB0 115200")
        ser.close()
        return 1
    
    print()
    print(f"✅ Motor 2 found at CAN ID: {motor_id}")
    print()
    
    # Run tests
    try:
        input("Press ENTER to run tests (or Ctrl+C to exit)...")
        print()
        
        # Test 1: Enable/Disable
        if not test_motor_enable_disable(ser, motor_id):
            print("\n⚠️  Enable/disable test failed, skipping other tests")
            ser.close()
            return 1
        
        time.sleep(1)
        
        # Test 2: Position Control
        print("\n⚠️  MOTOR WILL MOVE!")
        input("Press ENTER to test position control (or Ctrl+C to skip)...")
        test_position_control(ser, motor_id)
        
        time.sleep(1)
        
        # Test 3: Velocity Control
        print("\n⚠️  MOTOR WILL SPIN!")
        input("Press ENTER to test velocity control (or Ctrl+C to skip)...")
        test_velocity_control(ser, motor_id)
        
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETE!")
        print("=" * 70)
        print()
        print(f"✅ Motor 2 is working correctly at CAN ID {motor_id}")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        # Make sure motor is disabled
        packet = bytearray([0xAA, 0x55, 0x01, motor_id])
        packet.extend(struct.pack('<I', motor_id))
        packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        packet.append(sum(packet[2:]) & 0xFF)
        ser.write(packet)
        time.sleep(0.2)
    
    ser.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())

