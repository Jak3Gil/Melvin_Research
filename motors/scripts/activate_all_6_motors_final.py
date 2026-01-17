#!/usr/bin/env python3
"""
Activate all 6 motors using discovered byte encodings
Motors: 1, 3, 7, 9/19, 11, 14

Discovered bytes:
- Motor 1: 0x0c (standard format)
- Motor 3: 0x1c (standard format)
- Motor 7: 0x3c (standard format) - 41540007e83c01000d0a
- Motor 9/19: 0xdc (standard format) - 41540007e8dc01000d0a (CAN ID 19)
- Motor 11: 0x58 (for movement), 0x9c (for query)
- Motor 14: 0x70 (for movement), 0x74 (for query)
"""
import serial
import time

def send_and_get_response(ser, cmd, timeout=0.5):
    """Send command and get response"""
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    
    response = bytearray()
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            response.extend(ser.read(ser.in_waiting))
        time.sleep(0.03)
    
    return response.hex() if len(response) > 0 else None

def load_params(ser, byte_val):
    """Load motor parameters (extended format)"""
    cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    return send_and_get_response(ser, cmd)

port = 'COM6'
print("="*70)
print("Activate All 6 Motors - Using Discovered Byte Encodings")
print("="*70)
print()
print("Motors: 1, 3, 7, 9/19, 11, 14")
print()
print("Strategy: Use standard format (0x00) for Motors 1, 3, 7, 9")
print("         Use working bytes for Motors 11, 14")
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Motor configurations with discovered bytes
    motors = [
        (1, 0x0c, "Motor 1", "Standard format"),
        (3, 0x1c, "Motor 3", "Standard format"),
        (7, 0x3c, "Motor 7", "Standard format"),
        (9, 0xdc, "Motor 9/19", "Standard format (CAN ID 19)"),
        (11, 0x58, "Motor 11", "Movement byte"),
        (14, 0x70, "Motor 14", "Movement byte"),
    ]
    
    print("="*70)
    print("ACTIVATING ALL MOTORS")
    print("="*70)
    print()
    
    activated_motors = []
    
    for motor_num, byte_val, name, format_desc in motors:
        print(f"{name} (byte 0x{byte_val:02x}):")
        print(f"  Format: {format_desc}")
        
        # Activate with standard format
        cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
        resp = send_and_get_response(ser, cmd, timeout=0.8)
        
        if resp:
            print(f"  Activation: [RESPONSE] {resp[:60]}...")
            
            # Check response pattern
            resp_clean = resp.replace('0d0a', '').replace('0d', '').lower()
            pattern = None
            if '0fec' in resp_clean or '0ff4' in resp_clean:
                pattern = "Motor 1 pattern (0fec/0ff4)"
            elif '1fec' in resp_clean or '1ff4' in resp_clean:
                pattern = "Motor 3 pattern (1fec/1ff4)"
            elif '3fec' in resp_clean or '3ff4' in resp_clean:
                pattern = "Motor 7 pattern (3fec/3ff4)"
            elif '4fec' in resp_clean or '4ff4' in resp_clean:
                pattern = "Motor 9 pattern (4fec/4ff4)"
            elif '5fec' in resp_clean or '5ff4' in resp_clean:
                pattern = "Motor 11 pattern (5fec/5ff4)"
            elif '77ec' in resp_clean or '77f4' in resp_clean:
                pattern = "Motor 14 pattern (77ec/77f4)"
            
            if pattern:
                print(f"  Pattern: {pattern}")
            
            activated_motors.append((motor_num, name, byte_val, True))
        else:
            print(f"  Activation: [NO RESPONSE]")
            activated_motors.append((motor_num, name, byte_val, False))
        
        # Try load params
        resp2 = load_params(ser, byte_val)
        if resp2:
            print(f"  Load Params: [RESPONSE] {resp2[:60]}...")
        else:
            print(f"  Load Params: [NO RESPONSE]")
        
        time.sleep(0.3)
        print()
    
    ser.close()
    
    print("="*70)
    print("ACTIVATION SUMMARY")
    print("="*70)
    print()
    
    for motor_num, name, byte_val, got_response in activated_motors:
        status = "[OK]" if got_response else "[NO RESPONSE]"
        print(f"Motor {motor_num} ({name}): Byte 0x{byte_val:02x} {status}")
    
    print()
    print("="*70)
    print("CHECK MOTOR STUDIO")
    print("="*70)
    print()
    print("Open Motor Studio and check:")
    print("  - Are all 6 motors now visible?")
    print("  - Motor 1, 3, 7, 9/19, 11, 14")
    print()
    print("If all motors are visible, we've solved the initialization!")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

