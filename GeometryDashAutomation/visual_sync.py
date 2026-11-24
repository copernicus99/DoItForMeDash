"""Visual start synchronizer. No memory inspection or game modification.

At F8, focus Geometry Dash on the level-selection screen.
We click the level title/banner at a position relative to the game window and identify
its first substantial visual transition. The timestamp is the capture time
of that transition, not an exact engine simulation frame.
"""
import sys
import time
import numpy as np
import mss
import pyautogui

pyautogui.PAUSE = 0


def active_game_rect():
    if sys.platform == 'win32':
        import pygetwindow as windows
    else:
        import pywinctl as windows
    window = windows.getActiveWindow()
    if window is None or 'geometry dash' not in str(window.title).lower():
        raise RuntimeError('Focus the Geometry Dash window before pressing F8.')
    if getattr(window, 'isMinimized', False):
        raise RuntimeError('Geometry Dash is minimized.')
    rect = (int(window.left), int(window.top), int(window.width), int(window.height))
    if rect[2] < 400 or rect[3] < 300:
        raise RuntimeError('Geometry Dash window is too small for visual synchronization.')
    return rect


def capture(sct, region):
    frame = np.asarray(sct.grab(region))[:, :, :3]
    return frame[::3, ::3].copy()


def start_level_visual(timeout=5.0, threshold=22.0, fraction=0.12, banner_x=0.50, banner_y=0.34):
    """Click level-selection title/banner, return first major scene-transition time.

    Does not claim exact frame synchronization. Fails closed on timeout.
    """
    x, y, w, h = active_game_rect()
    # Coordinates are relative to the Geometry Dash window, not the desktop.
    # The title/banner is clickable on the level-selection screen.
    # Default center: 50% across, 34% down (includes a small window title bar).
    mx = x + round(w * banner_x)
    my = y + round(h * banner_y)
    # Central gameplay area; excludes borders, window title bar and progress UI.
    region = {'left': x + round(w * .20), 'top': y + round(h * .20),
              'width': round(w * .60), 'height': round(h * .55)}
    with mss.mss() as sct:
        before = capture(sct, region)
        print(f'Visual sync armed; clicking level title/banner at ({mx}, {my}) within window ({x}, {y}, {w}, {h}).', flush=True)
        pyautogui.click(mx, my)
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            frame = capture(sct, region)
            timestamp = time.perf_counter_ns()
            delta = np.abs(frame.astype(np.int16) - before.astype(np.int16))
            changed = float(np.mean(np.max(delta, axis=2) > threshold))
            if changed >= fraction:
                print(f'Visual level transition detected (changed pixels: {changed:.1%}); T=0.', flush=True)
                return timestamp
            time.sleep(.002)
    raise RuntimeError('Visual sync timed out. Confirm the level-selection title/banner is visible and the game is focused; retry F8.')
