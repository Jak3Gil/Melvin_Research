#!/usr/bin/env python3
"""
Verify Motor 9 activation worked and try to activate Motor 7
Motor 9 responds to CAN ID 9, so let's use that activation sequence
"""
import serial
import time

def activate_and_load_params(ser, byte_val):
    """Full activation sequence: activate + load params"""
    # Activate
    cmd1 = bytearray([0x41, 0x54, 0x00, 0x07, 0xe8, byte_val, 0x01, 0x00, 0x0d, 0x0a])
    ser.reset_input_buffer()
    ser.write(cmd1)
    ser.flush()
    time.sleep(0.3)
    
    # Load params
    cmd2 = bytearray([0x41, 0x54, 0x20, 0x07, 0xe8, byte_val, 0x08, 0x00,
                      0xc4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0d, 0x0a])
    ser.write(cmd2)
    ser.flush()
    time.sleep(0.3)

port = 'COM6'
print("="*70)
print("Activate Motors 7 and 9 - Using Working Method")
print("="*70)
print()
print("Motor 9: Confirmed working with CAN ID 9")
print("Motor 7: Will try CAN ID 7 (even though it didn't respond)")
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
    
    # Motor 9 - Use working method
    print("Activating Motor 9 (CAN ID 9)...")
    activate_and_load_params(ser, 9)
    print("  [OK] Activation sequence sent")
    print()
    
    # Motor 7 - Try even though no response
    print("Activating Motor 7 (CAN ID 7)...")
    activate_and_load_params(ser, 7)
    print("  [OK] Activation sequence sent (no response expected)")
    print()
    
    # Also try some variations for Motor 7
    print("Trying Motor 7 variations...")
    for byte_val in [0x70, 0x74]:  # Bytes that gave responses earlier (but moved Motor 14)
        print(f"  Trying byte 0x{byte_val:02x}...")
        activate_and_load_params(ser, byte_val)
        time.sleep(0.3)
    
    ser.close()
    
    print()
    print("="*70)
    print("ACTIVATION COMPLETE")
    print("="*70)
    print()
    print("Now check Motor Studio:")
    print("  - Is Motor 9 now detectable?")
    print("  - Is Motor 7 now detectable?")
    print("  - Are there any other motors visible?")
    print()
    print("If Motor 9 is detectable, the activation worked!")
    print()
    print("="*70)
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

