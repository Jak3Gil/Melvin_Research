#!/usr/bin/env python3
"""
Test ALL byte values (0x00 to 0xFF) for responses
No movement - just check which bytes respond to activation/load params commands
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

def test_byte(ser, byte_val):
    """Test a byte value for responses"""
    results = {'activate': None, 'load_params': None}
    
    # Test activation
    cmd1 = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
    resp1 = send_and_get_response(ser, cmd1, timeout=0.4)
    results['activate'] = resp1
    
    time.sleep(0.2)
    
    # Test load params
    cmd2 = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                      0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    resp2 = send_and_get_response(ser, cmd2, timeout=0.4)
    results['load_params'] = resp2
    
    return results

port = 'COM6'
print("="*70)
print("Test ALL Bytes for Responses - No Movement")
print("="*70)
print()
print("Testing all 256 byte values (0x00 to 0xFF)")
print("Looking for responses to activation and load params commands")
print()
print("Starting in 2 seconds...")
time.sleep(2)
print()

try:
    ser = serial.Serial(port, 921600, timeout=1.0)
    time.sleep(0.5)
    
    print("Initializing...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK]")
    print()
    
    # Priority ranges first (known motor bytes)
    priority_ranges = [
        (0x00, 0x20, "0x00-0x1f"),
        (0x2c, 0x50, "0x2c-0x4f (Motor 7/9 ranges)"),
        (0x58, 0x60, "0x58-0x5f (Motor 11 range)"),
        (0x70, 0x80, "0x70-0x7f (Motor 14 range)"),
        (0x8c, 0xa0, "0x8c-0x9f"),
    ]
    
    responding_bytes = []
    
    print("Testing priority ranges first...")
    print()
    
    for start, end, desc in priority_ranges:
        print(f"Range {desc}: ", end='', flush=True)
        count = 0
        
        for byte_val in range(start, end):
            results = test_byte(ser, byte_val)
            
            if results['activate'] or results['load_params']:
                responding_bytes.append({
                    'byte': byte_val,
                    'activate_resp': results['activate'],
                    'load_params_resp': results['load_params']
                })
                count += 1
            
            time.sleep(0.1)  # Short delay between bytes
        
        print(f"[{count} responding bytes found]")
    
    # Quick scan of remaining ranges (every 4th byte to save time)
    print()
    print("Quick scan of remaining bytes (every 4th byte)...")
    skipped = set()
    for start, end, _ in priority_ranges:
        skipped.update(range(start, end))
    
    for byte_val in range(0, 256, 4):
        if byte_val in skipped:
            continue
        
        results = test_byte(ser, byte_val)
        
        if results['activate'] or results['load_params']:
            responding_bytes.append({
                'byte': byte_val,
                'activate_resp': results['activate'],
                'load_params_resp': results['load_params']
            })
        
        time.sleep(0.05)
    
    ser.close()
    
    # Results
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    print(f"Total bytes that responded: {len(responding_bytes)}")
    print()
    
    if responding_bytes:
        print("BYTES WITH RESPONSES:")
        print("-" * 70)
        
        # Sort by byte value
        responding_bytes.sort(key=lambda x: x['byte'])
        
        for result in responding_bytes:
            byte_val = result['byte']
            print(f"\nByte 0x{byte_val:02x} ({byte_val}):")
            
            if result['activate_resp']:
                resp = result['activate_resp']
                print(f"  Activate: {resp[:60]}...")
            else:
                print(f"  Activate: No response")
            
            if result['load_params_resp']:
                resp = result['load_params_resp']
                print(f"  Load Params: {resp[:60]}...")
            else:
                print(f"  Load Params: No response")
    else:
        print("No bytes responded!")
    
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

