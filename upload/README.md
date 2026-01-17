# Upload – ESP32 / PlatformIO

Upload firmware to ESP32. **platformio.ini** must remain at the project root; these scripts `cd` to the root before running PlatformIO.

## Launchers

- **upload.ps1** – detect COM ports and upload (with bootloader instructions)
- **upload_manual.ps1** – manual flow: put ESP32 in bootloader, then upload

## Usage

Run from `upload/` or from project root:

```powershell
.\upload\upload.ps1
# or
.\upload\upload_manual.ps1
```

