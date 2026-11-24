"""Replay recorded events after visually synchronizing a new level start."""
import argparse
import threading
from pathlib import Path
from pynput import keyboard
from common import PATTERNS, launch_game, load_pattern, sleep_until
from visual_sync import start_level_visual


def main():
    p = argparse.ArgumentParser()
    p.add_argument('pattern')
    p.add_argument('--offset-ms', type=float, default=0.0)
    p.add_argument('--no-launch', action='store_true')
    args = p.parse_args()
    path = Path(args.pattern)
    if not path.exists():
        path = PATTERNS / (args.pattern if args.pattern.endswith('.json') else args.pattern + '.json')
    data = load_pattern(path)
    if data.get('sync_method') != 'visual_scene_transition_v1':
        raise ValueError('This recording predates visual synchronization. Re-record with v1.3 for aligned playback.')
    print(f'Loaded {len(data["events"])} events from {path}; offset {args.offset_ms} ms.', flush=True)
    if not args.no_launch:
        launch_game()
    print('Open the LEVEL SELECTION screen with the title/banner; press F8. F9 stops.', flush=True)
    started = threading.Event()
    stopped = threading.Event()
    state = {'start': None, 'busy': False}

    def sync_worker():
        try:
            start = start_level_visual()
            if not stopped.is_set():
                state['start'] = start
                print('PLAYBACK: visual start synchronized.', flush=True)
        except Exception as exc:
            print(f'Visual sync error: {exc}; return to the level-selection screen and retry F8.', flush=True)
            state['busy'] = False
            return
        started.set()

    def on_press(key):
        if key == keyboard.Key.f8 and not state['busy'] and not stopped.is_set():
            state['busy'] = True
            threading.Thread(target=sync_worker, daemon=True).start()
        elif key == keyboard.Key.f9:
            stopped.set()
            started.set()
            return False

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    controller = keyboard.Controller()
    held = False
    try:
        started.wait()
        if stopped.is_set() or state['start'] is None:
            return
        for event in data['events']:
            target = state['start'] + event['t_ns'] + round(args.offset_ms * 1e6)
            if not sleep_until(target, stopped):
                break
            if event['action'] == 'down':
                controller.press(keyboard.Key.space)
                held = True
            else:
                controller.release(keyboard.Key.space)
                held = False
        print('Stopped.' if stopped.is_set() else 'Playback completed.', flush=True)
    finally:
        if held:
            controller.release(keyboard.Key.space)
        listener.stop()

if __name__ == '__main__':
    main()
