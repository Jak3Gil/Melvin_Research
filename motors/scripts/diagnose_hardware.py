#!/usr/bin/env python3
"""
Hardware Diagnostic Script
Helps identify why motors aren't responding
"""

import serial
import struct
import time
import sys

def test_serial_port(port, baud):
    """Test if serial port is accessible"""
    print("\n" + "="*70)
    print("TEST 1: Serial Port Accessibility")
    print("="*70)
    
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
        print(f"✓ Port {port} opened successfully")
        print(f"  Baud rate: {baud}")
        print(f"  Timeout: {ser.timeout}s")
        ser.close()
        return True
    except serial.SerialException as e:
        print(f"✗ Cannot open port {port}")
        print(f"  Error: {e}")
        return False

def test_loopback(port, baud):
    """Test serial loopback (if TX and RX are connected)"""
    print("\n" + "="*70)
    print("TEST 2: Serial Loopback Test")
    print("="*70)
    print("(This only works if you have TX-RX loopback connected)")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
        
        test_data = b"LOOPBACK_TEST_12345"
        ser.write(test_data)
        ser.flush()
        time.sleep(0.1)
        
        received = ser.read(len(test_data))
        
        if received == test_data:
            print(f"✓ Loopback successful!")
            print(f"  Sent: {test_data.hex()}")
            print(f"  Received: {received.hex()}")
        elif received:
            print(f"⚠️  Partial loopback")
            print(f"  Sent: {test_data.hex()}")
            print(f"  Received: {received.hex()}")
        else:
            print(f"✗ No loopback (this is normal if TX-RX not connected)")
        
        ser.close()
        return len(received) > 0
    except Exception as e:
        print(f"✗ Loopback test failed: {e}")
        return False

def test_multiple_bauds(port):
    """Test different baud rates"""
    print("\n" + "="*70)
    print("TEST 3: Multiple Baud Rate Test")
    print("="*70)
    
    baud_rates = [115200, 250000, 500000, 921600, 1000000]
    results = {}
    
    for baud in baud_rates:
        print(f"\nTesting {baud} baud...")
        try:
            ser = serial.Serial(port, baud, timeout=0.5)
            time.sleep(0.3)
            
            # Try to enable motor 8
            packet = bytearray([0xAA, 0x55, 0x01, 0x08])
            packet.extend(struct.pack('<I', 8))
            packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            checksum = sum(packet[2:]) & 0xFF
            packet.append(checksum)
            
            ser.write(packet)
            ser.flush()
            time.sleep(0.2)
            
            response = ser.read(100)
            
            if response and len(response) > 4:
                print(f"  ✓ Got response at {baud}!")
                print(f"    {len(response)} bytes: {response.hex(' ')}")
                results[baud] = True
            else:
                print(f"  ✗ No response at {baud}")
                results[baud] = False
            
            ser.close()
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  ✗ Error at {baud}: {e}")
            results[baud] = False
    
    return results

def test_usb_adapter(port):
    """Test USB-to-CAN adapter"""
    print("\n" + "="*70)
    print("TEST 4: USB-to-CAN Adapter Test")
    print("="*70)
    
    try:
        ser = serial.Serial(port, 921600, timeout=0.5)
        
        # Check if adapter responds to any commands
        print("Checking adapter response...")
        
        # Try AT command (some adapters use this)
        ser.write(b"AT\r\n")
        ser.flush()
        time.sleep(0.2)
        response = ser.read(100)
        
        if response:
            print(f"✓ Adapter responded to AT command")
            print(f"  Response: {response}")
        else:
            print(f"⚠️  No response to AT command (may be normal)")
        
        # Check buffer status
        print(f"\nAdapter status:")
        print(f"  In waiting: {ser.in_waiting} bytes")
        print(f"  Out waiting: {ser.out_waiting} bytes")
        
        ser.close()
        return True
    except Exception as e:
        print(f"✗ Adapter test failed: {e}")
        return False

