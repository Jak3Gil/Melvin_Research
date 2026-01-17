# Motor Studio Command Capture Guide

## 🎯 Goal

Capture the exact commands Motor Studio sends to motors, then analyze them to create Python code that replicates Motor Studio's CANopen protocol.

---

## 📋 Quick Start

### Step 1: Capture Commands

**Option A: Use Serial Port Monitor Software (Easiest)**
1. See `serial_port_monitor_instructions.md` for detailed instructions
2. Recommended: Free Serial Port Monitor (free trial)

**Option B: Use Virtual Ports**
1. Install com0com (virtual port driver)
2. Create port pair (COM10 ↔ COM11)
3. Motor Studio → COM10
4. Capture script → COM11

**Option C: Try Python Script**
1. Run `capture_motor_studio_commands.py`
2. Note: Windows port locking may prevent this from working

### Step 2: Analyze Captured Commands

```bash
python analyze_captured_commands.py captured_file.csv
```

The analyzer will:
- Parse hex commands
- Identify AT/L91 format
- Detect CANopen messages
- Generate Python code examples
- Show command patterns

### Step 3: Use Generated Code

The analysis will show you:
- Exact command format Motor Studio uses
- CANopen message structure
- How to replicate in Python

---

## 📁 Files

- `capture_motor_studio_commands.py` - Python capture script (may not work due to Windows port locking)
- `serial_port_monitor_instructions.md` - Detailed instructions for serial port monitoring
- `analyze_captured_commands.py` - Analyzes captured commands and generates Python code

---

## ⚠️ Important Notes

- **Windows locks COM ports** - Only one program can use a port at a time
- **Use serial port monitor software** for best results
- **Capture both TX and RX** - Need to see commands AND responses
- **Export as CSV** - Best format for analysis

---

## 🚀 Next Steps

1. Capture Motor Studio commands using monitor software
2. Export as CSV
3. Run analyzer script
4. Use generated Python code to replicate CANopen protocol

