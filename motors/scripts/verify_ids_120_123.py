#!/usr/bin/env python3
"""
Verify if IDs 120-123 are real motors or aliases
Tests if they give different responses than known motors
"""

import serial
import sys
import time

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def send_command_with_response(ser, cmd, timeout=0.3):
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.05)
    
    response = b""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response += ser.read(ser.in_waiting)
        time.sleep(0.01)
    return response

def test_id_response(ser, can_id):
    """Get detailed response from a motor ID"""
    print(f"\nTesting CAN ID {can_id} (0x{can_id:02X}):")
    
    # Activate
    print(f"  Sending activate...")
    response1 = send_command_with_response(ser, build_activate_cmd(can_id))
    print(f"    Response: {response1.hex(' ') if response1 else 'NONE'}")
    
    time.sleep(0.1)
    
    # Load params
    print(f"  Sending load params...")
    response2 = send_command_with_response(ser, build_load_params_cmd(can_id))
    print(f"    Response: {response2.hex(' ') if response2 else 'NONE'}")
    
    return response1, response2

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 921600
    
    print("="*70)
    print("  Verify IDs 120-123 - Real Motors or Aliases?")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Baud: {baud}\n")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("✓ Serial port opened\n")
        
        # Send detection command
        detect_cmd = bytes([0x41, 0x54, 0x2b, 0x41, 0x54, 0x0d, 0x0a])
        ser.write(detect_cmd)
        ser.flush()
        time.sleep(0.5)
        
        print("="*70)
        print("Testing Known Motor IDs (for comparison)")
        print("="*70)
        
        known_ids = [8, 16, 21, 31, 64, 72]
        known_responses = {}
        
        for motor_id in known_ids:
            r1, r2 = test_id_response(ser, motor_id)
            known_responses[motor_id] = (r1, r2)
            time.sleep(0.2)
        
        print("\n" + "="*70)
        print("Testing NEW Motor IDs (120-123)")
        print("="*70)
        
        new_ids = [120, 121, 122, 123]
        new_responses = {}
        
        for motor_id in new_ids:
            r1, r2 = test_id_response(ser, motor_id)
            new_responses[motor_id] = (r1, r2)
            time.sleep(0.2)
        
        # Analysis
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)
        
        print("\nComparing responses...")
        
        # Check if new IDs give same responses as known IDs
        matches = []
        for new_id in new_ids:
            new_r1, new_r2 = new_responses[new_id]
            
            for known_id in known_ids:
                known_r1, known_r2 = known_responses[known_id]
                
                if new_r1 == known_r1 and new_r2 == known_r2:
                    matches.append((new_id, known_id))
                    print(f"  ⚠️  ID {new_id} gives SAME response as ID {known_id}")
                    print(f"      → IDs {new_id} and {known_id} likely control the SAME motor")
        
        if not matches:
            print("  ✓ IDs 120-123 give DIFFERENT responses than known motors")
            print("  → These might be real additional motors!")
        
        # Check if new IDs give unique responses from each other
        print("\nChecking if IDs 120-123 are unique from each other...")
        
        unique = True
        for i, id1 in enumerate(new_ids):
            for id2 in new_ids[i+1:]:
                r1_1, r1_2 = new_responses[id1]
                r2_1, r2_2 = new_responses[id2]
                
                if r1_1 == r2_1 and r1_2 == r2_2:
                    print(f"  ⚠️  IDs {id1} and {id2} give SAME responses")
                    print(f"      → IDs {id1} and {id2} likely control the SAME motor")
                    unique = False
        
        if unique:
            print("  ✓ IDs 120-123 all give DIFFERENT responses")
            print("  → These are 4 different motors!")
        
        # Summary
        print("\n" + "="*70)
        print("CONCLUSION")
        print("="*70)
        
        if matches:
            print("\n✗ IDs 120-123 are ALIASES of existing motors")
            print("   They control motors we already found.")
            print("\n   Mapping:")
            for new_id, known_id in matches:
                print(f"     ID {new_id} = ID {known_id} (same motor)")
        elif not unique:
            print("\n⚠️  IDs 120-123 are not all unique")
            print("   Some of these IDs control the same motor.")
        else:
            print("\n✓ IDs 120-123 appear to be REAL additional motors!")
            print("   They give different responses than known motors.")
            print("   But they didn't move when tested...")
            print("\n   Possible reasons:")
            print("     1. Motors are in locked/disabled state")
            print("     2. Motors need different activation sequence")
            print("     3. Response doesn't guarantee motor will move")
        
        ser.close()
        print("\n[COMPLETE]")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        if 'ser' in locals():
            ser.close()
        sys.exit(1)

if __name__ == '__main__':
    main()

