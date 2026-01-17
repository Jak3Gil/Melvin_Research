# Serial Port Monitor Instructions

## 🎯 Goal

Capture the exact commands that Motor Studio sends to your motors so we can replicate them in Python.

---

## ⚠️ Windows COM Port Locking

**The Problem:** Windows locks COM ports exclusively - only one program can use a port at a time.

**The Solution:** Use serial port monitor software that works at a lower level (driver level), allowing it to monitor ports without locking them.

---

## 📋 Method 1: Free Serial Port Monitor (RECOMMENDED)

### Step 1: Download and Install

1. **Download:** https://free-serial-port-monitor.com/
   - Free version available (15-day trial)
   - Or purchase full version (~$50)

2. **Install:**
   - Run installer
   - Follow installation wizard
   - May require admin privileges

### Step 2: Set Up Monitoring

1. **Launch Serial Port Monitor**
   - Open the application
   - You should see the main interface

2. **Create New Session:**
   - Click "New Session" or File → New Session
   - Choose "Session Type": Select "Serial Port" or "Monitor"
   - Click "Start" or "Next"

3. **Select Port:**
   - Choose your COM port (e.g., COM3, COM4)
   - Set baud rate: **921600**
   - Set other parameters if needed:
     - Data bits: 8
     - Stop bits: 1
     - Parity: None
     - Flow control: None

4. **Start Monitoring:**
   - Click "Start" or "OK"
   - Monitor should now be listening

### Step 3: Capture Motor Studio Commands

1. **Keep Monitor Running:**
   - Leave Serial Port Monitor open and running
   - You should see an empty capture window

