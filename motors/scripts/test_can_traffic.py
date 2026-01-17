#!/usr/bin/env python3
"""
Test CAN traffic - send motor enable command and listen for responses
"""

import can
import time

def test_can_interface(interface):
    """Test if motors respond on this CAN interface"""
    print(f"\n{'='*60}")
    print(f"  Testing {interface}")
    print(f"{'='*60}\n")
    
    try:
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        print(f"✓ {interface} opened\n")
        
        # Send enable command to motor 8 (standard 11-bit ID)
        print(f"Sending enable command to motor 8...")
        msg = can.Message(
            arbitration_id=0x008,
            data=[0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            is_extended_id=False
        )
        bus.send(msg)
        print(f"  → Sent: ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex()}")
        
        # Listen for responses
        print(f"\nListening for responses (5 seconds)...")
        start_time = time.time()
        response_count = 0
        
        while time.time() - start_time < 5.0:
            response = bus.recv(timeout=0.5)
            if response:
                response_count += 1
                ext = "EXT" if response.is_extended_id else "STD"
                print(f"  ← [{ext}] ID=0x{response.arbitration_id:08X}, Data={response.data.hex()}")
        
        if response_count > 0:
            print(f"\n✓ {interface}: {response_count} responses received")
            print(f"✓ Motors are on {interface}!")
        else:
            print(f"\n✗ {interface}: No responses")
        
        bus.shutdown()
        return response_count > 0
        
    except Exception as e:
        print(f"✗ Error on {interface}: {e}")
        return False

def main():
    print("="*60)
    print("  CAN Interface Test - Find Active Motors")
    print("="*60)
    
    # Test both interfaces
    can0_active = test_can_interface('can0')
    can1_active = test_can_interface('can1')
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}\n")
    
    if can0_active:
        print("✓ Motors found on: can0")
    if can1_active:
        print("✓ Motors found on: can1")
    
    if not can0_active and not can1_active:
        print("✗ No motors found on can0 or can1")
        print("\n  Possible reasons:")
        print("  1. Motors are connected via /dev/ttyUSB0 (serial)")
        print("  2. Motors need to be enabled first")
        print("  3. CAN bus not properly configured")
    
    print()

if __name__ == "__main__":
    main()

