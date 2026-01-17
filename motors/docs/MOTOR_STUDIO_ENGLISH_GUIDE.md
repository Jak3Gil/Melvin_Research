# Motor Studio - English Language Guide

## ✅ Working Motor Studio Found!

**Location**: `C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122\motor_tool.exe`

This version includes all required Qt5 DLLs and should work properly!

## 🚀 Quick Launch Options

### Option 1: Use the Launcher (Easiest)
```cmd
cd F:\Melvin_Research\Melvin_Research
launch_motor_studio.bat
```
Then select **Option 1** for the v00122 Motor Studio with English settings.

### Option 2: PowerShell Script
```powershell
cd F:\Melvin_Research\Melvin_Research
.\launch_motor_studio_english.ps1
```

### Option 3: Direct Launch
```cmd
cd C:\Users\Owner\Downloads\motor_tool_win_v00122\motor_tool_win_v00122
motor_tool.exe
```

## 🌐 Changing Language to English

If the Motor Studio opens in Chinese, follow these steps:

### Method 1: Look for Settings Menu
1. Look for the **Settings** menu (might show as "设置")
2. Find **Language** option (might show as "语言")
3. Select **English** (might show as "英文")
4. Restart the application

### Method 2: Common Chinese Menu Terms
- **设置** = Settings
- **语言** = Language
- **英文** = English
- **工具** = Tools
- **帮助** = Help
- **文件** = File
- **编辑** = Edit

### Method 3: Use Environment Variables
The launcher scripts set these environment variables to force English:
- `LANG=en_US`
- `LC_ALL=en_US.UTF-8`
- `QT_TRANSLATE_LANG=en`

## 📋 What You Can Do in Motor Studio

Once open, you can:
- ✅ **Scan for motors** - Find all connected motors
- ✅ **Change CAN IDs** - Reconfigure motor addresses
- ✅ **Test motors** - Enable/disable and test movement
- ✅ **Configure parameters** - Set motor parameters
- ✅ **Monitor status** - View motor position, velocity, torque

## 🔌 Connection Setup

Before using Motor Studio:

1. **Connect your CAN adapter** to USB (usually COM3)
2. **Set the correct COM port** in Motor Studio
3. **Set baud rate** to **921600** (for L91 protocol)
4. **Power on your motors**

## 🆘 Troubleshooting

### Motor Studio won't open
- Make sure you're running from the correct folder
- Check that all DLL files are present
- Try running as Administrator

### Can't find motors
- Check COM port is correct
- Verify baud rate is 921600
- Ensure motors are powered on
- Check CAN adapter connection

### Still in Chinese
- Use the translation guide above
- Look for gear/settings icon (⚙️)
- Try the environment variable method

## 🐍 Alternative: Python Motor Studio

If the GUI Motor Studio doesn't work, you can use the Python alternative:

```powershell
cd F:\Melvin_Research\Melvin_Research
python simple_motor_studio.py
```

This provides:
- Motor scanning
- ID configuration
- Motor testing
- All via command-line interface

## 📝 Notes

- The v00122 version is the most complete and should work best
- English translation files are included (`translations/qt_en.qm`)
- All required Qt5 DLLs are bundled with this version
- This is the official Robstride Motor Studio

## 🎯 Next Steps

1. Launch Motor Studio using one of the methods above
2. Connect to your motors via COM port
3. Scan for motors to find their current IDs
4. Configure/test as needed

Good luck! 🚀

