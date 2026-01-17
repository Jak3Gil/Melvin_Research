# Motors – CAN / L91 / Robstride

All motor-related scripts, documentation, and launchers for CAN bus, L91 protocol, Robstride, and Motor Studio.

## Structure

| Folder | Contents |
|--------|----------|
| **docs/** | Markdown and text documentation (~80 files): configuration, troubleshooting, investigation, Motor Studio, L91, Robstride, firmware, protocols |
| **scripts/** | Python scripts (~227 files): activation, configuration, discovery, control, capture, analysis, tests |
| **launchers/** | Batch (.bat), PowerShell (.ps1), and shell (.sh) scripts to run Motor Studio, scans, tests, and CAN setup |

## Quick start

- **Motor Studio:** `docs/START_HERE_MOTOR_STUDIO.md` and `launchers/launch_motor_studio.bat` or `launchers/launch_motor_studio_english.ps1`
- **Config:** `docs/QUICK_START_MOTOR_CONFIG.md`, `docs/MOTOR_CONFIGURATION_GUIDE.md`
- **Jetson:** `docs/JETSON_MOTOR_QUICK_START.md`, `scripts/jetson_motor_interface.py`
- **Safety:** `docs/SAFETY_WARNING.md`, `scripts/emergency_stop_all_motors.py`

## Docs (high level)

- **Motor Studio:** `START_HERE_MOTOR_STUDIO.md`, `MOTOR_STUDIO_ENGLISH_GUIDE.md`, `MOTOR_STUDIO_FORMAT_DISCOVERED.md`, `RUN_MOTOR_STUDIO.md`
- **L91:** `L91_MOTOR_SETUP.md`, `L91_PROTOCOL_USAGE.md`, `L91_CONFIG_ATTEMPT.md`
- **Robstride:** `ROBSTRIDE_CONFIGURATION_GUIDE.md`, `ROBSTRIDE_SDK_FINDINGS.md`, `ROBSTRIDE_MOTOR_STUDIO_INFO.md`
- **CAN / protocols:** `CAN_BUS_ARBITRATION_EXPLANATION.md`, `can_bus_addressing_issue.md`, `PROTOCOL_ANALYSIS_SUMMARY.md`, `PROTOCOL_SWITCH_GUIDE.md`
- **Configuration:** `MOTOR_CONFIGURATION_GUIDE.md`, `CONFIGURE_MOTOR_IDS.md`, `REMAP_INSTRUCTIONS.md`, `SOLUTION_MOTOR_CONFIGURATION.md`
- **Investigation / status:** `FINAL_MOTOR_SOLUTION_SUMMARY.md`, `COMPLETE_MOTOR_SCAN_RESULTS.md`, `MOTOR_ID_MAPPING.md`, `INVESTIGATION_SUMMARY.md`
- **Firmware:** `FIRMWARE_UPDATE_GUIDE.md`, `HOW_TO_UPDATE_FIRMWARE.md`, `WHY_FIRMWARE_UPDATE_FAILS.md`

## Launchers

- Motor Studio: `launch_motor_studio*.bat`, `launch_motor_studio*.ps1`, `restore_motor_studio_languages.ps1`
- Run workflows: `run_activate.bat`, `run_configure_all.bat`, `run_investigation.bat`, `run_remap.bat`
- Scans / CAN: `scan_motors.ps1`, `check_com3_can.ps1`, `find_usb_can.ps1`, `test_can_bitrates.sh`, `test_slcan_setup.sh`
- Tests: `test_motors.bat`, `test_simple.bat`, `test_motors.ps1`
- Robstride: `setup_robstride_bridge.sh`

## Scripts (by role)

- **Activation:** `activate_*`, `power_sequence_*`, `clear_fault_*`, `wake_up_motors.py`
- **Configuration:** `configure_*`, `reconfigure_*`, `remap_motor_ids.py`, `reset_motor_addresses.py`, `setup_robstride_*`
- **Discovery / scan:** `find_*`, `scan_*`, `discover_*`, `detect_motors_*`, `broadcast_discovery_*`, `query_motors_*`, `identify_*`, `map_*`
- **Control:** `move_motor*`, `move_motors_*`, `move_7_9*`, `emergency_stop_*`, `release_motor_brake.py`, `example_motor_control.py`, `connect_motors_*`
- **Motor Studio / capture:** `capture_motor_studio_*`, `send_motor_studio_*`, `monitor_motor_studio_*`, `simple_motor_studio.py`, `auto_capture_*`, `automated_capture.py`
- **Decode / format:** `decode_motor*`, `decode_all_motors_*`, `decode_new_response_*`
- **Debug / analysis:** `debug_*`, `diagnose_*`, `analyze_*`, `comprehensive_*`, `deep_*`, `investigate_*`, `verify_*`
- **Tests:** `test_motor*`, `test_motors_*`, `test_7_9*`, `test_canopen_*`, `test_l91_*`, `test_*_jetson.py`, etc.
- **OTA:** `ota_firmware_updater*.py`

Embedded L91 code stays in `../src/` (`l91_motor.cpp`, `l91_motor.h`) for the PlatformIO build.

