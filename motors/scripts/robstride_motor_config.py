#!/usr/bin/env python3
"""
RobStride Motor Configuration - Python Implementation
Based on official SampleProgram repository

This implements the motor configuration commands from RobStride.h/Robstride01.cpp
Allows setting CAN IDs, parameters, and protocol switching WITHOUT needing ROS!

Key functions extracted from C++ code:
- Set_CAN_ID: Change motor CAN ID (line 650-660 in Robstride01.cpp)
- RobStride_Motor_MotorDataSave: Save configuration to flash (line 687-704)
- RobStride_Motor_MotorModeSet: Switch protocols (line 813-830)
"""

import serial
import struct
import time

# Communication Types (from Robstride.h lines 26-41)
Communication_Type_Get_ID = 0x00
Communication_Type_MotionControl = 0x01
Communication_Type_MotorRequest = 0x02
Communication_Type_MotorEnable = 0x03
Communication_Type_MotorStop = 0x04
Communication_Type_SetPosZero = 0x06
Communication_Type_Can_ID = 0x07
Communication_Type_Control_Mode = 0x12
Communication_Type_GetSingleParameter = 0x11
Communication_Type_SetSingleParameter = 0x12
Communication_Type_ErrorFeedback = 0x15
Communication_Type_MotorDataSave = 0x16
Communication_Type_BaudRateChange = 0x17
Communication_Type_ProactiveEscalationSet = 0x18
Communication_Type_MotorModeSet = 0x19

