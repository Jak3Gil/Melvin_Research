#!/usr/bin/env python3
"""
Wait for motors to appear on CAN after DIP switch change
Continuously monitors can0 and can1 for any CAN traffic
"""

import can
import time

def monitor_can_bus(interface, duration=30):
    """Monitor CAN bus for any traffic"""
    print(f"\n{'='*60}")
    print(f"  Monitoring {interface} for {duration} seconds")
    print(f"{'='*60}\n")
    
    try:
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        print(f"✓ {interface} opened")
        print(f"  Listening for ANY CAN traffic...")
        print(f"  (Power cycle motors or controller if needed)\n")
        
        start_time = time.time()
        message_count = 0
        
        while time.time() - start_time < duration:
            elapsed = int(time.time() - start_time)
            print(f"\r  [{elapsed:02d}/{duration}s] Messages: {message_count}", end='', flush=True)
            
            msg = bus.recv(timeout=0.5)
            if msg:
                message_count += 1
                print(f"\n  ✓ CAN Message received!")
                ext = "EXT-29bit" if msg.is_extended_id else "STD-11bit"
                print(f"    Type: {ext}")
                print(f"    ID: 0x{msg.arbitration_id:08X}")
                print(f"    Data: {msg.data.hex()}")
                print(f"    Length: {len(msg.data)} bytes\n")
        
        print(f"\n\n{'='*60}")
        if message_count > 0:
            print(f"  ✓ {interface}: {message_count} messages received")
            print(f"  ✓ Motors are active on {interface}!")
        else:
            print(f"  ✗ {interface}: No traffic detected")
        print(f"{'='*60}\n")
        
        bus.shutdown()
        return message_count > 0
        
    except Exception as e:
        print(f"\n✗ Error on {interface}: {e}\n")
        return False

def main():
    print("="*60)
    print("  CAN Bus Monitor - Waiting for Motors")
    print("="*60)
    print("\nAfter changing DIP switches:")
    print("1. Unplug and replug the USB cable")
    print("2. OR power cycle the motors")
    print("3. This script will detect when they appear\n")
    
    input("Press ENTER when ready to start monitoring...")
    
    # Monitor both interfaces
    print("\n" + "="*60)
    print("  Starting continuous monitoring...")
    print("="*60)
    
    can0_active = monitor_can_bus('can0', duration=30)
    
    if not can0_active:
        can1_active = monitor_can_bus('can1', duration=30)
    else:
        can1_active = False
    
    # Summary
    print("\n" + "="*60)
    print("  FINAL RESULT")
    print("="*60 + "\n")
    
    if can0_active:
        print("✅ Motors found on: can0")
        print("\n   You can now update firmware with:")
        print("   python3 ota_firmware_updater_socketcan.py can0 rs00_0.0.3.22.bin 8\n")
    elif can1_active:
        print("✅ Motors found on: can1")
        print("\n   You can now update firmware with:")
        print("   python3 ota_firmware_updater_socketcan.py can1 rs00_0.0.3.22.bin 8\n")
    else:
        print("❌ No motors found on can0 or can1")
        print("\n   Try:")
        print("   1. Unplug and replug USB cable")
        print("   2. Power cycle motors")
        print("   3. Check DIP switch settings")
        print("   4. Run this script again\n")

if __name__ == "__main__":
    main()

