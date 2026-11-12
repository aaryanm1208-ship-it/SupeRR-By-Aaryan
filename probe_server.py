"""
Probe server script to verify live HTTP serving and responses.
Starts uvicorn in a separate thread with install_signal_handlers=False, executes HTTP requests, verifies responses, and exits.
"""

import time
import urllib.request
import urllib.error
import threading
import uvicorn
from src.api import app

class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.config = uvicorn.Config(
            app, 
            host="127.0.0.1", 
            port=8000, 
            log_level="warning"
        )
        self.server = uvicorn.Server(self.config)
        self.server.install_signal_handlers = lambda: None

    def run(self):
        try:
            self.server.run()
        except Exception as e:
            import traceback
            print("Server exception:", e)
            traceback.print_exc()

    def stop(self):
        self.server.should_exit = True

def main():
    print("Launching Uvicorn server in background thread on http://127.0.0.1:8000 ...")
    server_thread = ServerThread()
    server_thread.daemon = True
    server_thread.start()

    endpoints = [
        ("/", 200, "text/html"),
        ("/static/css/styles.css", 200, "text/css"),
        ("/static/js/app.js", 200, "javascript"),
        ("/api/summary", 200, "application/json"),
        ("/api/batters?limit=5", 200, "application/json"),
        ("/api/bowlers?limit=5", 200, "application/json"),
        ("/api/player/BATTER/7897", 200, "application/json"),
        ("/api/player/BOWLER/6450", 200, "application/json"),
        ("/api/research", 200, "application/json"),
        ("/api/figures", 200, "application/json"),
        ("/download/methodology_report.pdf", 200, "application/pdf")
    ]

    base_url = "http://127.0.0.1:8000"
    success = True

    # Polling wait for ready
    ready = False
    last_err = None
    for attempt in range(15):
        try:
            with urllib.request.urlopen(f"{base_url}/api/summary", timeout=1) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception as e:
            last_err = e
            time.sleep(0.3)

    if not ready:
        print(f"ERROR: Server failed to start within timeout. Last error: {last_err}")
        server_thread.stop()
        return False

    print("Server ready! Beginning live endpoint probes...")

    for path, expected_status, content_type_substr in endpoints:
        url = f"{base_url}{path}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                status = resp.status
                ct = resp.headers.get("content-type", "")
                body = resp.read()
                if status == expected_status and content_type_substr in ct and len(body) > 0:
                    print(f"  [PASS] {path} -> Status: {status}, Type: {ct}, Size: {len(body)} bytes")
                else:
                    print(f"  [FAIL] {path} -> Status: {status} (expected {expected_status}), Type: {ct} (expected {content_type_substr})")
                    success = False
        except urllib.error.HTTPError as e:
            print(f"  [FAIL] {path} -> HTTP Error: {e.code}")
            success = False
        except Exception as e:
            print(f"  [FAIL] {path} -> Error: {e}")
            success = False

    print("\nStopping server thread...")
    server_thread.stop()
    time.sleep(0.5)

    if success:
        print("\nALL ENDPOINT PROBES PASSED PERFECTLY (11/11)!")
    else:
        print("\nSOME PROBES FAILED!")

    return success

if __name__ == "__main__":
    ok = main()
    exit(0 if ok else 1)
