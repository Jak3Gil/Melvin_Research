#!/usr/bin/env python3
"""
Activate Motors 7 and 9 using encoded query bytes
Motor 7 query uses: 0x3c (long format)
Motor 9 query uses: 0x4c (long format)
Maybe activation also needs these encoded bytes?
"""
import serial
import time

def activate_motor(ser, can_id):
    """Activate motor using CAN ID or encoded byte"""
    packet = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, can_id, 0x01, 0x00, 0x0d, 0x0a])
    ser.write(packet)
    ser.flush()
    time.sleep(0.3)
    print(f"  [OK] Activation command sent (byte: 0x{can_id:02x})")

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
print("Activating Motors 7 and 9 - Using Encoded Query Bytes")
print("="*70)
print()
print("IMPORTANT: Close Motor Studio before running this script!")
print("Motor Studio may lock the serial port.")
print()
print("Starting in 3 seconds...")
time.sleep(3)
print()

try:
    print(f"Opening serial port {port}...")
    ser = serial.Serial(port, 921600, timeout=2.0)
    time.sleep(0.5)
    
    if ser.is_open:
        print(f"  [OK] Serial port {port} is OPEN")
    else:
        print(f"  [ERROR] Serial port {port} failed to open!")
        exit(1)
    
    # Initialize
    print("Initializing adapter...")
    ser.write(bytes.fromhex("41542b41540d0a"))
    time.sleep(0.5)
    ser.read(500)
    ser.write(bytes.fromhex("41542b41000d0a"))
    time.sleep(0.5)
    ser.read(500)
    print("  [OK] Initialized")
    print()
    
    # Try Motor 7 with encoded byte 0x3c
    print("Motor 7 Activation Sequence (using encoded byte 0x3c):")
    print("  Step 1: Activate Motor 7 (byte 0x3c)...")
    activate_motor(ser, 0x3c)
    
    print("  Step 2: Send small movement command...")
    move_motor_jog(ser, 0x3c, 0.01, 1)
    time.sleep(0.5)
    
    print("  Step 3: Stop motor...")
    move_motor_jog(ser, 0x3c, 0.0, 0)
    time.sleep(0.3)
    
    print("  [Motor 7 sequence complete]")
    print()
    
    # Try Motor 9 with encoded byte 0x4c
    print("Motor 9 Activation Sequence (using encoded byte 0x4c):")
    print("  Step 1: Activate Motor 9 (byte 0x4c)...")
    activate_motor(ser, 0x4c)
    
    print("  Step 2: Send small movement command...")
    move_motor_jog(ser, 0x4c, 0.01, 1)
    time.sleep(0.5)
    
    print("  Step 3: Stop motor...")
    move_motor_jog(ser, 0x4c, 0.0, 0)
    time.sleep(0.3)
    
    print("  [Motor 9 sequence complete]")
    print()
    
    # Also try actual CAN IDs again
    print("Also trying actual CAN IDs (7 and 9):")
    activate_motor(ser, 7)
    move_motor_jog(ser, 7, 0.01, 1)
    time.sleep(0.5)
    move_motor_jog(ser, 7, 0.0, 0)
    time.sleep(0.3)
    
    activate_motor(ser, 9)
    move_motor_jog(ser, 9, 0.01, 1)
    time.sleep(0.5)
    move_motor_jog(ser, 9, 0.0, 0)
    time.sleep(0.3)
    
    print("  [All sequences complete]")
    print()
    
    # Keep port open
    time.sleep(1.0)
    
    print("Closing serial port...")
    ser.close()
    print("  [OK] Port closed")
    
    print()
    print("="*70)
    print("ACTIVATION COMPLETE")
    print("="*70)
    print()
    print("Now open Motor Studio and check if Motors 7 and 9 are detectable!")
    print()
    print("="*70)
    
except serial.SerialException as e:
    print(f"[X] Serial Port Error: {e}")
    print()
    print("Possible issues:")
    print("  - Motor Studio is still open (close it first)")
    print("  - Another program is using COM6")
    print("  - Port doesn't exist")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

