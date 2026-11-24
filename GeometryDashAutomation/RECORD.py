"""Record jump events relative to a visually detected fresh level start."""
import argparse
import threading
import time
from pynput import keyboard
from common import launch_game, save_pattern
from visual_sync import start_level_visual


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--name', default='my_level')
    p.add_argument('--no-launch', action='store_true')
    args = p.parse_args()
    if not args.no_launch:
        launch_game()
    print('Navigate to the LEVEL SELECTION screen showing the large clickable level title/banner. Do not pause.', flush=True)
    print('Arm, return to game, F8 clicks the title/banner + visually synchronizes. F9 saves; F10 cancels.', flush=True)
    state = {'phase': 'armed', 'down': False, 'start': None, 'events': [], 'cancel': False}
    lock = threading.RLock()
    done = threading.Event()

    def sync_worker():
        try:
            t0 = start_level_visual()
            with lock:
                if state['phase'] == 'syncing':
                    state['start'] = t0
                    state['phase'] = 'recording'
                    print('RECORDING: visual start synchronized.', flush=True)
        except Exception as exc:
            with lock:
                if state['phase'] == 'syncing':
                    state['phase'] = 'armed'
            print(f'Visual sync error: {exc}', flush=True)

    def on_press(key):
        with lock:
            if key == keyboard.Key.f8 and state['phase'] == 'armed':
                state['phase'] = 'syncing'
                threading.Thread(target=sync_worker, daemon=True).start()
            elif key == keyboard.Key.f9:
                if state['phase'] == 'recording':
                    state['phase'] = 'finished'
                    done.set()
                    return False
                print('Not recording yet. Wait for visual synchronization.', flush=True)
            elif key == keyboard.Key.f10:
                state['cancel'] = True
                state['phase'] = 'finished'
                done.set()
                return False
            elif key == keyboard.Key.space and state['phase'] == 'recording' and not state['down']:
                state['down'] = True
                state['events'].append({'t_ns': max(0, time.perf_counter_ns() - state['start']), 'action': 'down'})

    def on_release(key):
        with lock:
            if key == keyboard.Key.space and state['phase'] == 'recording' and state['down']:
                state['down'] = False
                state['events'].append({'t_ns': max(0, time.perf_counter_ns() - state['start']), 'action': 'up'})

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    if state['cancel']:
        print('Cancelled; nothing saved.', flush=True)
    elif state['events']:
        if state['down']:
            state['events'].append({'t_ns': time.perf_counter_ns() - state['start'], 'action': 'up'})
        path = save_pattern(args.name, state['events'], sync='visual_scene_transition_v1')
        print(f'Saved {len(state["events"])} events to {path}', flush=True)
    else:
        print('No spacebar events recorded; nothing saved.', flush=True)

if __name__ == '__main__':
    main()
