#!/usr/bin/env python3
"""Just listen - don't send anything"""
import serial, time

print("Listening on /dev/ttyUSB0 for 10 seconds...")
print("(Motors might send status messages on startup)\n")

ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0.1)

start = time.time()
count = 0

while time.time() - start < 10:
    data = ser.read(100)
    if data:
        count += len(data)
        print(f"[{time.time()-start:.1f}s] Received: {data.hex()}")

ser.close()

if count > 0:
    print(f"\n✓ Received {count} bytes total")
    print("  Motors are sending data!")
else:
    print("\n✗ No data received")
    print("  Motors are completely silent")

