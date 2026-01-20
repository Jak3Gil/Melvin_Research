#!/usr/bin/env python3
"""
Detect Robstride 02 Motors using Robstride L91 Protocol on COM6
Target motors: 10, 12, 6, 5, 13

Based on actual working command formats provided by user.
"""

import serial
import struct
import time
from typing import List, Dict, Optional

# Target motor node IDs and their command formats
TARGET_MOTORS = {
    10: {
        'can_id': 10,
        'extended': bytes.fromhex('41542007e8540800c40000000000000d0a'),
        'standard': None,  # Extended format works
        'byte_val': 0x54
    },
    12: {
        'can_id': 12,
        'extended': bytes.fromhex('41542007e8640800c40000000000000d0a'),
        'standard': None,  # Extended format works
        'byte_val': 0x64
    },
    6: {
        'can_id': 6,
        'extended': bytes.fromhex('41542007e8340800c40000000000000d0a'),
        'standard': None,  # Extended format works
        'byte_val': 0x34
    },
    5: {
        'can_id': 5,
        'extended': None,
        'standard': bytes.fromhex('41540007e86c01000d0a'),
        'byte_val': 0x6c
    },
    13: {
        'can_id': 13,
        'extended': bytes.fromhex('41542007e86c0800c40000000000000d0a'),
        'standard': None,  # Extended format works
        'byte_val': 0x6c
    }
}

PORT = 'COM6'
BAUD = 921600


