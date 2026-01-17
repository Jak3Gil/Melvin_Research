#!/usr/bin/env python3
"""
Debug Motor 9 movement - check responses and try different methods
Motor 9 responds to activation/load params but doesn't move
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
        time.sleep(0.05)
    
    return response.hex() if len(response) > 0 else None

def activate_motor(ser, can_id):
    """Activate motor"""
    cmd = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    return send_and_get_response(ser, cmd)

def load_params(ser, can_id):
    """Load motor parameters"""
    cmd = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, can_id, 0x08, 0x00,
                     0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    return send_and_get_response(ser, cmd)

def move_motor_jog(ser, can_id, speed, flag=1):
    """Move motor using JOG command"""
    if speed == 0.0:
        speed_val = 0x7fff
    elif speed > 0.0:
        speed_val = 0x8000 + int(speed * 3283.0)
    else:
        speed_val = 0x7fff + int(speed * 3283.0)
    
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    cmd = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    cmd.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    cmd.extend([0x0d, 0x0a])
    
    return send_and_get_response(ser, cmd, timeout=1.0)

port = 'COM6'
print("="*70)
print("Debug Motor 9 Movement - Check Responses")
print("="*70)
print()

try:
    ser = serial.Serial(port, 921600, timeout=2.0)
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
    
    # Full activation sequence
    print("Step 1: Activate Motor 9 (CAN ID 9)...")
    resp1 = activate_motor(ser, 9)
    if resp1:
        print(f"  Response: {resp1}")
    else:
        print("  No response")
    time.sleep(0.5)
    
    print("\nStep 2: Load parameters...")
    resp2 = load_params(ser, 9)
    if resp2:
        print(f"  Response: {resp2}")
    else:
        print("  No response")
    time.sleep(0.5)
    
    print("\nStep 3: Try movement command (slow forward)...")
    resp3 = move_motor_jog(ser, 9, 0.05, 1)
    if resp3:
        print(f"  Response: {resp3}")
    else:
        print("  No response to movement command")
    time.sleep(2.0)
    
    print("\nStep 4: Stop motor...")
    resp4 = move_motor_jog(ser, 9, 0.0, 0)
    if resp4:
        print(f"  Response: {resp4}")
    else:
        print("  No response to stop command")
    time.sleep(1.0)
    
    print("\nStep 5: Try different speed (faster)...")
    resp5 = move_motor_jog(ser, 9, 0.2, 1)
    if resp5:
        print(f"  Response: {resp5}")
    else:
        print("  No response")
    time.sleep(2.0)
    
    print("\nStep 6: Stop...")
    resp6 = move_motor_jog(ser, 9, 0.0, 0)
    if resp6:
        print(f"  Response: {resp6}")
    
    ser.close()
    
    print()
    print("="*70)
    print("ANALYSIS")
    print("="*70)
    print()
    print("Check the responses above:")
    print("  - Do we get responses from movement commands?")
    print("  - What format are the responses?")
    print("  - Are there error messages?")
    print()
    print("If we get responses but no movement, the motor might:")
    print("  - Need a different command format")
    print("  - Need to be enabled/configured differently")
    print("  - Be in a protected/error state")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

