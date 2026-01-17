#!/usr/bin/env python3
"""
Test Motor 2 via CAN bus on Jetson
Motor 2 is expected to be in ID range 16-20 (likely ID 16)
"""
import can
import struct
import time
import sys

def test_motor_can(motor_id, interface='can0'):
    """Test a single motor via direct CAN interface"""
    print(f"======================================================================")
    print(f"  Testing Motor 2 (CAN ID: {motor_id}) on {interface}")
    print(f"======================================================================\n")
    
    try:
        # Connect to CAN bus
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        print(f"✓ Connected to {interface}")
        print(f"  Bitrate: 500000 (configured)")
        print()
        
        # Test 1: Enable motor
        print("Test 1: Enabling motor...")
        msg = can.Message(
            arbitration_id=motor_id,
            data=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC],
            is_extended_id=False
        )
        bus.send(msg)
        time.sleep(0.1)
        
        # Check for response
        response = bus.recv(timeout=0.5)
        if response:
            print(f"✅ Motor responded! ID: 0x{response.arbitration_id:02X}")
            print(f"   Data: {response.data.hex()}")
        else:
            print("⚠️  No response to enable command")
        print()
        
        # Test 2: Request status
        print("Test 2: Requesting motor status...")
        msg = can.Message(
            arbitration_id=motor_id,
            data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            is_extended_id=False
        )
        bus.send(msg)
        time.sleep(0.1)
        
        response = bus.recv(timeout=0.5)
        if response:
            print(f"✅ Status received! ID: 0x{response.arbitration_id:02X}")
            print(f"   Data: {response.data.hex()}")
        else:
            print("⚠️  No status response")
        print()
        
        # Test 3: Small movement
        print("Test 3: Sending small movement command...")
        # Position control: small angle movement
        position = 0.1  # radians
        velocity = 1.0  # rad/s
        kp = 5.0
        kd = 0.5
        torque = 0.0
        
        # Pack command (MIT protocol format)
        pos_int = int((position + 12.5) * 65535 / 25.0)
        vel_int = int((velocity + 45.0) * 4095 / 90.0)
        kp_int = int(kp * 4095 / 500.0)
        kd_int = int(kd * 4095 / 5.0)
        torque_int = int((torque + 18.0) * 4095 / 36.0)
        
        data = bytearray(8)
        data[0] = (pos_int >> 8) & 0xFF
        data[1] = pos_int & 0xFF
        data[2] = (vel_int >> 4) & 0xFF
        data[3] = ((vel_int & 0x0F) << 4) | ((kp_int >> 8) & 0x0F)
        data[4] = kp_int & 0xFF
        data[5] = (kd_int >> 4) & 0xFF
        data[6] = ((kd_int & 0x0F) << 4) | ((torque_int >> 8) & 0x0F)
        data[7] = torque_int & 0xFF
        
        msg = can.Message(
            arbitration_id=motor_id,
            data=data,
            is_extended_id=False
        )
        bus.send(msg)
        time.sleep(0.5)
        
        response = bus.recv(timeout=0.5)
        if response:
            print(f"✅ Movement command acknowledged! ID: 0x{response.arbitration_id:02X}")
            print(f"   Data: {response.data.hex()}")
        else:
            print("⚠️  No response to movement command")
        print()
        
        # Test 4: Disable motor
        print("Test 4: Disabling motor...")
        msg = can.Message(
            arbitration_id=motor_id,
            data=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD],
            is_extended_id=False
        )
        bus.send(msg)
        time.sleep(0.1)
        
        response = bus.recv(timeout=0.5)
        if response:
            print(f"✅ Motor disabled! ID: 0x{response.arbitration_id:02X}")
        else:
            print("⚠️  No response to disable command")
        print()
        
        bus.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def scan_motor2_range(interface='can0'):
    """Scan the expected ID range for motor 2"""
    print(f"======================================================================")
    print(f"  Scanning Motor 2 ID Range (16-20) on {interface}")
    print(f"======================================================================\n")
    
    found_motors = []
    
    try:
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        print(f"✓ Connected to {interface}\n")
        
        for motor_id in range(16, 21):
            print(f"Testing ID {motor_id} (0x{motor_id:02X})...", end=" ")
            
            # Send enable command
            msg = can.Message(
                arbitration_id=motor_id,
                data=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC],
                is_extended_id=False
            )
            bus.send(msg)
            
            # Check for response
            response = bus.recv(timeout=0.2)
            if response and response.arbitration_id == motor_id:
                print(f"✅ FOUND!")
                found_motors.append(motor_id)
                
                # Disable it
                msg = can.Message(
                    arbitration_id=motor_id,
                    data=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD],
                    is_extended_id=False
                )
                bus.send(msg)
                time.sleep(0.1)
            else:
                print("No response")
            
            time.sleep(0.1)
        
        bus.shutdown()
        
        print(f"\n======================================================================")
        print(f"  Scan Results")
        print(f"======================================================================\n")
        
        if found_motors:
            print(f"✅ Found {len(found_motors)} motor(s): {found_motors}")
            return found_motors[0]  # Return first found motor
        else:
            print("❌ No motors found in range 16-20")
            return None
            
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        return None

def main():
    print("\n🤖 Motor 2 CAN Bus Test (Jetson)\n")
    
    # Check which interface to use
    interface = 'can0'
    if len(sys.argv) > 1:
        interface = sys.argv[1]
    
    print(f"Using CAN interface: {interface}")
    print(f"Make sure motor 2 is powered and connected!\n")
    
    # First, scan for motor 2
    print("Step 1: Scanning for Motor 2...\n")
    motor_id = scan_motor2_range(interface)
    
    if motor_id:
        print(f"\n\nStep 2: Testing Motor 2 (ID {motor_id})...\n")
        test_motor_can(motor_id, interface)
        print("\n✅ Test complete!")
    else:
        print("\n❌ Could not find Motor 2")
        print("\nTroubleshooting:")
        print("  1. Check motor power")
        print("  2. Verify CAN wiring (CAN-H, CAN-L)")
        print("  3. Try the other interface: python3 test_motor2_can.py can1")
        print("  4. Check CAN bitrate: ip -details link show can0")

if __name__ == "__main__":
    main()

