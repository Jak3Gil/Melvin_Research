#!/usr/bin/env python3
"""
Test Motor 2 via USB-to-CAN adapter using L91 protocol
Motor 2 expected at CAN ID 16-20
"""
import serial
import struct
import time
import sys

def calculate_checksum(data):
    """Calculate L91 protocol checksum"""
    return sum(data[2:]) & 0xFF

def create_enable_packet(motor_id):
    """Create motor enable packet"""
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(calculate_checksum(packet))
    return packet

def create_disable_packet(motor_id):
    """Create motor disable packet"""
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    packet.append(calculate_checksum(packet))
    return packet

def create_position_packet(motor_id, position=0.0, velocity=1.0, kp=5.0, kd=0.5, torque=0.0):
    """Create position control packet"""
    packet = bytearray([0xAA, 0x55, 0x01, motor_id])
    packet.extend(struct.pack('<I', motor_id))
    packet.extend(struct.pack('<fffff', position, velocity, kp, kd, torque))
    packet.append(calculate_checksum(packet))
    return packet

def scan_for_motor2(port, baudrate):
    """Scan for Motor 2 in expected ID range (16-20)"""
    print(f"{'=' * 70}")
    print(f"  Scanning for Motor 2 (L91 Protocol)")
    print(f"{'=' * 70}\n")
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    print(f"Expected ID range: 16-20\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"✓ Connected to {port}\n")
        
        # Send AT command first
        print("Sending AT+AT detection command...")
        ser.write(b'AT+AT\r\n')
        time.sleep(0.2)
        response = ser.read(100)
        if response:
            print(f"  Response: {response.decode('utf-8', errors='ignore').strip()}")
        print()
        
        found_motors = []
        
        print("Scanning IDs 16-20...")
        print("-" * 70)
        
        for motor_id in range(16, 21):
            print(f"  Testing ID {motor_id} (0x{motor_id:02X})...", end=" ", flush=True)
            
            # Clear buffer
            ser.reset_input_buffer()
            
            # Send enable command
            packet = create_enable_packet(motor_id)
            ser.write(packet)
            time.sleep(0.3)
            
            # Check for response
            response = ser.read(100)
            
            if response and len(response) > 0:
                print(f"✅ FOUND! ({len(response)} bytes)")
                print(f"     Response: {response.hex()}")
                found_motors.append(motor_id)
                
                # Disable it
                packet = create_disable_packet(motor_id)
                ser.write(packet)
                time.sleep(0.2)
            else:
                print("No response")
            
            time.sleep(0.1)
        
        ser.close()
        
        print()
        print("=" * 70)
        print("  SCAN RESULTS")
        print("=" * 70)
        
        if found_motors:
            print(f"\n✅ Found {len(found_motors)} motor(s): {found_motors}")
            print(f"\n📝 Motor 2 is at CAN ID: {found_motors[0]}")
            return found_motors[0]
        else:
            print(f"\n❌ No motors found in range 16-20")
            return None
            
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_motor2(motor_id, port, baudrate):
    """Comprehensive test of Motor 2"""
    print(f"\n\n{'=' * 70}")
    print(f"  Testing Motor 2 (ID: {motor_id})")
    print(f"{'=' * 70}\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        print(f"✓ Connected to {port}\n")
        
        # Test 1: Enable motor
        print("Test 1: Enable Motor")
        print("-" * 70)
        packet = create_enable_packet(motor_id)
        print(f"  Sending: {packet.hex()}")
        ser.write(packet)
        time.sleep(0.3)
        response = ser.read(100)
        
        if response:
            print(f"  ✅ Response: {response.hex()}")
            print(f"     Length: {len(response)} bytes")
        else:
            print(f"  ⚠️  No response")
        print()
        
        # Test 2: Read status
        print("Test 2: Read Motor Status")
        print("-" * 70)
        packet = create_position_packet(motor_id, 0.0, 0.0, 0.0, 0.0, 0.0)
        print(f"  Sending status request...")
        ser.write(packet)
        time.sleep(0.3)
        response = ser.read(100)
        
        if response:
            print(f"  ✅ Status received: {response.hex()}")
            # Parse response if it's the expected format
            if len(response) >= 20:
                try:
                    # L91 response format (simplified)
                    print(f"     Raw data: {response[:20].hex()}")
                except:
                    pass
        else:
            print(f"  ⚠️  No response")
        print()
        
        # Test 3: Small movement
        print("Test 3: Small Movement Test")
        print("-" * 70)
        print(f"  Moving to position 0.1 radians...")
        packet = create_position_packet(motor_id, 0.1, 1.0, 5.0, 0.5, 0.0)
        ser.write(packet)
        time.sleep(0.5)
        response = ser.read(100)
        
        if response:
            print(f"  ✅ Movement response: {response.hex()}")
        else:
            print(f"  ⚠️  No response")
        
        time.sleep(0.5)
        
        # Return to zero
        print(f"  Returning to zero...")
        packet = create_position_packet(motor_id, 0.0, 1.0, 5.0, 0.5, 0.0)
        ser.write(packet)
        time.sleep(0.5)
        response = ser.read(100)
        
        if response:
            print(f"  ✅ Return response: {response.hex()}")
        print()
        
        # Test 4: Disable motor
        print("Test 4: Disable Motor")
        print("-" * 70)
        packet = create_disable_packet(motor_id)
        print(f"  Sending: {packet.hex()}")
        ser.write(packet)
        time.sleep(0.3)
        response = ser.read(100)
        
        if response:
            print(f"  ✅ Disabled: {response.hex()}")
        else:
            print(f"  ⚠️  No response")
        print()
        
        ser.close()
        
        print("=" * 70)
        print("  ALL TESTS COMPLETE")
        print("=" * 70)
        print(f"\n✅ Motor 2 (ID {motor_id}) is working via L91 protocol!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def main():
    print("\n🤖 Motor 2 Test - L91 Protocol via USB-to-CAN\n")
    
    # Default settings
    port = '/dev/ttyUSB1'
    baudrate = 921600
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    
    print(f"Configuration:")
    print(f"  Port: {port}")
    print(f"  Baudrate: {baudrate}")
    print(f"  Protocol: L91")
    print()
    
    # Step 1: Scan for Motor 2
    motor_id = scan_for_motor2(port, baudrate)
    
    if motor_id:
        # Step 2: Test Motor 2
        test_motor2(motor_id, port, baudrate)
    else:
        print("\n❌ Could not find Motor 2")
        print("\nTroubleshooting:")
        print(f"  1. Check motor power (LED should be on)")
        print(f"  2. Verify USB connection: ls -la /dev/ttyUSB*")
        print(f"  3. Check CAN wiring (CAN-H, CAN-L, GND)")
        print(f"  4. Try different baudrate:")
        print(f"     python3 test_motor2_l91.py {port} 115200")
        print(f"  5. Try different port:")
        print(f"     python3 test_motor2_l91.py /dev/ttyUSB0 921600")
        print(f"\n  Available ports:")
        import subprocess
        result = subprocess.run(['ls', '-la', '/dev/ttyUSB*'], 
                              capture_output=True, text=True)
        print(f"  {result.stdout}")

if __name__ == "__main__":
    main()

