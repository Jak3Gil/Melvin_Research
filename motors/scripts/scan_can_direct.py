#!/usr/bin/env python3
"""
Direct CAN scan using python-can library (doesn't require RobStride library)
Scans for RobStride motors on CAN bus
"""
import can
import time
import struct

def scan_motors_on_can(interface='can0', motor_ids_to_test=range(1, 32)):
    """
    Scan for motors by sending enable commands and checking for responses
    RobStride motors use extended CAN IDs
    """
    print(f"="*70)
    print(f"Scanning {interface} for RobStride motors")
    print(f"="*70)
    
    try:
        # Create CAN bus instance
        bus = can.interface.Bus(channel=interface, bustype='socketcan')
        print(f"✓ Connected to {interface}")
        print()
        
        found_motors = []
        
        for motor_id in motor_ids_to_test:
            # RobStride uses extended CAN IDs
            # Command ID format: 0x200 + motor_id for sending
            # Response ID format: 0x300 + motor_id for receiving
            
            cmd_id = 0x200 + motor_id
            resp_id = 0x300 + motor_id
            
            # Send enable/query command (RobStride format)
            # Data: [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] for enable
            data = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            
            msg = can.Message(
                arbitration_id=cmd_id,
                data=data,
                is_extended_id=True
            )
            
            try:
                # Clear receive buffer
                while True:
                    msg_recv = bus.recv(timeout=0.01)
                    if msg_recv is None:
                        break
                
                # Send command
                bus.send(msg)
                
                # Wait for response
                start_time = time.time()
                while time.time() - start_time < 0.1:  # 100ms timeout
                    msg_recv = bus.recv(timeout=0.05)
                    if msg_recv and msg_recv.arbitration_id == resp_id:
                        print(f"  ✓ Found Motor ID {motor_id} (0x{motor_id:02X})")
                        print(f"    Response ID: 0x{msg_recv.arbitration_id:03X}")
                        print(f"    Data: {' '.join(f'{b:02X}' for b in msg_recv.data)}")
                        found_motors.append(motor_id)
                        break
                
            except Exception as e:
                pass  # No response, motor not present
        
        bus.shutdown()
        return found_motors
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("="*70)
    print("  Direct CAN Motor Scanner (python-can)")
    print("="*70)
    print()
    
    # Scan both CAN interfaces
    all_motors = {}
    
    for interface in ['can0', 'can1']:
        print(f"\nScanning {interface}...")
        motors = scan_motors_on_can(interface, motor_ids_to_test=range(1, 32))
        
        if motors:
            all_motors[interface] = motors
            print(f"\n✓ Found {len(motors)} motor(s) on {interface}")
        else:
            print(f"\n✗ No motors found on {interface}")
        
        print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    
    total = sum(len(m) for m in all_motors.values())
    
    if total > 0:
        print(f"\n✓ Total motors found: {total}")
        for interface, motors in all_motors.items():
            print(f"\n{interface}: {len(motors)} motor(s)")
            for motor_id in motors:
                print(f"  - Motor ID {motor_id} (0x{motor_id:02X})")
    else:
        print("\n✗ No motors found on any CAN interface")
        print("\nThis could mean:")
        print("  1. Motors are connected via /dev/ttyUSB0 (L91 protocol), not direct CAN")
        print("  2. Motors need different CAN message format")
        print("  3. Motors are not powered or not connected to CAN bus")
        print("  4. CAN bitrate mismatch (try 1000000 instead of 500000)")
    
    print()

if __name__ == '__main__':
    main()

