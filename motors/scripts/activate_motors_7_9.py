#!/usr/bin/env python3
"""
Activate Motors 7 and 9 using the same sequence that activated Motor 11
We sent activation + movement commands using actual CAN IDs
"""
import serial
import time

def activate_motor(ser, can_id):
    """Activate motor using actual CAN ID"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    print(f"  [OK] Activation command sent to CAN ID {can_id}")

def move_motor_jog(ser, can_id, speed=0.03, flag=1):
    """Send movement command"""
    if speed == 0.0:
        speed_val = 0x7fff
    else:
        speed_val = 0x8000 + int(speed * 3283.0)
    speed_val = max(0, min(0xFFFF, speed_val))
    speed_high = (speed_val >> 8) & 0xFF
    speed_low = speed_val & 0xFF
    
    packet = bytearray([0x41, 0x54, 0x90, 0x07, 0xe8, can_id])
    packet.extend([0x08, 0x05, 0x70, 0x00, 0x00, 0x07, flag, speed_high, speed_low])
    packet.extend([0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.1)

port = 'COM6'
print("="*70)
print("Activating Motors 7 and 9 (Same sequence that activated Motor 11)")
print("="*70)
print()

try:
    print(f"Opening serial port {port}...")
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)  # Wait for port to be ready
    
    if ser.is_open:
        print(f"  [OK] Serial port {port} is OPEN")
    else:
        print(f"  [ERROR] Serial port {port} failed to open!")
        exit(1)
    
    # Initialize
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    response1 = ser.read(500)
    if response1:
        print(f"  Response 1: {response1.hex()[:40]}...")
    
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    response2 = ser.read(500)
    if response2:
        print(f"  Response 2: {response2.hex()[:40]}...")
    
    print("  [OK] Initialized")
    print()
    
    # Motor 7 activation sequence
    print("Motor 7 Activation Sequence:")
    print("  Step 1: Activate Motor 7 (CAN ID 7)...")
    activate_motor(ser, 7)
    
    print("  Step 2: Send small movement command...")
    move_motor_jog(ser, 7, 0.01, 1)  # Very small movement
    time.sleep(0.5)
    
    print("  Step 3: Stop motor...")
    move_motor_jog(ser, 7, 0.0, 0)
    time.sleep(0.3)
    
    print("  [Motor 7 sequence complete]")
    print()
    
    # Motor 9 activation sequence
    print("Motor 9 Activation Sequence:")
    print("  Step 1: Activate Motor 9 (CAN ID 9)...")
    activate_motor(ser, 9)
    
    print("  Step 2: Send small movement command...")
    move_motor_jog(ser, 9, 0.01, 1)  # Very small movement
    time.sleep(0.5)
    
    print("  Step 3: Stop motor...")
    move_motor_jog(ser, 9, 0.0, 0)
    time.sleep(0.3)
    
    print("  [Motor 9 sequence complete]")
    print()
    
    # Keep port open for a moment to ensure commands are sent
    time.sleep(1.0)
    
    print("Closing serial port...")
    ser.close()
    print("  [OK] Port closed")
    
    print("="*70)
    print("ACTIVATION COMPLETE")
    print("="*70)
    print()
    print("Check Motor Studio now - Motors 7 and 9 should be detectable!")
    print("(Same as Motor 11 became detectable after this sequence)")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

