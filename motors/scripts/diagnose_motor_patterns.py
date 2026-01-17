#!/usr/bin/env python3
"""
Diagnose Motor Response Patterns
Test all CAN IDs systematically to understand motor response patterns
"""

import serial
import sys
import time

def build_activate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])

def build_deactivate_cmd(can_id):
    return bytes([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x00, 0x00, 0x0d, 0x0a])

def build_load_params_cmd(can_id):
    return bytes([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                  0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])

def build_move_jog_cmd(can_id, speed=0.0, flag=1):
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = int(0x8000 + (speed * 3283.0))
    else:
        speed_val = int(0x7fff + (speed * 3283.0))
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id, 0x08, 0x05, 0x70, 
                     0x00, 0x00, 0x07, flag])
    cmd.extend([(speed_val >> 8) & 0xFF, speed_val & 0xFF, 0x0d, 0x0a])
    return bytes(cmd)

def send_command(ser, cmd):
    try:
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(0.05)
        return True
    except:
        return False

def test_can_id(ser, can_id):
    """Test a CAN ID and see which motor responds"""
    send_command(ser, build_activate_cmd(can_id))
    time.sleep(0.2)
    send_command(ser, build_load_params_cmd(can_id))
    time.sleep(0.2)
    
    # Small movement
    send_command(ser, build_move_jog_cmd(can_id, 0.04, 1))
    time.sleep(0.6)
    send_command(ser, build_move_jog_cmd(can_id, 0.0, 0))
    time.sleep(0.3)
    
    send_command(ser, build_deactivate_cmd(can_id))
    time.sleep(0.2)

def main():
    port = "COM3"
    baud = 921600
    
    print("="*70)
    print("MOTOR PATTERN DIAGNOSIS")
    print("="*70)
    print("\nBased on your results:")
    print("  - CAN IDs 8-15 -> Physical Motor 1")
    print("  - CAN IDs 16-22 -> Physical Motor 2")
    print("\nThis suggests:")
    print("  1. Only 2 motors are responding (where are the other 13?)")
    print("  2. Motors might be grouped/paired")
    print("  3. Configuration commands didn't work")
    print("\nLet's test more systematically...")
    
    input("\nPress Enter to start comprehensive test...")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(0.5)
        print("\n[OK] Serial port opened\n")
        
        # Test IDs 1-31 more systematically
        motor_mapping = {}
        
        print("Testing CAN IDs 1-31...")
        print("Watch which physical motor(s) move for each ID range\n")
        
        test_ranges = [
            (1, 7, "IDs 1-7"),
            (8, 15, "IDs 8-15 (you said Motor 1)"),
            (16, 22, "IDs 16-22 (you said Motor 2)"),
            (23, 31, "IDs 23-31"),
        ]
        
        for start_id, end_id, description in test_ranges:
            print(f"\n{'='*70}")
            print(f"Testing {description}")
            print(f"{'='*70}")
            
            for can_id in range(start_id, end_id + 1):
                print(f"\nTesting CAN ID {can_id} (0x{can_id:02X})...")
                print("Watch which physical motor moves...")
                input("Press Enter to test...")
                
                test_can_id(ser, can_id)
                
                motor_num = input("Which physical motor moved? (1-15, or 'none'): ").strip()
                if motor_num.lower() != 'none' and motor_num:
                    try:
                        motor_mapping[can_id] = int(motor_num)
                    except:
                        motor_mapping[can_id] = motor_num
        
        # Analysis
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)
        
        # Group by physical motor
        by_motor = {}
        for can_id, motor_num in motor_mapping.items():
            if motor_num not in by_motor:
                by_motor[motor_num] = []
            by_motor[motor_num].append(can_id)
        
        print("\nPhysical Motor -> CAN IDs mapping:")
        for motor_num in sorted(by_motor.keys(), key=lambda x: int(x) if isinstance(x, int) else 999):
            can_ids = sorted(by_motor[motor_num])
            print(f"  Physical Motor {motor_num}: CAN IDs {can_ids}")
        
        print(f"\nTotal physical motors responding: {len(by_motor)}")
        print(f"Expected: 15 motors")
        
        if len(by_motor) < 15:
            print(f"\n[WARNING] Only {len(by_motor)} motors are responding!")
            print("Possible reasons:")
            print("  - Other motors are not powered")
            print("  - Other motors are not connected to CAN bus")
            print("  - Other motors are not configured/enabled")
            print("  - CAN bus wiring issue")
        
        print("\nRecommendations:")
        print("  1. Check if all 15 motors are powered on")
        print("  2. Verify CAN bus connections for all motors")
        print("  3. Check if motors need to be enabled/activated individually")
        print("  4. Since only 2 motors respond, you can control those 2 with IDs 8 and 16")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

