#!/usr/bin/env python3
"""
Test different multi-device initialization configurations
Motor Studio uses "multi device" mode - we need to find what command enables it
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

def test_motor_activation(ser, byte_val, motor_name):
    """Test if motor responds after initialization"""
    cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
    resp = send_and_get_response(ser, cmd, timeout=0.8)
    return resp

port = 'COM6'
print("="*70)
print("Test Multi-Device Configuration Initializations")
print("="*70)
print()
print("Testing various initialization sequences that might enable")
print("multi-device mode (like Motor Studio does)")
print()
print("CONNECT ALL 6 MOTORS BEFORE RUNNING!")
print()
print("Starting in 3 seconds...")
time.sleep(3)
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    # Standard initialization
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Configuration sequences to test
    configurations = [
        # 1. Broadcast Enable (0xFF)
        {
            'name': 'Broadcast Enable (0xFF)',
            'cmds': [
                bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0xff, 0xff, 0x01, 0x00, 0x0d, 0x0a]),
            ]
        },
        
        # 2. NMT Broadcast Start All (CanOPEN)
        {
            'name': 'NMT Broadcast Start All (0x000)',
            'cmds': [
                bytes.fromhex("415400007ffc02010000000000000d0a"),  # NMT Start All (0x01)
            ]
        },
        
        # 3. NMT Broadcast Pre-operational
        {
            'name': 'NMT Broadcast Pre-op (0x000)',
            'cmds': [
                bytes.fromhex("415400007ffc02800000000000000d0a"),  # NMT Pre-op All (0x80)
                bytes.fromhex("415400007ffc02010000000000000d0a"),  # Then Start All
            ]
        },
        
        # 4. Broadcast Device Read
        {
            'name': 'Broadcast Device Read',
            'cmds': [
                bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x00, 0x00, 0x0d, 0x0a]),
            ]
        },
        
        # 5. Multiple Broadcast Activations
        {
            'name': 'Multiple Broadcast Activations',
            'cmds': [
                bytes([0x41, 0x54, 0x00, 0x07, 0xe8, 0xff, 0x01, 0x00, 0x0d, 0x0a]),
                bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x01, 0x00, 0x0d, 0x0a]),
            ]
        },
        
        # 6. AT Multi-Device Commands (text)
        {
            'name': 'AT Multi-Device (Text Commands)',
            'cmds': [
                b"AT+MD\r\n",
                b"AT MD\r\n",
                b"AT+MULTI\r\n",
                b"AT ENABLE MULTI\r\n",
            ]
        },
        
        # 7. Sequential Broadcast Enable All IDs
        {
            'name': 'Sequential Broadcast (IDs 0-15)',
            'cmds': [
                bytes([0x41, 0x54, 0x00, 0x07, 0xe8, i, 0x01, 0x00, 0x0d, 0x0a])
                for i in range(0, 16)
            ]
        },
        
        # 8. Device Read + Broadcast Enable
        {
            'name': 'Device Read + Broadcast Enable',
            'cmds': [
                bytes.fromhex("41542b41000d0a"),  # Device read
                bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x01, 0x00, 0x0d, 0x0a]),  # Broadcast enable
            ]
        },
        
        # 9. Extended Format Broadcast
        {
            'name': 'Extended Format Broadcast (0x20)',
            'cmds': [
                bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, 0xff, 0x08, 0x00,
                          0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a]),
            ]
        },
        
        # 10. Broadcast + Individual Initialization
        {
            'name': 'Broadcast + Individual Init',
            'cmds': [
                bytes([0x41, 0x54, 0x00, 0x07, 0xff, 0xff, 0x01, 0x00, 0x0d, 0x0a]),  # Broadcast
                bytes.fromhex("41540007e83c01000d0a"),  # Motor 7
                bytes.fromhex("41540007e8dc01000d0a"),  # Motor 9
            ]
        },
    ]
    
    for config_idx, config in enumerate(configurations, 1):
        print("="*70)
        print(f"CONFIGURATION {config_idx}: {config['name']}")
        print("="*70)
        print()
        
        # Send initialization commands
        for cmd in config['cmds']:
            print(f"  Sending: {cmd.hex()[:60]}...")
            resp = send_and_get_response(ser, cmd, timeout=0.5)
            if resp:
                print(f"    Response: {resp[:60]}...")
            time.sleep(0.2)
        
        print()
        print("  Testing Motors 7 and 9 after this configuration...")
        time.sleep(0.5)
        
        # Test Motor 7 (byte 0x3c)
        resp_7 = test_motor_activation(ser, 0x3c, "Motor 7")
        if resp_7:
            print(f"    Motor 7: [RESPONSE] {resp_7[:60]}...")
            if '3fec' in resp_7.lower() or '3ff4' in resp_7.lower():
                print(f"    -> Motor 7 PATTERN DETECTED!")
        else:
            print(f"    Motor 7: [NO RESPONSE]")
        
        time.sleep(0.3)
        
        # Test Motor 9 (byte 0xdc)
        resp_9 = test_motor_activation(ser, 0xdc, "Motor 9")
        if resp_9:
            print(f"    Motor 9: [RESPONSE] {resp_9[:60]}...")
            if '4fec' in resp_9.lower() or '4ff4' in resp_9.lower() or 'dc' in resp_9.lower():
                print(f"    -> Motor 9 PATTERN DETECTED!")
        else:
            print(f"    Motor 9: [NO RESPONSE]")
        
        # If both responded, this might be the right configuration!
        if resp_7 and resp_9:
            print()
            print("  *** POTENTIAL SUCCESS! ***")
            print(f"  Both Motors 7 and 9 responded after: {config['name']}")
            print()
        
        time.sleep(0.5)
        print()
    
    ser.close()
    
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    print()
    print("Check which configuration (if any) made Motors 7 and 9 respond.")
    print("That configuration is likely what Motor Studio uses for multi-device mode!")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

