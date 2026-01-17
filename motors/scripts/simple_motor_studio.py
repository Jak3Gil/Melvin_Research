#!/usr/bin/env python3
"""
Simple Motor Studio Alternative
Configure and test Robstride motors without Motor Studio software
"""

import serial
import struct
import time
import sys

class SimpleMotorStudio:
    def __init__(self, port='COM3', baudrate=921600):
        """Initialize connection to motors"""
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"✓ Connected to {port} at {baudrate} baud")
            time.sleep(0.5)
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            sys.exit(1)
    
    def send_command(self, motor_id, command_type, data=None):
        """Send L91 protocol command to motor"""
        # L91 Protocol format: [0xFE, 0xEE, motor_id, data_len, command, data..., checksum]
        if data is None:
            data = []
        
        packet = [0xFE, 0xEE, motor_id, len(data) + 1, command_type] + data
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        self.ser.write(bytes(packet))
        time.sleep(0.05)
        
        # Read response
        response = self.ser.read(100)
        return response
    
    def scan_motors(self, start_id=1, end_id=31):
        """Scan for motors in ID range"""
        print(f"\n🔍 Scanning for motors (ID {start_id}-{end_id})...")
        found_motors = []
        
        for motor_id in range(start_id, end_id + 1):
            # Try to read motor status (command 0x9A)
            response = self.send_command(motor_id, 0x9A)
            
            if len(response) > 5 and response[0] == 0xFE and response[1] == 0xEE:
                print(f"  ✓ Found motor at ID {motor_id}")
                found_motors.append(motor_id)
            else:
                print(f"  - No motor at ID {motor_id}", end='\r')
        
        print("\n")
        return found_motors
    
    def change_motor_id(self, old_id, new_id):
        """Change motor CAN ID"""
        print(f"\n🔧 Changing motor ID from {old_id} to {new_id}...")
        
        # L91 command to change ID (command 0x79, data: new_id)
        response = self.send_command(old_id, 0x79, [new_id])
        
        if len(response) > 0:
            print(f"  ✓ Command sent. Please power cycle the motor.")
            print(f"  ⚠️  IMPORTANT: Turn motor power OFF then ON for change to take effect")
            return True
        else:
            print(f"  ✗ Failed to change ID")
            return False
    
    def enable_motor(self, motor_id):
        """Enable motor (release brake)"""
        print(f"\n▶️  Enabling motor {motor_id}...")
        response = self.send_command(motor_id, 0x88)
        if len(response) > 0:
            print(f"  ✓ Motor {motor_id} enabled")
            return True
        return False
    
    def disable_motor(self, motor_id):
        """Disable motor (engage brake)"""
        print(f"\n⏸️  Disabling motor {motor_id}...")
        response = self.send_command(motor_id, 0x80)
        if len(response) > 0:
            print(f"  ✓ Motor {motor_id} disabled")
            return True
        return False
    
    def test_motor_movement(self, motor_id):
        """Test motor with small movement"""
        print(f"\n🔄 Testing motor {motor_id} movement...")
        
        # Enable motor first
        self.enable_motor(motor_id)
        time.sleep(0.5)
        
        # Send position command (command 0xA6)
        # Position: 0 degrees (center), velocity: 5 deg/s, torque: 1 Nm
        position = 0  # degrees
        velocity = 5  # deg/s
        torque = 100  # 0.01 Nm units (1 Nm)
        
        # Pack data (simplified - adjust based on actual L91 protocol)
        data = [
            (position >> 8) & 0xFF, position & 0xFF,
            (velocity >> 8) & 0xFF, velocity & 0xFF,
            (torque >> 8) & 0xFF, torque & 0xFF
        ]
        
        response = self.send_command(motor_id, 0xA6, data)
        
        if len(response) > 0:
            print(f"  ✓ Motor {motor_id} command sent")
            time.sleep(2)
            
            # Disable motor
            self.disable_motor(motor_id)
            return True
        else:
            print(f"  ✗ Failed to move motor {motor_id}")
            return False
    
    def interactive_menu(self):
        """Interactive menu for motor configuration"""
        while True:
            print("\n" + "="*50)
            print("  🔧 Simple Motor Studio")
            print("="*50)
            print("1. Scan for motors")
            print("2. Change motor ID")
            print("3. Enable motor")
            print("4. Disable motor")
            print("5. Test motor movement")
            print("6. Exit")
            print("="*50)
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                self.scan_motors()
            
            elif choice == '2':
                old_id = int(input("Enter current motor ID: "))
                new_id = int(input("Enter new motor ID (1-31): "))
                if 1 <= new_id <= 31:
                    self.change_motor_id(old_id, new_id)
                else:
                    print("❌ Invalid ID. Must be 1-31")
            
            elif choice == '3':
                motor_id = int(input("Enter motor ID to enable: "))
                self.enable_motor(motor_id)
            
            elif choice == '4':
                motor_id = int(input("Enter motor ID to disable: "))
                self.disable_motor(motor_id)
            
            elif choice == '5':
                motor_id = int(input("Enter motor ID to test: "))
                self.test_motor_movement(motor_id)
            
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
    
    def close(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Connection closed")


def main():
    print("="*50)
    print("  Simple Motor Studio Alternative")
    print("  Configure Robstride Motors via Python")
    print("="*50)
    
    # Get COM port
    port = input("\nEnter COM port (default: COM3): ").strip() or "COM3"
    
    try:
        studio = SimpleMotorStudio(port=port)
        studio.interactive_menu()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        if 'studio' in locals():
            studio.close()


if __name__ == "__main__":
    main()

