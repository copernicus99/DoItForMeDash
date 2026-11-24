"""Local-only dashboard for launching and supervising the existing CLI scripts."""
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from common import ROOT, PATTERNS

def compiled_runtime():
    return bool(getattr(sys, "frozen", False) or "__compiled__" in globals() or getattr(sys, "_nuitka_binary_dir", None))

def worker_command(mode):
    """Launch worker through the packaged EXE, never an absent system Python."""
    if compiled_runtime():
        candidates = [ROOT / "DoItForMeDash.exe", Path(sys.executable), Path(sys.argv[0]).resolve()]
        executable = next((path for path in candidates if path.is_file() and path.suffix.lower() == ".exe"), None)
        if executable is None:
            raise RuntimeError("Packaged DoItForMeDash.exe not found. Reinstall the application.")
        return [str(executable), "--" + mode]
    return [sys.executable, "-u", str(ROOT / ("RECORD.py" if mode == "record" else "PLAYBACK.py"))]


HOST = '127.0.0.1'
PORT = int(os.environ.get('GD_PORT', '8765'))
LOCK = threading.Lock()
STATE = {'process': None, 'mode': None, 'started': None, 'lines': []}

def status():
    with LOCK:
        proc = STATE['process']
        active = proc is not None and proc.poll() is None
        return {'active': active, 'mode': STATE['mode'] if active else None,
                'pid': proc.pid if active else None,
                'logs': STATE['lines'][-60:],
                'patterns': sorted(p.name for p in PATTERNS.glob('*.json')) if PATTERNS.exists() else []}

def collect(proc):
    for line in proc.stdout:
        with LOCK:
            STATE['lines'].append(line.rstrip()[:300])
            STATE['lines'] = STATE['lines'][-120:]
    proc.wait()
    with LOCK:
        STATE['lines'].append('Process exited (code %s).' % proc.returncode)

def start(mode, data):
    if mode not in ('record', 'playback'):
        raise ValueError('Invalid mode')
    with LOCK:
        if STATE['process'] and STATE['process'].poll() is None:
            raise ValueError('A session is already running. Stop it first.')
        cmd = worker_command(mode)
        if mode == 'record':
            name = str(data.get('name', 'my_level')).strip()
            if not name or len(name) > 80 or not all(c.isalnum() or c in '-_' for c in name):
                raise ValueError('Name must contain only letters, digits, dash or underscore (max 80).')
            cmd += ['--name', name]
        else:
            name = str(data.get('pattern', ''))
            if not name.endswith('.json') or Path(name).name != name or name not in [p.name for p in PATTERNS.glob('*.json')]:
                raise ValueError('Select a valid saved pattern.')
            cmd += [name]
        cmd.append('--no-launch')
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        try:
            proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1, creationflags=flags)
        except OSError as exc:
            raise RuntimeError(f'Could not launch {mode} worker: {exc}. Command: {cmd[0]}') from exc
        STATE.update(process=proc, mode=mode, started=time.time(), lines=['Started ' + mode + ' session.'])
        threading.Thread(target=collect, args=(proc,), daemon=True).start()
    return status()

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, obj):
        payload = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)
    def do_GET(self):
        if urlparse(self.path).path == '/':
            payload = (ROOT / 'dashboard.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif urlparse(self.path).path == '/doitforme_dash_banner.png':
            image_path = ROOT / 'doitforme_dash_banner.png'
            if not image_path.is_file():
                return self.respond(404, {'error': 'Banner image not found'})
            payload = image_path.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(payload)
        elif urlparse(self.path).path == '/api/status':
            self.respond(200, status())
        else:
            self.respond(404, {'error': 'Not found'})
    def do_POST(self):
        route = urlparse(self.path).path
        if route not in ('/api/start', '/api/stop'):
            return self.respond(404, {'error': 'Not found'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length > 4096:
                return self.respond(413, {'error': 'Request too large'})
            data = json.loads(self.rfile.read(length) or b'{}')
            if route == '/api/start':
                result = start(data.get('mode'), data)
            else:
                with LOCK:
                    proc = STATE['process']
                    if proc and proc.poll() is None:
                        proc.terminate()
                        STATE['lines'].append('Stopped from dashboard. Unsaved recording may be lost; use F9 to save.')
                result = status()
            self.respond(200, result)
        except (ValueError, TypeError, RuntimeError, OSError) as exc:
            self.respond(400, {'error': str(exc)})
    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    print(f'Geometry Dash dashboard: http://{HOST}:{PORT}', flush=True)
    print('Keep this terminal open. Press Ctrl+C to stop the web server.', flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