class Robstride02Scanner:
    """Robstride 02 motor scanner using L91 protocol on COM6"""
    
    def __init__(self, port=PORT, baudrate=BAUD):
        self.port = port
        self.baudrate = baudrate
        self.ser: Optional[serial.Serial] = None
        
    def connect(self) -> bool:
        """Connect to serial port and initialize adapter"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            time.sleep(0.5)
            
            # Initialize adapter: AT+AT, then AT+A0
            print(f"Initializing USB-CAN adapter on {self.port}...")
            self.ser.write(bytes.fromhex("41542b41540d0a"))  # AT+AT
            time.sleep(0.3)
            self._drain_rx()
            
            self.ser.write(bytes.fromhex("41542b41000d0a"))  # AT+A0
            time.sleep(0.3)
            self._drain_rx()
            
            print(f"  [OK] Connected to {self.port} at {self.baudrate} baud\n")
            return True
            
        except Exception as e:
            print(f"  [FAIL] Cannot connect to {self.port}: {e}")
            return False
    
    def _drain_rx(self):
        """Drain RX buffer"""
        if self.ser:
            while self.ser.in_waiting > 0:
                self.ser.read(self.ser.in_waiting)
                time.sleep(0.01)
    
    def _read_response(self, timeout: float = 1.0) -> bytes:
        """Read response from adapter"""
        if not self.ser:
            return b''
        
        response = bytearray()
        start_time = time.time()
        last_data_time = start_time
        
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                chunk = self.ser.read(self.ser.in_waiting)
                response.extend(chunk)
                last_data_time = time.time()
            else:
                # If we have data and nothing new for 200ms, assume done
                if len(response) > 0 and (time.time() - last_data_time) > 0.2:
                    break
                time.sleep(0.05)
        
        return bytes(response)
    
    def _parse_frames(self, data: bytes) -> List[Dict]:
        """Parse CAN frames from response data"""
        frames = []
        i = 0
        while i < len(data):
            # Look for "AT" header (0x41 0x54)
            if i + 4 < len(data) and data[i] == 0x41 and data[i+1] == 0x54:
                # Extract status byte
                status = data[i+2]
                # Extract CAN ID (2 bytes, little-endian)
                if i + 5 < len(data):
                    can_id = struct.unpack('<H', data[i+3:i+5])[0]
                    # Extract DLC
                    if i + 6 < len(data):
                        dlc = data[i+5]
                        # Extract data (up to 8 bytes)
                        data_start = i + 6
                        data_end = min(data_start + dlc, len(data))
                        frame_data = data[data_start:data_end]
                        
                        frames.append({
                            'offset': i,
                            'status': status,
                            'can_id': can_id,
                            'dlc': dlc,
                            'data': frame_data,
                            'hex': data[i:data_end].hex()
                        })
                        i = data_end
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return frames
    
    def test_motor(self, motor_id: int, motor_config: Dict) -> Dict:
        """Test a motor using its command format"""
        print(f"  Testing Motor {motor_id:2d} (CAN ID {motor_config['can_id']})...", end='', flush=True)
        
        self._drain_rx()
        self.ser.reset_input_buffer()
        time.sleep(0.1)
        
        # Try extended format first if available
        if motor_config.get('extended'):
            cmd = motor_config['extended']
            format_type = 'extended'
        elif motor_config.get('standard'):
            cmd = motor_config['standard']
            format_type = 'standard'
        else:
            print(f" [ERROR] No command format available")
            return {'motor_id': motor_id, 'found': False, 'error': 'No command format'}
        
        # Send command
        self.ser.write(cmd)
        self.ser.flush()
        time.sleep(0.3)  # Wait for response
        
        # Read response
        response = self._read_response(timeout=1.5)
        
        if response and len(response) > 0:
            # Parse frames
            frames = self._parse_frames(response)
            
            if frames:
                # Check if we got a valid response frame
                valid_response = False
                for frame in frames:
                    # Motor responses typically have CAN IDs in a certain range
                    # For example, Motor 8 responds with 0x4700
                    # Other motors might respond with similar patterns
                    if frame['can_id'] > 0:  # Any non-zero CAN ID indicates response
                        valid_response = True
                        break
                
                if valid_response:
                    print(f" [FOUND] OK")
                    print(f"           Format: {format_type}")
                    print(f"           Command: {cmd.hex()}")
                    print(f"           Response frames: {len(frames)}")
                    for idx, frame in enumerate(frames):
                        print(f"             Frame {idx+1}: CAN ID 0x{frame['can_id']:04X}, Data: {frame['data'].hex()[:20]}...")
                    
                    return {
                        'motor_id': motor_id,
                        'can_id': motor_config['can_id'],
                        'found': True,
                        'format': format_type,
                        'command': cmd.hex(),
                        'response_frames': len(frames),
                        'frames': frames
                    }
        
        print(f" [NOT FOUND]")
        return {'motor_id': motor_id, 'found': False}
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            port = self.port
            self.ser.close()
            print(f"Disconnected from {port}\n")


def main():
    """Main function"""
    print("="*70)
    print("ROBSTRIDE 02 MOTOR DETECTION - L91 Protocol")
    print("="*70)
    print()
    print(f"Port: {PORT}")
    print(f"Baudrate: {BAUD}")
    print(f"Target Motors (CAN IDs): {sorted([m['can_id'] for m in TARGET_MOTORS.values()])}")
    print()
    
    scanner = Robstride02Scanner(port=PORT, baudrate=BAUD)
    
    try:
        # Connect
        if not scanner.connect():
            print("[FAIL] Cannot connect to COM6")
            print("Make sure:")
            print("  1. COM6 is available")
            print("  2. Motor Studio is closed")
            print("  3. USB-CAN adapter is connected")
            return
        
        # Test each target motor
        print("="*70)
        print("TESTING TARGET MOTORS")
        print("="*70)
        print()
        
        results = {}
        
        for motor_id in sorted(TARGET_MOTORS.keys()):
            motor_config = TARGET_MOTORS[motor_id]
            result = scanner.test_motor(motor_id, motor_config)
            results[motor_id] = result
            time.sleep(0.3)  # Brief delay between tests
        
        # Summary
        print()
        print("="*70)
        print("DETECTION SUMMARY")
        print("="*70)
        print()
        
        found_motors = {mid: res for mid, res in results.items() if res.get('found', False)}
        
        if found_motors:
            print(f"[OK] Found {len(found_motors)} out of {len(TARGET_MOTORS)} target motor(s):")
            print()
            for motor_id in sorted(found_motors.keys()):
                result = found_motors[motor_id]
                print(f"  [OK] Motor {motor_id:2d} (CAN ID {result['can_id']:2d})")
                print(f"      Format: {result['format']}")
                print(f"      Response: {result['response_frames']} frame(s)")
                if result.get('frames'):
                    for idx, frame in enumerate(result['frames'][:2]):  # Show first 2 frames
                        print(f"        Frame {idx+1}: CAN ID 0x{frame['can_id']:04X}")
            print()
            
            missing = [mid for mid in TARGET_MOTORS.keys() if mid not in found_motors]
            if missing:
                print(f"[WARNING] Missing {len(missing)} motor(s): {missing}")
                print()
        else:
            print("[FAIL] No target motors detected!")
            print()
            print("Possible reasons:")
            print("  - Motors not powered on")
            print("  - CAN bus connection issues")
            print("  - Wrong command format")
            print("  - Motors need initialization")
            print()
        
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Stopped by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        scanner.disconnect()


if __name__ == '__main__':
    main()
