#!/usr/bin/env python3
"""
Scan CAN1 on Pins 33 and 37
Pin 33 (GPIO 13) - CAN1_DIN (RX)
Pin 37 (GPIO 26) - CAN1_DOUT (TX)
"""
import can
import time
import subprocess

def setup_can1(bitrate=921600):
    """Setup CAN1 at specified bitrate"""
    print(f"Configuring CAN1 (Pins 33/37) at {bitrate} baud...")
    
    try:
        # Bring down
        subprocess.run(['sudo', 'ip', 'link', 'set', 'can1', 'down'], 
                      capture_output=True)
        
        # Set bitrate
        subprocess.run(['sudo', 'ip', 'link', 'set', 'can1', 'type', 'can', 
                       'bitrate', str(bitrate)], check=True)
        
        # Bring up
        subprocess.run(['sudo', 'ip', 'link', 'set', 'can1', 'up'], check=True)
        
        print(f"✓ CAN1 configured at {bitrate} baud")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def scan_motors(bus, start=1, end=127):
    """Scan for motors using RobStride protocol"""
    found = []
    
    print(f"\nScanning IDs {start}-{end}...")
    
    for motor_id in range(start, end + 1):
        try:
            # RobStride enable command
            msg = can.Message(
                arbitration_id=0x7E8,
                data=[motor_id, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                is_extended_id=False
            )
            
            bus.send(msg)
            time.sleep(0.1)
            
            # Check for response
            response = bus.recv(timeout=0.2)
            if response:
                found.append(motor_id)
                print(f"  Found: ID {motor_id:3d} (0x{motor_id:02X})")
        except Exception as e:
            pass
    
    return found

def listen_for_traffic(bus, duration=5):
    """Listen for any CAN traffic"""
    print(f"\nListening for CAN traffic ({duration} seconds)...")
    
    messages = []
    start = time.time()
    
    while time.time() - start < duration:
        try:
            msg = bus.recv(timeout=0.1)
            if msg:
                messages.append(msg)
                print(f"  RX: ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex()}")
        except:
            pass
    
    return messages

def main():
    print("="*70)
    print("  CAN1 SCANNER (Pins 33 & 37)")
    print("="*70)
    print()
    print("Hardware:")
    print("  Pin 33 (GPIO 13) - CAN1_DIN (RX)")
    print("  Pin 37 (GPIO 26) - CAN1_DOUT (TX)")
    print()
    
    # Try multiple baud rates
    baud_rates = [921600, 1000000, 500000, 250000, 115200]
    
    all_results = {}
    
    for baud in baud_rates:
        print("\n" + "="*70)
        print(f"  TESTING AT {baud} BAUD")
        print("="*70)
        
        if not setup_can1(baud):
            continue
        
        try:
            bus = can.Bus(channel='can1', interface='socketcan')
            print("✓ Connected to CAN1")
            
            # Method 1: Active scan
            print("\n--- Method 1: Active Motor Scan ---")
            found_motors = scan_motors(bus, 1, 127)
            
            # Method 2: Passive listening
            print("\n--- Method 2: Passive Listening ---")
            traffic = listen_for_traffic(bus, duration=3)
            
            bus.shutdown()
            
            all_results[baud] = {
                'motors': found_motors,
                'traffic': len(traffic)
            }
            
            if found_motors or traffic:
                print(f"\n✓ Activity detected at {baud} baud!")
                break  # Found something, no need to try other baud rates
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("  RESULTS")
    print("="*70)
    print()
    
    total_motors = 0
    total_traffic = 0
    
    for baud, results in all_results.items():
        motors = results['motors']
        traffic = results['traffic']
        
        if motors or traffic:
            print(f"At {baud} baud:")
            if motors:
                print(f"  Motors found: {len(motors)}")
                print(f"  IDs: {motors}")
            if traffic:
                print(f"  CAN messages: {traffic}")
            
            total_motors += len(motors)
            total_traffic += traffic
    
    print()
    
    if total_motors == 0 and total_traffic == 0:
        print("✗ NO MOTORS OR TRAFFIC DETECTED ON CAN1")
        print()
        print("Possible reasons:")
        print("  1. No CAN transceiver connected to pins 33/37")
        print("  2. Motors not wired to CAN1 bus")
        print("  3. CAN transceiver needs power")
        print("  4. Wrong CAN-H/CAN-L wiring")
        print()
        print("Hardware requirements:")
        print("  - CAN transceiver (e.g., MCP2515, TJA1050)")
        print("  - Connect:")
        print("    Pin 33 → Transceiver RX")
        print("    Pin 37 → Transceiver TX")
        print("    Transceiver CANH → Motor CAN-H")
        print("    Transceiver CANL → Motor CAN-L")
        print("    GND → Common ground")
    else:
        print(f"✓ FOUND {total_motors} MOTORS ON CAN1!")
        print()
        print("Next steps:")
        print("  1. Identify which motors these are")
        print("  2. Configure to unique IDs")
        print("  3. Test motor control")
    
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

