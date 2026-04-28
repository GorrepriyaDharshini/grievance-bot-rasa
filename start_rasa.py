"""
Hold port open immediately for Render, then start Rasa on different port
and proxy requests to it.
"""

import os
import threading
import time
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error

RENDER_PORT = int(os.environ.get("PORT", 8080))
RASA_PORT = 19000  # internal port for Rasa

rasa_ready = False


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def _proxy(self):
        global rasa_ready
        if not rasa_ready:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Rasa is loading...")
            return
        target = f"http://127.0.0.1:{RASA_PORT}{self.path}"
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else None
            req = urllib.request.Request(
                target,
                data=body,
                headers={k: v for k, v in self.headers.items()},
                method=self.command,
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, format, *args):
        pass


def run_proxy():
    server = HTTPServer(("0.0.0.0", RENDER_PORT), ProxyHandler)
    print(f"Proxy holding port {RENDER_PORT}...")
    server.serve_forever()


def run_rasa():
    global rasa_ready
    time.sleep(3)
    os.chdir("rasa_bot")
    env = os.environ.copy()
    proc = subprocess.Popen(
        ["rasa", "run", "--enable-api", "--cors", "*", "--port", str(RASA_PORT)],
        env=env,
    )
    # Wait for Rasa to be ready
    while True:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{RASA_PORT}/", timeout=2)
            rasa_ready = True
            print("Rasa is ready!")
            break
        except:
            time.sleep(5)
    proc.wait()


# Start proxy immediately
proxy_thread = threading.Thread(target=run_proxy, daemon=True)
proxy_thread.start()

# Start Rasa in background
rasa_thread = threading.Thread(target=run_rasa)
rasa_thread.start()
rasa_thread.join()
