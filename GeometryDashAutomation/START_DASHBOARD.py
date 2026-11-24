"""Windows desktop entry point: starts local backend and opens default browser."""
import socket
import sys
import threading
import webbrowser
from web_server import HOST, PORT, Handler, ThreadingHTTPServer
import RECORD
import PLAYBACK

URL = f"http://{HOST}:{PORT}"

def open_dashboard():
    webbrowser.open(URL)

def main():
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as exc:
        # A second launch should open the existing dashboard, not create a second server.
        try:
            with socket.create_connection((HOST, PORT), timeout=0.5):
                open_dashboard()
                return
        except OSError:
            raise RuntimeError(f"Could not start local dashboard on {HOST}:{PORT}: {exc}") from exc
    print(f"DoItForMe Dash running at {URL}", flush=True)
    threading.Timer(0.7, open_dashboard).start()
    try:
        server.serve_forever()
    finally:
        server.server_close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--record', '--playback'):
        mode = sys.argv.pop(1)
        if mode == '--record':
            from RECORD import main as run
        else:
            from PLAYBACK import main as run
        run()
    else:
        main()
