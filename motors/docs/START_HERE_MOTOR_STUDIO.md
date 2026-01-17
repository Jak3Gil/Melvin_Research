# 🚀 START HERE - Motor Studio Quick Start

## ✅ FOUND: Working Motor Studio!

**Location**: `C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\motor_tool.exe`

This version has all the Qt5 DLLs and should work perfectly!

---

## 🎯 Launch Motor Studio (Choose One Method)

### ⭐ Method 1: Easy Launcher (RECOMMENDED)
```cmd
cd F:\Melvin_Research\Melvin_Research
launch_motor_studio.bat
```
Then press **1** to launch the v00122 version with English settings.

### Method 2: PowerShell Script
```powershell
cd F:\Melvin_Research\Melvin_Research
.\launch_motor_studio_english.ps1
```

### Method 3: Direct Launch
Double-click:
```
C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\motor_tool.exe
```

---

## 🌐 If Motor Studio Opens in Chinese

**Don't panic!** Here's what to do:

### Quick Translation Guide
- **设置** = Settings
- **语言** = Language  
- **英文** = English

### Steps:
1. Look for **设置** (Settings) in the menu bar
2. Find **语言** (Language) option
3. Select **English** or **英文**
4. Restart Motor Studio

**OR** use the translation guide: `CHINESE_TO_ENGLISH_MENU.md`

---

## 🔌 Connect to Your Motors

1. **Connect CAN adapter** to USB (usually COM3)
2. **Power on motors**
3. In Motor Studio:
   - Select **COM port** (COM3)
   - Set **baud rate** to **921600**
   - Click **Connect** button
   - Click **Scan** button
4. Your motors should appear!

---

## 📚 Documentation Files Created

- `MOTOR_STUDIO_ENGLISH_GUIDE.md` - Complete guide
- `CHINESE_TO_ENGLISH_MENU.md` - Translation reference
- `launch_motor_studio_english.bat` - English launcher
- `launch_motor_studio_english.ps1` - PowerShell launcher
- `simple_motor_studio.py` - Python alternative (if GUI doesn't work)

---

## 🆘 Troubleshooting

### Motor Studio won't open
✅ **Solution**: Use the launcher scripts - they set up the environment correctly

### Still getting Qt5 DLL errors
✅ **Solution**: The v00122 version has all DLLs included. Make sure you're using:
```
C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\motor_tool.exe
```

### Can't find motors
✅ **Check**:
- COM port is correct (usually COM3)
- Baud rate is 921600
- Motors are powered on
- CAN adapter is connected

### Interface is in Chinese
✅ **Solution**: See `CHINESE_TO_ENGLISH_MENU.md` for translations

---

## 🐍 Alternative: Python Motor Studio

If the GUI doesn't work, use the Python version:

```cmd
cd F:\Melvin_Research\Melvin_Research
python simple_motor_studio.py
```

Features:
- Scan for motors
- Change CAN IDs
- Enable/disable motors
- Test motor movement
- All in English!

---

## 🎉 You're Ready!

1. Launch Motor Studio using Method 1 above
2. Connect to your motors
3. Start configuring!

**Need help?** Check the other documentation files or ask!

Good luck! 🚀