2. **Open Motor Studio:**
   - Launch `motor_tool.exe`
   - Connect to the same COM port
   - Motor Studio should connect successfully (monitor doesn't lock the port)

3. **Perform Actions:**
   - Scan for motors
   - Enable a motor
   - Move a motor
   - Change motor settings
   - Each action will generate commands

4. **View Captured Data:**
   - Commands should appear in the monitor window
   - You'll see:
     - Timestamp
     - Direction (TX/RX - Transmit/Receive)
     - Hex data
     - ASCII representation

### Step 4: Export Captured Data

1. **Select Data:**
   - Select all captured commands (Ctrl+A)
   - Or select specific commands

2. **Export:**
   - Right-click → Export
   - Or File → Export
   - Choose format:
     - **CSV** (best for analysis)
     - **TXT** (text format)
     - **Hex** (hex dump)

3. **Save File:**
   - Save as `motor_studio_capture.csv` or similar
   - Share the file so we can analyze it

---

## 📋 Method 2: PortMon (Sysinternals - FREE)

### Step 1: Download

1. **Download PortMon:**
   - https://docs.microsoft.com/en-us/sysinternals/downloads/portmon
   - Free tool from Microsoft
   - Older interface but works

2. **Extract:**
   - Extract ZIP file
   - Run `portmon.exe`

### Step 2: Set Up

1. **Launch PortMon:**
   - Run as Administrator (may be required)
   - You'll see the monitoring window

2. **Configure:**
   - Options → Capture Events
   - Select your COM port
   - Or capture all ports

3. **Start Capture:**
   - File → Connect to Local Computer
   - Capture should start

### Step 3: Capture

1. **Run Motor Studio**
2. **Watch PortMon window**
3. **See serial commands appear**
4. **Export or copy data**

**Note:** PortMon shows low-level Windows API calls, so the format may be less readable than dedicated serial monitors.

---

## 📋 Method 3: Virtual Port Pair (com0com - FREE)

This method creates virtual COM port pairs - Motor Studio uses one, your script uses the other.

### Step 1: Download and Install

1. **Download com0com:**
   - https://sourceforge.net/projects/com0com/
   - Free virtual serial port driver

2. **Install:**
   - Run installer
   - **Requires admin privileges**
   - May need to disable driver signing on Windows

3. **Create Port Pair:**
   - Open com0com setup program
   - Create a pair (e.g., COM10 <-> COM11)
   - These ports are now connected

### Step 2: Use the Virtual Ports

1. **Connect Motor Studio to COM10**
2. **Run capture script on COM11**
3. **All data flows through both ports**
4. **Both programs can use ports simultaneously**

### Step 3: Capture

- Motor Studio sends to COM10
- Your script receives on COM11
- Capture all commands!

---

## 📋 Method 4: Alternative: Serial Port Monitor (ELTIMA)

### Commercial Option

1. **Download:** https://www.eltima.com/products/serial-port-monitor/
   - Paid software (~$200)
   - Free trial available
   - More features than free options

2. **Use similar to Free Serial Port Monitor**

---

## 📋 Method 5: Capture on Jetson (Linux)

If you have access to the Jetson's CAN bus:

### Using candump

```bash
# On Jetson
ssh melvin@192.168.1.119

# Monitor CAN bus traffic
candump -L can1 > motor_studio_capture.log

# Or with timestamps
candump -t z can1 > motor_studio_capture.log

# Or display CANopen-specific IDs
candump -L can1 | grep -E "600|601|602|700|200|300"
```

### Using can-utils

```bash
# Install can-utils if needed
sudo apt-get install can-utils

# Capture all traffic
candump can1 -l -t z

# View captured file
cat candump.log
```

---

## 📊 What to Look For

When capturing, you're looking for:

### 1. Initialization Commands

```
AT+MODE=...
AT+BAUD=...
AT+CANOPEN=...
```

### 2. CANopen SDO Commands

```
CAN ID: 0x601 (0x600 + node_id 1)
Data: [0x40, 0x00, 0x10, 0x00, ...]  (Read Device Type)
```

### 3. Motor Control Commands

```
CAN ID: 0x201 (0x200 + node_id 1)  (PDO)
Data: [position_low, position_high, velocity, ...]
```

### 4. NMT Commands

```
CAN ID: 0x000
Data: [0x01, node_id]  (Start node)
Data: [0x02, node_id]  (Stop node)
```

---

## 🔍 Example Capture Output

You should see something like:

```
Time        Direction  Port    Data
----------------------------------------
10:23:45.123  TX      COM3    41 54 00 07 E8 01 01 00 0D 0A
10:23:45.145  RX      COM3    41 54 00 07 E8 01 4B 00 10 00 ...
10:23:45.200  TX      COM3    41 54 20 07 E8 01 40 00 10 00 ...
10:23:45.223  RX      COM3    41 54 20 07 E8 01 4B 00 10 00 ...
```

---

## 📤 Exporting and Sharing

Once you have captured data:

1. **Export as CSV or TXT**
2. **Save the file**
3. **Share it** so we can analyze:
   - Look for patterns
   - Identify command format
   - Convert to Python code

---

## 🎯 Recommended Approach

**For Windows users (easiest):**

1. **Use Free Serial Port Monitor**
   - Download free trial
   - Monitor your COM port
   - Capture Motor Studio commands
   - Export as CSV
   - Share with me for analysis

2. **Or use com0com virtual ports**
   - Create port pair
   - Motor Studio → COM10
   - Python script → COM11
   - Capture all traffic

**For Linux/Jetson users:**

1. **Use candump**
   - Monitor CAN bus directly
   - Capture all CAN frames
   - Analyze CANopen messages

---

## 💡 Tips

- **Capture multiple sessions:** Scan, enable motor, move motor, etc.
- **Save separate files:** One for each action type
- **Include timestamps:** Helps understand command sequences
- **Export in readable format:** CSV is best for analysis
- **Capture both TX and RX:** Need to see responses too

---

## 📞 Next Steps

Once you have captured data:

1. **Save the capture file**
2. **Run the analysis script:** `analyze_captured_commands.py`
3. **Share results** so we can create the correct Python code

The analysis script will:
- Parse captured commands
- Identify patterns
- Extract CANopen message format
- Generate Python code to replicate them

