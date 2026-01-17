#!/usr/bin/env python3
"""
Analyze captured CAN messages from COM6
Use this to analyze hex data you've captured
"""
import sys

# Your captured messages from the original query
captured_messages = [
    "41542b41540d0a",  # open serial port
    "41542b41000d0a",  # device read
    "41542007e80c0800c40000000000000d0a",  # can id 1
    "41542007e81c0800c40000000000000d0a",  # can id 3
    "41542007e83c0800c40000000000000d0a",  # can id 7 (long format)
    "41540007e87c01000d0a",  # can id 7 (short format, both worked)
    "415400007ffc0801020304050600000d0a",  # CanOPEN to private proto
    "41542007e8740800c40000000000000d0a",  # can id 14
    "41540007e89c01000d0a",  # can id 11
    "41542007e84c0800c40000000000000d0a",  # can id 9
]

def extract_can_id_from_hex(hex_str):
    """Extract CAN ID from hex string"""
    hex_clean = hex_str.replace('0d0a', '').lower()
    
    if not hex_clean.startswith('4154'):
        return None
    
    # Long format: 41542007e8XX...
    if hex_clean.startswith('41542007e8'):
        if len(hex_clean) >= 12:
            id_byte_hex = hex_clean[10:12]
            try:
                id_byte = int(id_byte_hex, 16)
                long_format_map = {
                    0x0c: 1,   # CAN ID 1
                    0x1c: 3,   # CAN ID 3
                    0x3c: 7,   # CAN ID 7
                    0x4c: 9,   # CAN ID 9
                    0x74: 14,  # CAN ID 14
                }
                if id_byte in long_format_map:
                    return long_format_map[id_byte]
                return f"Unknown byte: 0x{id_byte:02x}"
            except:
                pass
    
    # Short format: 41540007e8XX...
    elif hex_clean.startswith('41540007e8'):
        if len(hex_clean) >= 12:
            id_byte_hex = hex_clean[10:12]
            try:
                id_byte = int(id_byte_hex, 16)
                short_format_map = {
                    0x7c: 7,   # CAN ID 7
                    0x9c: 11,  # CAN ID 11
                }
                if id_byte in short_format_map:
                    return short_format_map[id_byte]
                return f"Unknown byte: 0x{id_byte:02x}"
            except:
                pass
    
    # CanOPEN format
    elif hex_clean.startswith('415400007ffc'):
        return "CanOPEN"
    
    # Control messages
    elif hex_clean.startswith('41542b'):
        return "Control"
    
    return None

def analyze_messages(messages):
    """Analyze all captured messages"""
    print("="*70)
    print("Analyzing Captured CAN Messages")
    print("="*70)
    print()
    
    motors_found = {}
    control_messages = []
    canopen_messages = []
    unrecognized = []
    
    for msg in messages:
        msg_clean = msg.lower().replace(' ', '').replace('\n', '').replace('\r', '')
        can_id = extract_can_id_from_hex(msg_clean)
        
        if isinstance(can_id, int):
            if can_id not in motors_found:
                motors_found[can_id] = []
            motors_found[can_id].append(msg_clean)
        elif can_id == "Control":
            control_messages.append(msg_clean)
        elif can_id == "CanOPEN":
            canopen_messages.append(msg_clean)
        else:
            unrecognized.append((msg_clean, can_id))
    
    print("MOTORS DETECTED:")
    print("="*70)
    if motors_found:
        for motor_id in sorted(motors_found.keys()):
            count = len(motors_found[motor_id])
            print(f"  Motor ID {motor_id}: {count} message(s)")
            for msg in motors_found[motor_id]:
                print(f"    {msg}")
        print()
        print(f"Total unique motors: {len(motors_found)}")
        print(f"Expected: 6 motors")
        
        if len(motors_found) < 6:
            print(f"\n[WARNING] Only {len(motors_found)} out of 6 motors found!")
            print("Missing motor IDs need to be identified from Motor Studio.")
    else:
        print("  No motors detected!")
    
    print()
    print("="*70)
    
    if control_messages:
        print("CONTROL MESSAGES:")
        print("="*70)
        for msg in control_messages:
            print(f"  {msg}")
        print()
    
    if canopen_messages:
        print("CanOPEN MESSAGES:")
        print("="*70)
        for msg in canopen_messages:
            print(f"  {msg}")
        print()
    
    if unrecognized:
        print("UNRECOGNIZED MESSAGES:")
        print("="*70)
        for msg, reason in unrecognized:
            print(f"  {msg}")
            if reason:
                print(f"    Reason: {reason}")
        print()
    
    return motors_found

if __name__ == "__main__":
    # Analyze the captured messages
    motors = analyze_messages(captured_messages)
    
    print("="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print()
    print("To find the missing 2 motors:")
    print("1. Run Motor Studio and connect all 6 motors")
    print("2. Use monitor_motor_studio_traffic.py to capture traffic")
    print("3. Look for messages with format 41542007e8XX... or 41540007e8XX...")
    print("4. Note the byte values at position 10-11 (after '07e8')")
    print("5. Those byte values correspond to the missing motor CAN IDs")
    print("="*70)