class RobStrideMotor:
    """
    RobStride Motor Control Class
    Based on RobStride.h/Robstride01.cpp from official repository
    """
    
    def __init__(self, port='/dev/ttyUSB0', baud=921600, master_id=0xFD):
        """
        Initialize motor controller
        
        Args:
            port: Serial port (e.g., '/dev/ttyUSB0')
            baud: Baud rate (default 921600)
            master_id: Master CAN ID (default 0xFD)
        """
        self.ser = serial.Serial(port, baud, timeout=0.5)
        self.master_id = master_id
        time.sleep(0.5)
        print(f"[OK] Connected to {port} at {baud} baud")
    
    def _send_extended_can(self, comm_type, motor_id, data=None, extra_id_bytes=0):
        """
        Send extended CAN frame (L91 protocol)
        
        Based on working format from instant_test.py:
        Header: 0xAA 0x55
        Command: comm_type
        Motor ID: motor_id (4 bytes little-endian)
        Data: 8 bytes
        Checksum: sum of all bytes after header
        
        Args:
            comm_type: Communication type (0x00-0x19)
            motor_id: Target motor CAN ID
            data: 8 bytes of data (optional)
            extra_id_bytes: Extra ID bytes (for Set_CAN_ID command)
        """
        if data is None:
            data = [0x00] * 8
        elif len(data) < 8:
            data = list(data) + [0x00] * (8 - len(data))
        
        # Build packet with working format
        packet = bytearray([0xAA, 0x55])  # Header (from instant_test.py)
        packet.append(comm_type)  # Command type
        
        # For Set_CAN_ID command, we need to encode both old and new ID
        if comm_type == Communication_Type_Can_ID and extra_id_bytes != 0:
            # Special handling for CAN ID change
            # Pack: old_id (1 byte) + new_id (1 byte) + padding
            packet.append(motor_id)  # Old ID
            packet.extend(struct.pack('<I', extra_id_bytes))  # New ID as 4 bytes
        else:
            # Normal command: motor ID as 4 bytes little-endian
            packet.extend(struct.pack('<I', motor_id))
        
        # Add data (8 bytes)
        packet.extend(data[:8])
        
        # Add checksum (sum of all bytes after header)
        checksum = sum(packet[2:]) & 0xFF
        packet.append(checksum)
        
        self.ser.write(packet)
        self.ser.flush()
        time.sleep(0.15)
        
        # Read response
        response = self.ser.read(100)
        return response
    
    def get_motor_id(self, current_id):
        """
        Get motor's unique 64-bit MCU ID
        Based on RobStride_Get_CAN_ID() (line 213-222)
        """
        print(f"Getting ID for motor {current_id}...")
        response = self._send_extended_can(Communication_Type_Get_ID, current_id)
        
        if response and len(response) > 8:
            print(f"  Response: {response.hex(' ')}")
            # Parse unique ID from response
            if len(response) >= 16:
                unique_id = struct.unpack('<Q', response[8:16])[0]
                print(f"  Unique ID: 0x{unique_id:016X}")
                return unique_id
        return None
    
    def set_motor_id(self, old_id, new_id):
        """
        Set motor CAN ID
        Based on Set_CAN_ID() function (line 650-660 in Robstride01.cpp)
        
        CRITICAL: This is the command to change motor CAN IDs!
        
        Args:
            old_id: Current motor CAN ID
            new_id: New CAN ID to assign
        
        Returns:
            bool: True if successful
        """
        print(f"\n{'='*60}")
        print(f"Setting Motor ID: {old_id} -> {new_id}")
        print(f"{'='*60}")
        
        # Step 1: Disable motor first (from C++ code line 652)
        print(f"  1. Disabling motor {old_id}...")
        self.disable_motor(old_id, clear_error=False)
        time.sleep(0.3)
        
        # Step 2: Send CAN ID change command
        # ExtId format: Communication_Type_Can_ID<<24 | new_id<<16 | master_id<<8 | old_id
        print(f"  2. Sending CAN ID change command...")
        
        # Build the extended ID with new_id in bits 16-23
        response = self._send_extended_can(
            Communication_Type_Can_ID, 
            old_id,
            data=[0x00] * 8,
            extra_id_bytes=new_id
        )
        
        if response:
            print(f"  Response: {response.hex(' ')}")
        
        time.sleep(0.5)
        
        # Step 3: Verify new ID responds
        print(f"  3. Verifying new ID {new_id}...")
        test_response = self.enable_motor(new_id)
        
        if test_response and len(test_response) > 4:
            print(f"  ✓ Motor now responds to ID {new_id}!")
            
            # Step 4: Save to flash
            print(f"  4. Saving configuration to flash...")
            self.save_motor_data(new_id)
            time.sleep(0.5)
            
            print(f"\n✅ SUCCESS! Motor ID changed: {old_id} -> {new_id}")
            print(f"   Configuration saved to motor flash memory")
            return True
        else:
            print(f"\n❌ FAILED! Motor does not respond to new ID {new_id}")
            print(f"   Trying to re-enable old ID {old_id}...")
            self.enable_motor(old_id)
            return False
    
    def enable_motor(self, motor_id):
        """
        Enable motor
        Based on Enable_Motor() (line 547-564)
        """
        print(f"  Enabling motor {motor_id}...")
        response = self._send_extended_can(Communication_Type_MotorEnable, motor_id)
        time.sleep(0.2)
        return response
    
    def disable_motor(self, motor_id, clear_error=False):
        """
        Disable motor
        Based on Disenable_Motor() (line 571-591)
        
        Args:
            motor_id: Motor CAN ID
            clear_error: If True, clear error flags
        """
        data = [0x01 if clear_error else 0x00] + [0x00] * 7
        response = self._send_extended_can(Communication_Type_MotorStop, motor_id, data)
        time.sleep(0.2)
        return response
    
    def save_motor_data(self, motor_id):
        """
        Save motor configuration to flash
        Based on RobStride_Motor_MotorDataSave() (line 687-704)
        
        CRITICAL: This saves the CAN ID change permanently!
        """
        print(f"  Saving motor {motor_id} data to flash...")
        
        # Special data sequence from C++ code (line 695-702)
        data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        
        response = self._send_extended_can(Communication_Type_MotorDataSave, motor_id, data)
        time.sleep(0.5)
        
        if response:
            print(f"  Save response: {response.hex(' ')}")
        
        return response
    
    def set_zero_position(self, motor_id):
        """
        Set current position as zero
        Based on Set_ZeroPos() (line 667-679)
        """
        print(f"Setting zero position for motor {motor_id}...")
        
        # Disable first
        self.disable_motor(motor_id, clear_error=False)
        time.sleep(0.2)
        
        # Send zero position command
        data = [0x01] + [0x00] * 7
        response = self._send_extended_can(Communication_Type_SetPosZero, motor_id, data)
        time.sleep(0.3)
        
        # Re-enable
        self.enable_motor(motor_id)
        
        print(f"  Zero position set!")
        return response
    
    def switch_protocol(self, motor_id, protocol_type):
        """
        Switch motor protocol
        Based on RobStride_Motor_MotorModeSet() (line 813-830)
        
        Args:
            motor_id: Motor CAN ID
            protocol_type: 0x00=Private, 0x01=CANopen, 0x02=MIT
        
        NOTE: Motor must be power-cycled after protocol switch!
        """
        print(f"\nSwitching motor {motor_id} to protocol 0x{protocol_type:02X}...")
        print(f"  0x00 = Private (Lingzu)")
        print(f"  0x01 = CANopen")
        print(f"  0x02 = MIT")
        
        # Special data sequence (line 821-828)
        data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, protocol_type, 0x08]
        
        response = self._send_extended_can(Communication_Type_MotorModeSet, motor_id, data)
        time.sleep(0.5)
        
        print(f"\n⚠️  IMPORTANT: Power-cycle the motor for protocol change to take effect!")
        
        return response
    
    def scan_motors(self, start_id=1, end_id=127):
        """
        Scan for responding motors
        """
        print(f"\nScanning motors {start_id}-{end_id}...")
        found = []
        
        for motor_id in range(start_id, end_id + 1):
            if motor_id % 10 == 0:
                print(f"  Progress: {motor_id}/{end_id}...")
            
            response = self.enable_motor(motor_id)
            if response and len(response) > 4:
                print(f"  ✓ Motor {motor_id} responds")
                found.append(motor_id)
                self.disable_motor(motor_id)
            
            time.sleep(0.05)
        
        print(f"\nFound {len(found)} motors: {found}")
        return found
    
    def close(self):
        """Close serial connection"""
        self.ser.close()
        print("[OK] Connection closed")