def continuous_monitor(port, baud, duration=10):
    """Continuously monitor for any activity"""
    print("\n" + "="*70)
    print(f"TEST 5: Continuous Monitor ({duration}s)")
    print("="*70)
    print("Monitoring for ANY activity on the bus...")
    print("(Try power cycling motors during this test)")
    
    try:
        ser = serial.Serial(port, baud, timeout=0.1)
        
        start_time = time.time()
        activity_count = 0
        
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            
            # Check for incoming data
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                activity_count += 1
                print(f"  [{elapsed:.2f}s] Activity! {len(data)} bytes: {data.hex(' ')}")
            
            # Every 2 seconds, send a test packet
            if int(elapsed) % 2 == 0 and elapsed > 0:
                if int(elapsed) not in [x for x in range(0, int(duration), 2)][:-1]:
                    continue
                    
                # Send enable to motor 8
                packet = bytearray([0xAA, 0x55, 0x01, 0x08])
                packet.extend(struct.pack('<I', 8))
                packet.extend([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                checksum = sum(packet[2:]) & 0xFF
                packet.append(checksum)
                
                ser.write(packet)
                ser.flush()
            
            time.sleep(0.1)
        
        ser.close()
        
        if activity_count > 0:
            print(f"\n✓ Detected {activity_count} activity events")
            return True
        else:
            print(f"\n✗ No activity detected in {duration} seconds")
            return False
            
    except Exception as e:
        print(f"✗ Monitor failed: {e}")
        return False

def main():
    port = '/dev/ttyUSB0'
    baud = 921600
    
    print("="*70)
    print("HARDWARE DIAGNOSTIC TOOL")
    print("="*70)
    print(f"\nPort: {port}")
    print(f"Default Baud: {baud}")
    print("\nThis will run multiple tests to identify hardware issues")
    print("="*70)
    
    results = {}
    
    # Test 1: Serial port
    results['serial_port'] = test_serial_port(port, baud)
    if not results['serial_port']:
        print("\n❌ CRITICAL: Cannot access serial port!")
        print("   Check:")
        print("   1. USB cable connected")
        print("   2. User in dialout group: sudo usermod -a -G dialout $USER")
        print("   3. Device permissions: ls -l /dev/ttyUSB0")
        return
    
    # Test 2: Loopback (optional)
    results['loopback'] = test_loopback(port, baud)
    
    # Test 3: Multiple baud rates
    results['baud_rates'] = test_multiple_bauds(port)
    
    # Test 4: USB adapter
    results['usb_adapter'] = test_usb_adapter(port)
    
    # Test 5: Continuous monitor
    print("\n⚠️  About to start 10-second continuous monitor")
    print("   Try power cycling motors during this test!")
    input("   Press Enter to continue...")
    results['monitor'] = continuous_monitor(port, baud, duration=10)
    
    # Summary
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    print(f"\n1. Serial Port: {'✓ OK' if results['serial_port'] else '✗ FAIL'}")
    print(f"2. Loopback: {'✓ OK' if results.get('loopback') else '⚠️  N/A'}")
    print(f"3. USB Adapter: {'✓ OK' if results['usb_adapter'] else '✗ FAIL'}")
    print(f"4. Monitor: {'✓ Activity detected' if results['monitor'] else '✗ No activity'}")
    
    print(f"\n5. Baud Rate Results:")
    for baud, success in results['baud_rates'].items():
        print(f"   {baud:>7} baud: {'✓ Response' if success else '✗ No response'}")
    
    # Diagnosis
    print("\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)
    
    any_baud_works = any(results['baud_rates'].values())
    
    if any_baud_works:
        print("\n✅ GOOD NEWS: Motors respond at some baud rate!")
        working_bauds = [b for b, s in results['baud_rates'].items() if s]
        print(f"   Working baud rates: {working_bauds}")
        print(f"\n   Use one of these baud rates for motor control")
    elif results['monitor']:
        print("\n⚠️  PARTIAL: Detected activity but no motor responses")
        print("   Possible issues:")
        print("   1. Wrong protocol/command format")
        print("   2. Motors in different mode")
        print("   3. CAN bus issues (termination)")
    else:
        print("\n❌ PROBLEM: No motor communication detected")
        print("\n   Most likely causes:")
        print("   1. Motors not powered on")
        print("      → Check motor power supply LEDs")
        print("      → Verify power connections")
        print()
        print("   2. CAN bus not connected")
        print("      → Check CAN-H wire (usually yellow/white)")
        print("      → Check CAN-L wire (usually green/blue)")
        print("      → Check GND connection")
        print()
        print("   3. Missing termination resistors")
        print("      → Need 120Ω at START of bus")
        print("      → Need 120Ω at END of bus")
        print("      → Measure: should be ~60Ω total")
        print()
        print("   4. Wrong USB-to-CAN adapter")
        print("      → Verify adapter is CH340/HL-340")
        print("      → Check adapter LEDs (TX/RX)")
        print()
        print("   5. Hardware failure")
        print("      → Try different USB port")
        print("      → Try different USB cable")
        print("      → Check for damaged connectors")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    if any_baud_works:
        print("\n1. Use the working baud rate")
        print("2. Run motor configuration script")
        print("3. Assign unique IDs to motors")
    else:
        print("\n1. Check motor power (LEDs on?)")
        print("2. Verify CAN bus wiring:")
        print("   - CAN-H connected to all motors")
        print("   - CAN-L connected to all motors")
        print("   - GND connected to all motors")
        print("3. Add termination resistors (120Ω at each end)")
        print("4. Power cycle everything")
        print("5. Run this diagnostic again")
    
    print()

if __name__ == '__main__':
    main()

