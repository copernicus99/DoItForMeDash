"""Shared utilities for Geometry Dash input recording/replay."""
import json
import os
import sys
import time
import webbrowser
from pathlib import Path

APP_ID = 322170
ROOT = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) or '__compiled__' in globals() else Path(__file__).resolve().parent
PATTERNS = Path.home() / 'Documents' / 'DoItForMe Dash' / 'patterns'
PATTERNS.mkdir(parents=True, exist_ok=True)


def launch_game():
    url = f'steam://rungameid/{APP_ID}'
    if not webbrowser.open(url):
        print(f'Could not open {url}. Launch Geometry Dash through Steam manually.')
    print('Wait for Geometry Dash to load, open the level-selection screen with the clickable title/banner before F8.')


def load_pattern(path):
    with Path(path).open('r', encoding='utf-8') as f:
        data = json.load(f)
    if data.get('format_version') != 1 or not isinstance(data.get('events'), list):
        raise ValueError('Unsupported pattern format')
    prev = -1
    for event in data['events']:
        if event.get('action') not in ('down', 'up') or type(event.get('t_ns')) is not int or event['t_ns'] < prev:
            raise ValueError('Invalid or unordered events')
        prev = event['t_ns']
    return data


def save_pattern(name, events, sync=None):
    PATTERNS.mkdir(exist_ok=True)
    safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in name).strip('_') or 'recording'
    path = PATTERNS / (safe + '.json')
    if path.exists():
        path = PATTERNS / (safe + '_' + time.strftime('%Y%m%d_%H%M%S') + '.json')
    data = {'format_version': 1, 'game': 'Geometry Dash', 'steam_app_id': APP_ID,
            'clock': 'relative_monotonic_nanoseconds', 'sync_method': sync, 'events': events}
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return path


def sleep_until(target_ns, stop=None):
    while True:
        if stop is not None and stop.is_set():
            return False
        remaining = target_ns - time.perf_counter_ns()
        if remaining <= 0:
            return True
        if remaining > 3_000_000:
            time.sleep(min((remaining - 1_000_000) / 1e9, 0.02))
        elif remaining > 500_000:
            time.sleep(0.0002)
        # Short busy wait at the end; OS scheduling still limits precision.