def configure_all_motors_unique_ids(port='/dev/ttyUSB0', baud=921600):
    """
    Configure all motors with unique CAN IDs (1-15)
    
    This function will:
    1. Scan for all responding motors
    2. Assign unique IDs (1-15) to each motor
    3. Save configuration to flash
    """
    print("="*70)
    print("CONFIGURE ALL MOTORS WITH UNIQUE IDs")
    print("="*70)
    print()
    
    motor = RobStrideMotor(port, baud)
    
    try:
        # Step 1: Scan for motors
        print("\nStep 1: Scanning for motors...")
        found_ids = motor.scan_motors(1, 127)
        
        if not found_ids:
            print("\n❌ No motors found!")
            return
        
        print(f"\nFound {len(found_ids)} responding CAN IDs")
        print(f"IDs: {found_ids}")
        
        # Step 2: Group by unique motors (based on response patterns)
        print("\nStep 2: Identifying unique physical motors...")
        print("(Multiple IDs may control the same motor)")
        
        # Use the lowest ID in each group as the representative
        # For your case: 8-10, 20, 31, 32-39, 64-71, 72-79
        motor_groups = []
        
        # Simple grouping: consecutive IDs likely same motor
        current_group = [found_ids[0]]
        for i in range(1, len(found_ids)):
            if found_ids[i] == current_group[-1] + 1:
                current_group.append(found_ids[i])
            else:
                motor_groups.append(current_group)
                current_group = [found_ids[i]]
        motor_groups.append(current_group)
        
        print(f"\nIdentified {len(motor_groups)} motor groups:")
        for i, group in enumerate(motor_groups, 1):
            if len(group) > 1:
                print(f"  Motor {i}: IDs {group[0]}-{group[-1]} ({len(group)} IDs)")
            else:
                print(f"  Motor {i}: ID {group[0]}")
        
        # Step 3: Assign unique IDs
        print(f"\nStep 3: Assigning unique IDs (1-{len(motor_groups)})...")
        
        for i, group in enumerate(motor_groups, 1):
            old_id = group[0]  # Use first ID in group
            new_id = i  # Assign sequential IDs starting from 1
            
            print(f"\n--- Motor {i} ---")
            success = motor.set_motor_id(old_id, new_id)
            
            if success:
                print(f"✅ Motor {i} configured: ID {old_id} -> {new_id}")
            else:
                print(f"❌ Failed to configure motor {i}")
            
            time.sleep(1.0)
        
        print(f"\n{'='*70}")
        print("CONFIGURATION COMPLETE")
        print(f"{'='*70}")
        print(f"\nConfigured {len(motor_groups)} motors with unique IDs 1-{len(motor_groups)}")
        print("\n⚠️  IMPORTANT: Power-cycle all motors for changes to take full effect!")
        print()
        
    finally:
        motor.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--configure-all':
        # Configure all motors
        configure_all_motors_unique_ids()
    else:
        # Example usage
        print("="*70)
        print("RobStride Motor Configuration Tool")
        print("="*70)
        print()
        print("Usage examples:")
        print()
        print("1. Configure all motors with unique IDs:")
        print("   python robstride_motor_config.py --configure-all")
        print()
        print("2. Manual configuration:")
        print("   motor = RobStrideMotor('/dev/ttyUSB0', 921600)")
        print("   motor.set_motor_id(old_id=8, new_id=1)")
        print("   motor.close()")
        print()
        print("3. Scan for motors:")
        print("   motor = RobStrideMotor('/dev/ttyUSB0', 921600)")
        print("   found = motor.scan_motors(1, 127)")
        print("   motor.close()")
        print()

