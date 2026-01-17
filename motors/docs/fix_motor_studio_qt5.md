# Fix Motor Studio Qt5Core.dll Error

## Problem
Motor Studio is missing Qt5Core.dll - this is a required library for the application to run.

## Solutions

### Solution 1: Download and Install Qt5 Runtime (Recommended)

**Option A: Install Visual C++ Redistributables**
1. Download Microsoft Visual C++ Redistributables:
   - Visit: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Or search: "Visual C++ Redistributable latest"
   - Install both x64 and x86 versions

**Option B: Install Qt5 Runtime**
1. Download Qt5 from: https://www.qt.io/download-open-source
2. Or use the minimal Qt5 runtime installer
3. Install to default location

### Solution 2: Use Alternative Motor Configuration Method

Since Motor Studio has dependency issues, let's configure motors directly via Python on the Jetson.

I'll create a script to configure motor IDs without needing Motor Studio.

### Solution 3: Copy Qt5 DLLs to Motor Studio Folder

If you have Qt5 installed elsewhere on your system, you can copy the DLLs:

**Required DLLs:**
- Qt5Core.dll
- Qt5Gui.dll
- Qt5Widgets.dll
- Qt5Network.dll (possibly)

**Copy them to:**
```
c:\Users\Owner\Downloads\Studio (2)\Studio\...\motor_tool.exe (same folder)
```

### Solution 4: Try the Other Motor Studio Version

The `driver.exe` might be a standalone version without Qt dependencies:
```
c:\Users\Owner\Downloads\motorstudio0.0.8\motorstudio0.0.8\driver.exe
```

---

## 🚀 BEST SOLUTION: Configure Motors via Python Script

Since Motor Studio has issues, I'll create a Python script that can configure motor IDs directly from the Jetson.

This will:
- Scan for motors
- Let you test each one
- Change their CAN IDs
- No Windows software needed!

Would you like me to create this script?

