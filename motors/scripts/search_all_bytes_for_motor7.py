#!/usr/bin/env python3
"""
Search all bytes systematically to find Motor 7
Motor 9: CAN ID 19, byte 0xdc
Motor 7: Might be at a different CAN ID, need to find its byte encoding
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

port = 'COM6'
print("="*70)
print("Search All Bytes for Motor 7")
print("="*70)
print()
print("Motor 9: CAN ID 19, byte 0xdc")
print("Searching systematically for Motor 7...")
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
    
    # Search priority ranges first
    priority_ranges = [
        (0xa0, 0xf0, "0xa0-0xef (around Motor 9's 0xdc)"),
        (0x00, 0x20, "0x00-0x1f"),
        (0x20, 0x60, "0x20-0x5f"),
        (0x60, 0xa0, "0x60-0x9f"),
    ]
    
    found_bytes = []
    
    print("Searching priority ranges...")
    print()
    
    for start, end, desc in priority_ranges:
        print(f"Range {desc}: ", end='', flush=True)
        count = 0
        
        for byte_val in range(start, end):
            cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
            resp = send_and_get_response(ser, cmd, timeout=0.4)
            
            if resp:
                found_bytes.append((byte_val, resp))
                count += 1
            
            time.sleep(0.05)  # Fast scan
        
        print(f"[{count} found]")
    
    ser.close()
    
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    
    if found_bytes:
        print(f"Found {len(found_bytes)} responding bytes:")
        print()
        for byte_val, resp in sorted(found_bytes, key=lambda x: x[0]):
            print(f"Byte 0x{byte_val:02x} ({byte_val}): {resp[:60]}...")
            
            # Check for Motor 7 patterns
            resp_clean = resp.replace('0d0a', '').replace('0d', '').lower()
            if '3fec' in resp_clean or '3c' in resp_clean[:20]:
                print(f"  -> Motor 7 pattern detected!")
            elif '4fec' in resp_clean or '4c' in resp_clean[:20]:
                print(f"  -> Motor 9 pattern detected!")
            elif '5fec' in resp_clean:
                print(f"  -> Motor 11 pattern detected!")
            elif '77ec' in resp_clean:
                print(f"  -> Motor 14 pattern detected!")
    else:
        print("No responding bytes found in tested ranges.")
    
    print()
    print("="*70)
    print()
    print("Compare responses to Motor 9's pattern:")
    print("  Motor 9 (byte 0xdc): Should have a specific response pattern")
    print("  Motor 7 might have a similar pattern but different byte value")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

