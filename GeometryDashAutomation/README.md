# Geometry Dash Automation v1.3.2 — Title/Banner Start + Visual Synchronization

This unofficial local desktop tool records spacebar down/up events and replays them in Geometry Dash. It includes a local web dashboard.

## Installation

Install Python 3.10+ and Steam/Geometry Dash. Extract this entire folder into your PyCharm project root (not `.venv` or `.idea`). Keep your existing `patterns/` recordings before overwriting anything.

```bash
python -m pip install -r requirements.txt
python START_DASHBOARD.py
```

Open http://127.0.0.1:8765 on the **same PC** as the game. For macOS grant Accessibility and Screen Recording permissions; Linux X11 is preferred (Wayland may block global input or screenshots).

## NEW v1.3.1 procedure — do NOT pause the level

1. Open Geometry Dash and navigate to the **level-selection screen** (e.g., Stereo Madness, showing the large clickable level title/banner). Do **not** enter the level or press Esc.
2. In the dashboard choose Record, give it a name, and click **Arm Recording**. Disable "Launch through Steam" if the game is already running.
3. Return to the game, press **F8**. No hovering or calibration is needed. Do not move the game window while visual synchronization is underway.
4. Python clicks the title/banner at a window-relative location (50% across, 34% down) and samples the game window. Once the first substantial scene change is detected, it logs `T=0` and begins recording. Play using Space.
5. Press **F9** to save (or F10 to discard). The pattern appears in `patterns/`.
6. For playback, return to the **same level card** (not the pause screen), arm playback, press F8. F9 stops playback. Playback offset is fixed at **0 ms** in the dashboard.

## How visual sync works and limitations

The same capture/click/detection algorithm runs during recording and playback. It timestamps the first major change in a central region of the game window after clicking the title/banner. This avoids the inconsistent manual pause location. **It does not measure the game's internal simulation frame** and cannot guarantee frame-perfect alignment. Transition animations, overlays, video settings, different frame rates, performance, and the game version can cause offset or false detections. The log reports the percentage of pixels changed; if the visual sync times out, check the level card and retry F8.

Patterns recorded with versions 1.0–1.2 used pause/resume-relative timing and are **not compatible** with visual-start playback. v1.3 explicitly refuses to replay them instead of silently misaligning jumps. Re-record those levels in v1.3. Existing pattern files are not deleted.

## Keyboard shortcuts

- **F8:** click level-selection title/banner and synchronize visually
- **Space:** jump (recorded down/up events)
- **F9:** save recording / emergency stop playback
- **F10:** cancel recording

## CLI

```bash
python RECORD.py --name stereo_madness --no-launch
python PLAYBACK.py stereo_madness --offset-ms 0 --no-launch
```

## Troubleshooting

- Missing module: run `python -m pip install -r requirements.txt` in the interpreter PyCharm uses.
- F8 not detected: check the dashboard log and OS input permissions.
- F8 does not start level: game must be foreground on the level-selection screen with the clickable title/banner visible.
- Visual sync timeout: ensure no overlay covers the game and the level-selection screen is visible; retry F8.
- Game starts but jumps miss: verify recording and playback use the same level/game version/FPS; verify the level and frame rate match; the dashboard uses a fixed 0 ms offset.
- On some systems the mouse click or global keyboard events may be blocked by game input handling or OS permissions.

The dashboard server binds only to 127.0.0.1. This project is unofficial and not affiliated with Geometry Dash or RobTop Games.

## v1.3.1 click position

The default click is 50% across and 34% down the Geometry Dash window (including its title bar). If your level-selection layout differs, edit `banner_x` and `banner_y` defaults in `visual_sync.py`. The program detects a substantial scene change, **not** the exact simulation start frame. Do not click the green triangle on the pause screen: that is Resume, not level start.

## v1.3.2 dashboard updates

The Steam launch checkboxes default to off; the title is displayed on one line when space permits; recording/playback directions are in the corresponding cards; timing offset and Stop Process controls are hidden; the console filters repeated navigation prompts; and the quick-start tiles have been removed. Use F9 to save/stop or F10 to cancel recording. The underlying CLI still accepts an optional timing offset for advanced troubleshooting.


## Dashboard v1.3.4
The dashboard no longer offers Steam launch checkboxes. Recording and playback sessions are always started with `--no-launch`; open Geometry Dash manually before arming. The workflow instructions are numbered, and the pattern controls are embedded directly under step 1, with the ARM buttons under step 2.
