#!/usr/bin/env python3
"""
Move motors 7 and 9 individually in small, slow increments back and forth
Tests both actual CAN IDs (7, 9) and the discovered query bytes (0x70, 0x58)
"""
import serial
import time
import sys

def move_motor_jog(ser, can_id, speed, flag=1):
    """
    Move motor using JOG command
    Format: AT 90 07 e8 <can_id> 08 05 70 00 00 07 <flag> <speed_high> <speed_low> 0d 0a
    
    Args:
        can_id: Motor CAN ID (or query byte for motors 7, 9)
        speed: Speed value (0.0 = stop, positive = forward, negative = reverse)
        flag: 0=stop, 1=move
    """
    # Speed encoding (16-bit signed, where 0x7fff = 0.0)
    if speed == 0.0:
        speed_val = 0x7fff  # Stop
    elif speed > 0.0:
        # Positive speed: scale factor ~3283.0
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        # Negative speed
        speed_val = 0x7fff + int(speed * 3283.0)
    
    # Clamp to 16-bit range
    speed_val = max(0, min(0xFFFF, speed_val))
    
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    data = [0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low]
    
    packet = bytearray([0x41, 0x54])  # "AT"
    packet.append(0x90)  # Command: MOVE_JOG
    packet.append(0x07)
    packet.append(0xe8)
    packet.append(can_id)
    packet.extend(data)
    packet.extend([0x0d, 0x0a])
    
    ser.write(packet)
    ser.flush()
    time.sleep(0.05)
    
    # Read any response
    resp = ser.read(200)
    return resp.hex() if len(resp) > 0 else None

def activate_motor(ser, can_id):
    """Activate motor"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id])
    packet.extend([0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.2)

def stop_motor(ser, can_id):
    """Stop motor"""
    return move_motor_jog(ser, can_id, 0.0, 0)

def move_motor_sequence(ser, motor_name, can_id, use_query_byte=False):
    """
    Move a motor in small, slow increments back and forth
    """
    print(f"\n{'='*70}")
    print(f"MOVING {motor_name} (CAN ID: {can_id})")
    print(f"{'='*70}")
    
    # Small, slow speed
    speed = 0.05  # Very slow
    move_duration = 1.0  # Move for 1 second
    pause_duration = 0.5  # Pause between movements
    
    try:
        # Activate motor
        print(f"  Activating {motor_name}...")
        activate_motor(ser, can_id)
        time.sleep(0.5)
        
        # Move forward (small increment)
        print(f"  Moving forward slowly (speed={speed})...")
        resp = move_motor_jog(ser, can_id, speed, 1)
        if resp:
            print(f"    Response: {resp[:40]}...")
        time.sleep(move_duration)
        
        # Stop
        print(f"  Stopping...")
        stop_motor(ser, can_id)
        time.sleep(pause_duration)
        
        # Move backward (small increment)
        print(f"  Moving backward slowly (speed={-speed})...")
        resp = move_motor_jog(ser, can_id, -speed, 1)
        if resp:
            print(f"    Response: {resp[:40]}...")
        time.sleep(move_duration)
        
        # Stop
        print(f"  Stopping...")
        stop_motor(ser, can_id)
        time.sleep(pause_duration)
        
        # Move forward again (small increment)
        print(f"  Moving forward slowly again...")
        resp = move_motor_jog(ser, can_id, speed, 1)
        if resp:
            print(f"    Response: {resp[:40]}...")
        time.sleep(move_duration)
        
        # Stop
        print(f"  Stopping...")
        stop_motor(ser, can_id)
        time.sleep(pause_duration)
        
        # Move backward again (small increment)
        print(f"  Moving backward slowly again...")
        resp = move_motor_jog(ser, can_id, -speed, 1)
        if resp:
            print(f"    Response: {resp[:40]}...")
        time.sleep(move_duration)
        
        # Final stop
        print(f"  Final stop...")
        stop_motor(ser, can_id)
        time.sleep(0.5)
        
        print(f"  [{motor_name} sequence complete]")
        return True
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_motors_7_and_9(port='COM6', baudrate=921600):
    """Test moving motors 7 and 9 with different CAN ID encodings"""
    
    try:
        ser = serial.Serial(port, baudrate, timeout=2.0)
        print("="*70)
        print("Moving Motors 7 and 9 Individually")
        print("="*70)
        print()
        print("Testing with different CAN ID encodings:")
        print("  - Actual CAN IDs: 7, 9")
        print("  - Query bytes: 0x70 (Motor 7), 0x58 (Motor 9)")
        print()
        
        # Initialize adapter
        print("Initializing adapter...")
        ser.write(bytes.fromhex("41542b41540d0a"))
        time.sleep(0.5)
        ser.read(500)
        ser.write(bytes.fromhex("41542b41000d0a"))
        time.sleep(0.5)
        ser.read(500)
        print("  [OK]")
        print()
        
        results = {}
        
        # Test Motor 7 with actual CAN ID
        print("\n" + "="*70)
        print("TEST 1: Motor 7 with CAN ID = 7")
        print("="*70)
        results['motor7_can7'] = move_motor_sequence(ser, "Motor 7", 7)
        time.sleep(2)
        
        # Test Motor 7 with query byte
        print("\n" + "="*70)
        print("TEST 2: Motor 7 with query byte = 0x70")
        print("="*70)
        results['motor7_byte70'] = move_motor_sequence(ser, "Motor 7", 0x70)
        time.sleep(2)
        
        # Test Motor 9 with actual CAN ID
        print("\n" + "="*70)
        print("TEST 3: Motor 9 with CAN ID = 9")
        print("="*70)
        results['motor9_can9'] = move_motor_sequence(ser, "Motor 9", 9)
        time.sleep(2)
        
        # Test Motor 9 with query byte
        print("\n" + "="*70)
        print("TEST 4: Motor 9 with query byte = 0x58")
        print("="*70)
        results['motor9_byte58'] = move_motor_sequence(ser, "Motor 9", 0x58)
        time.sleep(2)
        
        ser.close()
        
        # Summary
        print()
        print("="*70)
        print("SUMMARY")
        print("="*70)
        print()
        print("Motor 7:")
        print(f"  CAN ID 7: {'Worked' if results.get('motor7_can7') else 'No movement detected'}")
        print(f"  Byte 0x70: {'Worked' if results.get('motor7_byte70') else 'No movement detected'}")
        print()
        print("Motor 9:")
        print(f"  CAN ID 9: {'Worked' if results.get('motor9_can9') else 'No movement detected'}")
        print(f"  Byte 0x58: {'Worked' if results.get('motor9_byte58') else 'No movement detected'}")
        print()
        print("="*70)
        print()
        print("OBSERVATION:")
        print("  Watch the physical motors during each test.")
        print("  If a motor moves, note which encoding (CAN ID vs query byte) works.")
        print("  This will confirm the correct addressing for movement commands.")
        print()
        print("="*70)
        
        return results
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    port = 'COM6'
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    print()
    print("Moving Motors 7 and 9 individually in small, slow increments...")
    print("Watch the physical motors during the test!")
    print()
    print("Starting in 3 seconds...")
    time.sleep(3)
    print()
    
    results = test_motors_7_and_9(port)

