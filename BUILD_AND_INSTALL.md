# DoItForMe Dash v1.4.5 — Recording/Playback Launch Fix

This version fixes the installed application attempting to start a missing subprocess when ARM RECORDING or ARM PLAYBACK is clicked. The packaged application launches its own EXE with `--record` or `--playback`, and the required worker modules are explicitly included. Worker launch errors now return an API error instead of an unhandled traceback.

## Build and reinstall (Windows)

1. Extract this ZIP to a writable folder.
2. Double-click `BUILD_INSTALLER.bat`. This version **always rebuilds** the application; do not copy the v1.4.4 compiled `dist` folder into it.
3. Approve MSVC/Inno Setup installation only if requested. Both tools are required on the BUILD PC, not on other PCs.
4. Wait for the `SUCCESS! Installer created` message. The script opens File Explorer at `installer\DoItForMeDash_Setup_1.4.5.exe`.
5. Close any running DoItForMe Dash server window, then run the new Setup EXE to update the existing installation.
6. Launch DoItForMe Dash using the desktop shortcut and test ARM RECORDING. Keep the DoItForMe Dash server window open.

**Important:** The ZIP contains the source and automated Windows installer builder, not a precompiled Windows Setup EXE. The EXE must be built on Windows using Nuitka/MSVC and Inno Setup.

The game requires Steam/Geometry Dash. Patterns are stored under Documents\DoItForMe Dash\patterns.
