# How to Run Motor Studio in English

## Found Executables

### Option 1: Motor Studio Driver
**Location**: `C:\Users\Owner\Downloads\motorstudio0.0.8\motorstudio0.0.8\driver.exe`

### Option 2: Motor Tools (Studio 2)
**17nm Motor Tool**: 
- `C:\Users\Owner\Downloads\Studio (2)\Studio\...\简易上位机\17nm上位机\motor_tool.exe`

**120nm Motor Tool**:
- `C:\Users\Owner\Downloads\Studio (2)\Studio\...\简易上位机\120nm上位机\z1_motor_tool.exe`

## Steps to Try English

### Method 1: Check Application Settings
1. **Run the executable** (double-click or run from command line)
2. **Look for language settings** in the application:
   - Check "Settings" or "设置" menu
   - Look for "Language" or "语言" option
   - Check "Options" or "选项" menu
   - Look for "Preferences" or "首选项"

### Method 2: Check System Language
Some applications use Windows system language:
1. Open **Windows Settings**
2. Go to **Time & Language** → **Language & Region**
3. Set **Windows display language** to **English**
4. Restart the application

### Method 3: Run and Look for Language Menu
Many Chinese applications have English option even if menu is in Chinese:
- Look for menu items like: 语言, 设置, 选项, English, 英文
- Common locations:
  - Top menu bar (File/Edit/View/Help)
  - Settings/Preferences dialog
  - About/Help menu

### Method 4: Use Translation Overlay
If no English option:
- Use Windows translation features
- Use screen translation tools (Google Translate app, etc.)
- Learn key Chinese terms:
  - 设置 = Settings
  - 语言 = Language  
  - 英文 = English
  - CAN ID = CAN ID (usually same)
  - 配置 = Configuration

## Running the Tools

### To run driver.exe:
```powershell
cd "C:\Users\Owner\Downloads\motorstudio0.0.8\motorstudio0.0.8"
.\driver.exe
```

### To run motor tools:
```powershell
# 17nm tool
cd "C:\Users\Owner\Downloads\Studio (2)\Studio\..."
.\简易上位机\17nm上位机\motor_tool.exe

# 120nm tool  
cd "C:\Users\Owner\Downloads\Studio (2)\Studio\..."
.\简易上位机\120nm上位机\z1_motor_tool.exe
```

## What to Look For

When the application opens, look for:
1. **CAN ID configuration option**
2. **Motor address/ID setting**
3. **Configuration menu**
4. **Settings/Preferences**
5. **Language selection**

Even if in Chinese, the CAN ID configuration option should be identifiable by:
- CAN ID numbers (1-31)
- Motor ID/Address labels
- Configuration/settings icons

## Recommendation

**Try running `driver.exe` first** - it's in the motorstudio folder and might be the main configuration tool. Check its menus for language settings or CAN ID configuration options.

