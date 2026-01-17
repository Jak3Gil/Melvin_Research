#!/usr/bin/env python3
"""
Configure RobStride motors using SocketCAN
Based on robstride_actuator_bridge approach
This should properly handle address configuration
"""

import can
import struct
import time

def send_can_frame(bus, motor_id, data):
    """Send CAN frame to motor"""
    msg = can.Message(
        arbitration_id=motor_id,
        data=data,
        is_extended_id=False
    )
    try:
        bus.send(msg)
        return True
    except can.CanError as e:
        print(f"CAN Error: {e}")
        return False

def enable_motor(bus, motor_id):
    """Enable motor (MIT protocol)"""
    # MIT enable: 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFC
    data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC]
    send_can_frame(bus, motor_id, data)
    time.sleep(0.1)

def disable_motor(bus, motor_id):
    """Disable motor (MIT protocol)"""
    # MIT disable: 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFD
    data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD]
    send_can_frame(bus, motor_id, data)
    time.sleep(0.1)

def set_zero_position(bus, motor_id):
    """Set current position as zero"""
    # MIT set zero: 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0xFE
    data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE]
    send_can_frame(bus, motor_id, data)
    time.sleep(0.1)

def move_motor(bus, motor_id, position=0.0, velocity=0.0, kp=0.0, kd=0.0, torque=0.0):
    """
    Send MIT mode control command
    position: radians (-12.5 to 12.5)
    velocity: rad/s (-30 to 30)
    kp: position gain (0 to 500)
    kd: velocity gain (0 to 5)
    torque: Nm (-18 to 18)
    """
    # Limit values
    position = max(-12.5, min(12.5, position))
    velocity = max(-30.0, min(30.0, velocity))
    kp = max(0.0, min(500.0, kp))
    kd = max(0.0, min(5.0, kd))
    torque = max(-18.0, min(18.0, torque))
    
    # Convert to 16-bit integers
    p_int = int((position + 12.5) * 65535.0 / 25.0)
    v_int = int((velocity + 30.0) * 4095.0 / 60.0)
    kp_int = int(kp * 4095.0 / 500.0)
    kd_int = int(kd * 4095.0 / 5.0)
    t_int = int((torque + 18.0) * 4095.0 / 36.0)
    
    # Pack into CAN frame
    data = bytearray(8)
    data[0] = (p_int >> 8) & 0xFF
    data[1] = p_int & 0xFF
    data[2] = (v_int >> 4) & 0xFF
    data[3] = ((v_int & 0x0F) << 4) | ((kp_int >> 8) & 0x0F)
    data[4] = kp_int & 0xFF
    data[5] = (kd_int >> 4) & 0xFF
    data[6] = ((kd_int & 0x0F) << 4) | ((t_int >> 8) & 0x0F)
    data[7] = t_int & 0xFF
    
    send_can_frame(bus, motor_id, data)

def scan_motors(bus, id_range):
    """Scan for responding motors"""
    print(f"Scanning IDs {id_range[0]}-{id_range[-1]}...")
    responding = []
    
    for motor_id in id_range:
        # Send enable command
        enable_motor(bus, motor_id)
        
        # Listen for response
        msg = bus.recv(timeout=0.1)
        if msg and msg.arbitration_id == motor_id:
            responding.append(motor_id)
            print(f"  ✓ ID {motor_id}")
    
    return responding

print("="*70)
print("CONFIGURE MOTORS USING SOCKETCAN")
print("="*70)
print("\nBased on RobStride actuator bridge")
print("Using proper CAN protocol")
print("="*70)

try:
    # Connect to CAN interface
    print("\nConnecting to can0...")
    bus = can.interface.Bus(channel='can0', interface='socketcan')
    print("✅ Connected to can0\n")
    
    # Check CAN interface status
    import subprocess
    result = subprocess.run(['ip', '-details', 'link', 'show', 'can0'], 
                          capture_output=True, text=True)
    print("CAN0 Status:")
    for line in result.stdout.split('\n'):
        if 'bitrate' in line or 'state' in line:
            print(f"  {line.strip()}")
    
    print("\n" + "="*70)
    print("SCANNING FOR MOTORS")
    print("="*70)
    
    # Scan different ID ranges
    print("\n1. Scanning IDs 1-20...")
    motors_1_20 = scan_motors(bus, range(1, 21))
    
    print("\n2. Scanning IDs 21-40...")
    motors_21_40 = scan_motors(bus, range(21, 41))
    
    print("\n3. Scanning IDs 64-80...")
    motors_64_80 = scan_motors(bus, range(64, 81))
    
    all_found = motors_1_20 + motors_21_40 + motors_64_80
    
    print(f"\n{'='*70}")
    print("SCAN RESULTS")
    print(f"{'='*70}")
    
    print(f"\n✅ Found {len(all_found)} responding motor IDs:")
    print(f"   {all_found}")
    
    if len(all_found) > 0:
        print(f"\n📋 Next steps:")
        print(f"   1. Test motor movement with SocketCAN")
        print(f"   2. Configure motors to unique IDs using CAN protocol")
        print(f"   3. This should properly handle address masks")
    else:
        print(f"\n⚠️  No motors found via SocketCAN")
        print(f"\nPossible issues:")
        print(f"   1. Motors may be using L91 protocol (not MIT)")
        print(f"   2. CAN bitrate mismatch (try 500000 instead of 1000000)")
        print(f"   3. Motors need to be on can0 interface")
        print(f"\nTo change bitrate:")
        print(f"   sudo ip link set can0 down")
        print(f"   sudo ip link set can0 type can bitrate 500000")
        print(f"   sudo ip link set can0 up")
    
    bus.shutdown()
    print()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    
    print(f"\n📋 Setup required:")
    print(f"   1. Run: bash setup_robstride_bridge.sh")
    print(f"   2. Or manually configure can0:")
    print(f"      sudo ip link set can0 type can bitrate 1000000")
    print(f"      sudo ip link set can0 up")

