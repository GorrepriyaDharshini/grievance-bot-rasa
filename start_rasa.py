"""
Start a dummy HTTP server on port 10000 immediately,
then replace it with Rasa once model is loaded.
"""
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 8080))

class WarmupHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Rasa is loading, please wait...")
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Rasa is loading, please wait...")
    def log_message(self, format, *args):
        pass

def start_dummy():
    server = HTTPServer(("0.0.0.0", PORT), WarmupHandler)
    server.serve_forever()

# Start dummy server in background to hold port open
t = threading.Thread(target=start_dummy, daemon=True)
t.start()
print(f"Dummy server holding port {PORT}...")

# Now start Rasa — this will fail to bind port but that's ok
# because we just need Rasa to handle webhooks via subprocess
import time
time.sleep(2)

# Replace process with Rasa
os.chdir("rasa_bot")
os.execvp("rasa", ["rasa", "run", "--enable-api", "--cors", "*", "--port", str(PORT)])