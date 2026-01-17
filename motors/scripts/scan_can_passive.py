#!/usr/bin/env python3
"""
Passive CAN scan - just listen for ANY traffic on both interfaces
"""

import can
import time
import threading

def listen_interface(interface, results, duration=15):
    """Listen passively on one interface"""
    try:
        bus = can.interface.Bus(channel=interface, interface='socketcan')
        print(f"✓ Listening on {interface}...")
        
        start_time = time.time()
        count = 0
        
        while time.time() - start_time < duration:
            msg = bus.recv(timeout=0.5)
            if msg:
                count += 1
                ext = "EXT" if msg.is_extended_id else "STD"
                print(f"  [{interface}] {ext} ID=0x{msg.arbitration_id:08X} Data={msg.data.hex()}")
        
        results[interface] = count
        bus.shutdown()
        
    except Exception as e:
        print(f"✗ Error on {interface}: {e}")
        results[interface] = 0

def main():
    print("="*60)
    print("  Passive CAN Monitoring - 15 seconds")
    print("="*60)
    print("\nListening for ANY CAN traffic...")
    print("(Motors might send periodic status messages)\n")
    
    results = {}
    
    # Listen on both interfaces simultaneously
    t0 = threading.Thread(target=listen_interface, args=('can0', results, 15))
    t1 = threading.Thread(target=listen_interface, args=('can1', results, 15))
    
    t0.start()
    t1.start()
    
    t0.join()
    t1.join()
    
    print("\n" + "="*60)
    print("  RESULTS")
    print("="*60)
    
    if results.get('can0', 0) > 0:
        print(f"✓ can0: {results['can0']} messages")
    else:
        print(f"✗ can0: No traffic")
    
    if results.get('can1', 0) > 0:
        print(f"✓ can1: {results['can1']} messages")
    else:
        print(f"✗ can1: No traffic")
    
    if results.get('can0', 0) == 0 and results.get('can1', 0) == 0:
        print("\n⚠️  No CAN traffic detected on either interface")
        print("\nPossible issues:")
        print("1. Motors not connected to can0/can1")
        print("2. DIP switches need different setting")
        print("3. Controller still in serial mode")
        print("4. Need to check physical CAN connections")
    
    print()

if __name__ == "__main__":
    main()

