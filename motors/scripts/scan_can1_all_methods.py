#!/usr/bin/env python3
"""
Comprehensive CAN1 Scanner - Try All Discovery Methods
Tests CAN1 GPIO with multiple protocols and variations
"""
import can
import time
import struct

def setup_can1(bitrate=921600):
    """Setup CAN1 interface"""
    import subprocess
    
    print(f"Setting up CAN1 at {bitrate} baud...")
    
    try:
        # Bring down first
        subprocess.run(['sudo', 'ip', 'link', 'set', 'can1', 'down'], 
                      capture_output=True)
        
        # Configure bitrate
        subprocess.run(['sudo', 'ip', 'link', 'set', 'can1', 'type', 'can', 
                       'bitrate', str(bitrate)], check=True)
        
        # Bring up
        subprocess.run(['sudo', 'ip', 'link', 'set', 'can1', 'up'], check=True)
        
        print(f"✓ CAN1 configured at {bitrate} baud")
        return True
    except Exception as e:
        print(f"✗ Failed to setup CAN1: {e}")
        return False

def method1_standard_ids(bus):
    """Method 1: Standard 11-bit CAN IDs (RobStride protocol)"""
    print("\n" + "="*70)
    print("  METHOD 1: Standard CAN IDs (11-bit)")
    print("="*70)
    
    found = []
    
    for motor_id in range(1, 128):
        try:
            # RobStride enable command
            msg = can.Message(
                arbitration_id=0x7E8,
                data=[motor_id, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                is_extended_id=False
            )
            
            bus.send(msg)
            time.sleep(0.05)
            
            # Check for response
            response = bus.recv(timeout=0.15)
            if response:
                found.append(motor_id)
                print(f"  Found: ID {motor_id:3d} (0x{motor_id:02X})")
        except:
            pass
    
    print(f"\n✓ Method 1 found {len(found)} motor(s)")
    return found

def method2_extended_ids(bus):
    """Method 2: Extended 29-bit CAN IDs"""
    print("\n" + "="*70)
    print("  METHOD 2: Extended CAN IDs (29-bit)")
    print("="*70)
    
    found = []
    
    for motor_id in range(1, 128):
        try:
            # Try extended ID format
            msg = can.Message(
                arbitration_id=0x18000000 + motor_id,
                data=[motor_id, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                is_extended_id=True
            )
            
            bus.send(msg)
            time.sleep(0.05)
            
            response = bus.recv(timeout=0.15)
            if response:
                found.append(motor_id)
                print(f"  Found: ID {motor_id:3d} (Extended)")
        except:
            pass
    
    print(f"\n✓ Method 2 found {len(found)} motor(s)")
    return found

def method3_canopen_discovery(bus):
    """Method 3: CANopen Protocol Discovery"""
    print("\n" + "="*70)
    print("  METHOD 3: CANopen Protocol")
    print("="*70)
    
    found = []
    
    try:
        # Send NMT reset to all nodes
        print("  Sending NMT reset...")
        nmt_msg = can.Message(
            arbitration_id=0x000,
            data=[0x81, 0x00],  # Reset all nodes
            is_extended_id=False
        )
        bus.send(nmt_msg)
        time.sleep(0.5)
        
        # Listen for boot-up messages (0x700 + node_id)
        print("  Listening for boot-up messages...")
        start = time.time()
        while time.time() - start < 3.0:
            try:
                msg = bus.recv(timeout=0.1)
                if msg and 0x700 <= msg.arbitration_id <= 0x77F:
                    node_id = msg.arbitration_id - 0x700
                    found.append(node_id)
                    print(f"  Found: CANopen Node {node_id}")
            except:
                pass
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"\n✓ Method 3 found {len(found)} motor(s)")
    return found

def method4_broadcast_discovery(bus):
    """Method 4: Broadcast Discovery"""
    print("\n" + "="*70)
    print("  METHOD 4: Broadcast Discovery")
    print("="*70)
    
    found = []
    
    try:
        # Send broadcast enable
        print("  Sending broadcast enable...")
        broadcast = can.Message(
            arbitration_id=0x7FF,
            data=[0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            is_extended_id=False
        )
        bus.send(broadcast)
        
        # Listen for responses
        print("  Listening for responses...")
        start = time.time()
        seen_ids = set()
        
        while time.time() - start < 2.0:
            try:
                msg = bus.recv(timeout=0.1)
                if msg and msg.arbitration_id not in seen_ids:
                    seen_ids.add(msg.arbitration_id)
                    print(f"  Response: CAN ID 0x{msg.arbitration_id:03X}")
                    found.append(msg.arbitration_id)
            except:
                pass
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"\n✓ Method 4 found {len(found)} response(s)")
    return found

def method5_listen_passive(bus):
    """Method 5: Passive Listening"""
    print("\n" + "="*70)
    print("  METHOD 5: Passive Listening (No Commands)")
    print("="*70)
    
    found = []
    
    print("  Listening for spontaneous CAN traffic...")
    print("  (Motors might broadcast status automatically)")
    
    start = time.time()
    seen_ids = set()
    
    while time.time() - start < 5.0:
        try:
            msg = bus.recv(timeout=0.1)
            if msg and msg.arbitration_id not in seen_ids:
                seen_ids.add(msg.arbitration_id)
                print(f"  Traffic: CAN ID 0x{msg.arbitration_id:03X}, "
                      f"Data: {msg.data.hex()}")
                found.append(msg.arbitration_id)
        except:
            pass
    
    if not found:
        print("  No spontaneous traffic detected")
    
    print(f"\n✓ Method 5 found {len(found)} active ID(s)")
    return found

def method6_alternative_addresses(bus):
    """Method 6: Try Alternative CAN Addresses"""
    print("\n" + "="*70)
    print("  METHOD 6: Alternative CAN Addresses")
    print("="*70)
    
    found = []
    
    # Try different base addresses
    base_addresses = [0x100, 0x200, 0x300, 0x400, 0x500, 0x600]
    
    for base in base_addresses:
        print(f"\n  Testing base address 0x{base:03X}...")
        
        for offset in range(1, 16):
            try:
                msg = can.Message(
                    arbitration_id=base + offset,
                    data=[offset, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    is_extended_id=False
                )
                
                bus.send(msg)
                time.sleep(0.03)
                
                response = bus.recv(timeout=0.1)
                if response:
                    found.append((base, offset))
                    print(f"    Found: 0x{base:03X} + {offset}")
            except:
                pass
    
    print(f"\n✓ Method 6 found {len(found)} motor(s)")
    return found

def method7_config_mode_scan(bus):
    """Method 7: Configuration Mode Discovery"""
    print("\n" + "="*70)
    print("  METHOD 7: Configuration Mode Scan")
    print("="*70)
    
    found = []
    
    print("  Scanning for motors in configuration mode...")
    
    for motor_id in range(1, 128):
        try:
            # Configuration mode query (different command byte)
            msg = can.Message(
                arbitration_id=0x7E8,
                data=[motor_id, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                is_extended_id=False
            )
            
            bus.send(msg)
            time.sleep(0.05)
            
            response = bus.recv(timeout=0.15)
            if response:
                found.append(motor_id)
                print(f"  Found in config mode: ID {motor_id:3d}")
        except:
            pass
    
    print(f"\n✓ Method 7 found {len(found)} motor(s)")
    return found

def main():
    print("="*70)
    print("  COMPREHENSIVE CAN1 SCANNER")
    print("="*70)
    print()
    print("This will try EVERY discovery method on CAN1 GPIO")
    print()
    
    # Try multiple baud rates
    baud_rates = [921600, 1000000, 500000, 250000]
    
    all_results = {}
    
    for baud in baud_rates:
        print("\n" + "="*70)
        print(f"  TESTING AT {baud} BAUD")
        print("="*70)
        
        if not setup_can1(baud):
            print(f"Skipping {baud} baud (setup failed)")
            continue
        
        try:
            # Open CAN1 bus
            bus = can.Bus(channel='can1', interface='socketcan')
            print(f"✓ Connected to CAN1")
            print()
            
            results = {}
            
            # Try all methods
            results['standard'] = method1_standard_ids(bus)
            results['extended'] = method2_extended_ids(bus)
            results['canopen'] = method3_canopen_discovery(bus)
            results['broadcast'] = method4_broadcast_discovery(bus)
            results['passive'] = method5_listen_passive(bus)
            results['alternative'] = method6_alternative_addresses(bus)
            results['config_mode'] = method7_config_mode_scan(bus)
            
            bus.shutdown()
            
            all_results[baud] = results
            
        except Exception as e:
            print(f"\n✗ Error at {baud} baud: {e}")
            continue
    
    # Summary
    print("\n" + "="*70)
    print("  FINAL RESULTS")
    print("="*70)
    print()
    
    total_found = 0
    
    for baud, results in all_results.items():
        print(f"\nAt {baud} baud:")
        
        for method, found in results.items():
            if found:
                print(f"  {method}: {len(found)} motor(s)")
                total_found += len(found)
    
    print()
    print("="*70)
    
    if total_found == 0:
        print("✗ NO MOTORS FOUND ON CAN1")
        print()
        print("Possible reasons:")
        print("  1. Motors not connected to CAN1 GPIO")
        print("  2. Motors all on USB-to-CAN adapter")
        print("  3. CAN1 GPIO not properly configured")
        print("  4. Need CAN transceiver hardware")
        print()
        print("RECOMMENDATION:")
        print("  → Check if CAN transceiver is connected to CAN1 GPIO")
        print("  → Verify motors are wired to CAN1 bus")
        print("  → Try CAN0 instead")
    else:
        print(f"✓ FOUND {total_found} MOTORS/RESPONSES ON CAN1!")
        print()
        print("NEXT STEPS:")
        print("  → Identify which motors responded")
        print("  → Configure them to unique IDs")
        print("  → Test motor control")
    
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

