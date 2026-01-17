#!/usr/bin/env python3
"""
Decode the new response formats found:
- Format 1: 415400005ff4084e4330209c23370d0d0a (bytes 0x58-0x5f)
- Format 2: 4154000077f408bc7d30209c23370d0d0a (bytes 0x70-0x77)

Structure appears to be:
4154 0000 [ID_PART] 08 [DATA] 0d0d0a

Need to decode [ID_PART] and [DATA] to identify motors 7, 9, 11
"""
import serial
import time
import sys

def decode_response_format(resp_hex, query_byte):
    """Decode response to extract motor ID information"""
    
    resp_clean = resp_hex.replace('0d0a', '').replace('0d', '').lower()
    
    print(f"\nDecoding response from query byte 0x{query_byte:02x}:")
    print(f"  Full: {resp_hex}")
    
    if not resp_clean.startswith('41540000'):
        return None
    
    # Extract ID part (bytes 4-5 after "41540000")
    # Format: 4154 0000 [ID_PART_HI] [ID_PART_LO] 08 [DATA...]
    if len(resp_clean) < 16:
        return None
    
    id_part = resp_clean[8:12]  # 4 hex chars = 2 bytes
    data_start = 14  # After "41540000" + id_part + "08"
    
    print(f"\nStructure:")
    print(f"  Prefix:    4154 0000")
    print(f"  ID Part:   {id_part} (0x{id_part}) = {int(id_part, 16)} decimal")
    print(f"  Next byte: {resp_clean[12:14]}")
    print(f"  Data:      {resp_clean[data_start:]}")
    
    # Check if data contains known motor encodings
    data = resp_clean[data_start:]
    motor_encodings = {
        '0c': 1,   # Motor 1 (long format)
        '1c': 3,   # Motor 3 (long format)
        '3c': 7,   # Motor 7 (long format)
        '4c': 9,   # Motor 9 (long format)
        '7c': 7,   # Motor 7 (short format, alternative)
        '9c': 11,  # Motor 11 (short format)
        '74': 14,  # Motor 14 (long format)
    }
    
    found_encodings = []
    for enc, motor_id in motor_encodings.items():
        if enc in data:
            pos = data.find(enc)
            found_encodings.append((motor_id, enc, pos))
            print(f"\n  Found encoding '{enc}' (Motor {motor_id}) at position {pos} in data")
    
    # Try to decode ID part to motor ID
    id_val = int(id_part, 16)
    print(f"\nID Part Analysis:")
    print(f"  As 16-bit: 0x{id_val:04x} = {id_val}")
    print(f"  High byte: 0x{(id_val >> 8) & 0xff:02x} = {(id_val >> 8) & 0xff}")
    print(f"  Low byte:  0x{id_val & 0xff:02x} = {id_val & 0xff}")
    
    # Try reverse lookup: what motor ID would produce this ID part?
    # If ID part is derived from motor ID somehow
    for motor_id in [7, 9, 11]:
        # Try various encodings
        test_vals = [
            motor_id << 8,  # Motor ID in high byte
            motor_id,       # Motor ID in low byte
            (motor_id << 4) | 0xf4,  # Motor ID << 4 + 0xf4
            (motor_id << 4) | 0x0c,  # Motor ID << 4 + 0x0c
        ]
        
        for test_val in test_vals:
            if test_val == id_val:
                print(f"  -> MATCH! Could be Motor {motor_id} (encoding: {hex(test_val)})")
    
    return {
        'query_byte': query_byte,
        'id_part': id_part,
        'id_val': id_val,
        'data': data,
        'found_encodings': found_encodings
    }

def test_and_decode_responses(port='COM6', baudrate=921600):
    """Test the bytes that give responses and decode them"""
    
    try:
        ser = serial.Serial(port, baudrate, timeout=3.0)
        print("="*70)
        print("Decoding New Response Formats")
        print("="*70)
        print()
        
        # Initialize
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        
        # Test bytes that give responses
        test_bytes = [
            0x5c,  # Format 1: 415400005ff4...
            0x70,  # Format 2: 4154000077f4...
        ]
        
        results = []
        
        for byte_val in test_bytes:
            print("\n" + "="*70)
            
            cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val])
            cmd.extend([0x01, 0x00, 0x0d, 0x0a])
            
            ser.reset_input_buffer()
            ser.write(bytes(cmd))
            time.sleep(1.0)
            
            response = bytearray()
            start = time.time()
            while time.time() - start < 2.0:
                if ser.in_waiting > 0:
                    response.extend(ser.read(ser.in_waiting))
                time.sleep(0.1)
            
            if len(response) > 4:
                resp_hex = response.hex()
                decoded = decode_response_format(resp_hex, byte_val)
                if decoded:
                    results.append(decoded)
            
            time.sleep(0.5)
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("DECODING SUMMARY")
        print("="*70)
        
        for result in results:
            print(f"\nQuery Byte 0x{result['query_byte']:02x}:")
            print(f"  ID Part: 0x{result['id_part']} ({result['id_val']})")
            if result['found_encodings']:
                for motor_id, enc, pos in result['found_encodings']:
                    print(f"  -> Contains Motor {motor_id} encoding '{enc}' at data[{pos}]")
        
        print()
        print("="*70)
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    test_and_decode_responses(port)

