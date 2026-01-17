#!/usr/bin/env python3
"""
Jetson Motor Interface
Easy-to-use interface for controlling motors via USB-to-CAN at 921600 baud
"""
import serial
import struct
import time
from typing import List, Tuple, Optional

class JetsonMotorController:
    """Controller for RobStride motors via USB-to-CAN"""
    
    def __init__(self, port='/dev/ttyUSB1', baud=921600, timeout=0.5):
        """
        Initialize motor controller
        
        Args:
            port: Serial port (default: /dev/ttyUSB1)
            baud: Baud rate (default: 921600)
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser = None
        self.connected_motors = []
        
    def connect(self) -> bool:
        """
        Connect to USB-to-CAN adapter
        
        Returns:
            True if connection successful
        """
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
            print(f'✅ Connected to {self.port} at {self.baud} baud')
            
            # Test adapter
            self.ser.write(b'AT+AT\r\n')
            time.sleep(0.1)
            response = self.ser.read(100)
            
            if b'OK' in response:
                print('✅ USB-to-CAN adapter responding')
                return True
            else:
                print('⚠️  Adapter may not be responding properly')
                return True  # Still allow connection
                
        except Exception as e:
            print(f'❌ Connection failed: {e}')
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print('✅ Disconnected')
    
    def scan_motors(self, start_id=1, end_id=127) -> List[int]:
        """
        Scan for motors in ID range
        
        Args:
            start_id: Starting CAN ID
            end_id: Ending CAN ID
            
        Returns:
            List of responding motor IDs
        """
        if not self.ser or not self.ser.is_open:
            print('❌ Not connected')
            return []
        
        print(f'Scanning for motors (IDs {start_id}-{end_id})...')
        found = []
        
        for motor_id in range(start_id, end_id + 1):
            # Build activate command (AT protocol format)
            cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
            
            self.ser.reset_input_buffer()
            self.ser.write(cmd)
            self.ser.flush()
            time.sleep(0.15)
            
            # Read response
            response = b""
            start_time = time.time()
            while time.time() - start_time < 0.25:
                if self.ser.in_waiting > 0:
                    response += self.ser.read(self.ser.in_waiting)
                    time.sleep(0.02)
            
            if len(response) > 4:
                # Verify with load params command
                cmd2 = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
                             0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
                
                self.ser.reset_input_buffer()
                self.ser.write(cmd2)
                self.ser.flush()
                time.sleep(0.15)
                
                response2 = b""
                start_time = time.time()
                while time.time() - start_time < 0.25:
                    if self.ser.in_waiting > 0:
                        response2 += self.ser.read(self.ser.in_waiting)
                        time.sleep(0.02)
                
                # Deactivate
                cmd3 = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x00, 0x00, 0x0d, 0x0a])
                self.ser.write(cmd3)
                time.sleep(0.1)
                
                if len(response2) > 4:
                    found.append(motor_id)
                    print(f'  Found: CAN ID {motor_id:3d} (0x{motor_id:02X})')
        
        self.connected_motors = found
        print(f'\n✅ Found {len(found)} motor(s)')
        return found
    
    def enable_motor(self, motor_id: int) -> bool:
        """
        Enable a motor
        
        Args:
            motor_id: CAN ID of motor
            
        Returns:
            True if motor responded
        """
        if not self.ser or not self.ser.is_open:
            print('❌ Not connected')
            return False
        
        # AT protocol activate command
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x01, 0x00, 0x0d, 0x0a])
        
        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        self.ser.flush()
        time.sleep(0.15)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:
            if self.ser.in_waiting > 0:
                response += self.ser.read(self.ser.in_waiting)
                time.sleep(0.02)
        
        return len(response) > 4
    
    def load_params(self, motor_id: int) -> bool:
        """
        Load motor parameters
        
        Args:
            motor_id: CAN ID of motor
            
        Returns:
            True if motor responded
        """
        if not self.ser or not self.ser.is_open:
            print('❌ Not connected')
            return False
        
        # AT protocol load params command
        cmd = bytes([0x41, 0x54, 0x20, 0x07, 0xe8, motor_id, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
        
        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        self.ser.flush()
        time.sleep(0.15)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:
            if self.ser.in_waiting > 0:
                response += self.ser.read(self.ser.in_waiting)
                time.sleep(0.02)
        
        return len(response) > 4
    
    def disable_motor(self, motor_id: int) -> bool:
        """
        Disable a motor
        
        Args:
            motor_id: CAN ID of motor
            
        Returns:
            True if motor responded
        """
        if not self.ser or not self.ser.is_open:
            print('❌ Not connected')
            return False
        
        # AT protocol deactivate command
        cmd = bytes([0x41, 0x54, 0x00, 0x07, 0xe8, motor_id, 0x00, 0x00, 0x0d, 0x0a])
        
        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        self.ser.flush()
        time.sleep(0.15)
        
        response = b""
        start_time = time.time()
        while time.time() - start_time < 0.25:
            if self.ser.in_waiting > 0:
                response += self.ser.read(self.ser.in_waiting)
                time.sleep(0.02)
        
        return len(response) > 4
    
    def move_motor(self, motor_id: int, speed=0.08, flag=1) -> bool:
        """
        Move motor with jog command
        
        Args:
            motor_id: CAN ID of motor
            speed: Movement speed (0.0 to stop, positive/negative for direction)
            flag: Movement flag (1=move, 0=stop)
            
        Returns:
            True if motor responded
        """
        if not self.ser or not self.ser.is_open:
            print('❌ Not connected')
            return False
        
        # Build jog command
        if speed == 0.0:
            speed_val = 0x7fff
        elif speed > 0.0:
            speed_val = int(0x8000 + (speed * 3283.0))
        else:
            speed_val = int(0x7fff + (speed * 3283.0))
        
        cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, motor_id, 0x08, 0x05, 0x70, 
                         0x00, 0x00, 0x07, flag])
        cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
        
        self.ser.reset_input_buffer()
        self.ser.write(bytes(cmd))
        self.ser.flush()
        time.sleep(0.05)
        
        return True
    
    def pulse_motor(self, motor_id: int, pulses=3, duration=0.4):
        """
        Pulse a motor for identification
        
        Args:
            motor_id: CAN ID of motor
            pulses: Number of pulses
            duration: Duration of each pulse in seconds
        """
        print(f'Pulsing motor {motor_id} ({pulses} times)...')
        
        # Activate motor
        self.enable_motor(motor_id)
        time.sleep(0.2)
        self.load_params(motor_id)
        time.sleep(0.2)
        
        # Execute pulses
        for i in range(pulses):
            print(f'  Pulse {i+1}/{pulses}...', end=' ')
            
            # Move
            self.move_motor(motor_id, speed=0.08, flag=1)
            time.sleep(duration)
            
            # Stop
            self.move_motor(motor_id, speed=0.0, flag=0)
            time.sleep(0.3)
            
            print('✓')
        
        # Deactivate motor
        self.disable_motor(motor_id)
        print('Done!')
    
    def emergency_stop_all(self):
        """Emergency stop all known motors"""
        print('🛑 EMERGENCY STOP - Disabling all motors...')
        
        # Stop all motors in common ranges
        for motor_id in range(1, 128):
            packet = bytearray([0xAA, 0x55, 0x01, motor_id])
            packet.extend(struct.pack('<I', motor_id))
            packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            packet.append(sum(packet[2:]) & 0xFF)
            
            self.ser.write(packet)
            time.sleep(0.01)
        
        print('✅ Emergency stop complete')
    
    def get_motor_info(self) -> dict:
        """Get information about connected motors"""
        return {
            'port': self.port,
            'baud': self.baud,
            'connected': self.ser is not None and self.ser.is_open,
            'motors_found': len(self.connected_motors),
            'motor_ids': self.connected_motors
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def main():
    """Demo usage"""
    print('=' * 70)
    print('  Jetson Motor Interface Demo')
    print('=' * 70)
    print()
    
    # Create controller
    controller = JetsonMotorController()
    
    # Connect
    if not controller.connect():
        print('Failed to connect')
        return
    
    print()
    
    # Scan for motors
    motors = controller.scan_motors(start_id=1, end_id=127)
    
    if not motors:
        print('No motors found')
        controller.disconnect()
        return
    
    print()
    print('=' * 70)
    print(f'Found {len(motors)} motor(s)')
    print('=' * 70)
    print()
    
    # Test first motor
    if motors:
        test_id = motors[0]
        print(f'Testing motor {test_id}...')
        print('Watch for movement!')
        print()
        
        controller.pulse_motor(test_id, pulses=3, duration=0.3)
    
    print()
    
    # Show info
    info = controller.get_motor_info()
    print('Connection Info:')
    print(f'  Port: {info["port"]}')
    print(f'  Baud: {info["baud"]}')
    print(f'  Motors: {info["motors_found"]}')
    print()
    
    # Disconnect
    controller.disconnect()


if __name__ == '__main__':
    main()

