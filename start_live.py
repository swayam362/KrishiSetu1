"""
KrushiSetu Live Public Launcher
Runs the Flask application and creates a public secure HTTPS tunnel via Cloudflare.
This allows anyone on any mobile phone, tablet, or PC to access the marketplace anywhere, anytime.
"""

import os
import sys

# Configure UTF-8 encoding safely for Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import subprocess
import re
import threading

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED_PATH = os.path.join(PROJECT_DIR, "cloudflared.exe")

def stream_output(process):
    url_found = None
    for line in iter(process.stderr.readline, ''):
        if not line:
            break
        line_str = line.strip()
        # Search for trycloudflare.com link
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line_str)
        if match and not url_found:
            url_found = match.group(0)
            print("\n" + "=" * 65)
            print(" [SUCCESS] KRUSHISETU IS NOW LIVE ONLINE!")
            print("=" * 65)
            print(f" >>> PUBLIC URL FOR ALL DEVICES:")
            print(f"     {url_found}")
            print("=" * 65)
            print(" * Open this link on ANY smartphone, tablet, or laptop.")
            print(" * Data uploads will sync live across all connected devices.")
            print(" * Keep this window running while using the public link.")
            print("=" * 65 + "\n")
            sys.stdout.flush()

def main():
    print("=" * 65)
    print("STARTING KRUSHISETU LIVE APPLICATION...")
    print("=" * 65)

    if not os.path.exists(CLOUDFLARED_PATH):
        print(f"Error: {CLOUDFLARED_PATH} not found.")
        return

    # 1. Start Flask app
    print("[1/2] Starting backend Flask server on port 5000...")
    backend_env = os.environ.copy()
    backend_proc = subprocess.Popen(
        [sys.executable, os.path.join(PROJECT_DIR, "backend", "app.py")],
        cwd=PROJECT_DIR,
        env=backend_env
    )

    time.sleep(2)

    # 2. Start Cloudflare Tunnel
    print("[2/2] Launching secure public tunnel for all devices...")
    tunnel_cmd = [CLOUDFLARED_PATH, "tunnel", "--url", "http://127.0.0.1:5000"]
    tunnel_proc = subprocess.Popen(
        tunnel_cmd,
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1
    )

    # Read tunnel stderr in a background thread to find the URL
    thread = threading.Thread(target=stream_output, args=(tunnel_proc,), daemon=True)
    thread.start()

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend stopped.")
                break
            if tunnel_proc.poll() is not None:
                print("Tunnel stopped.")
                break
    except KeyboardInterrupt:
        print("\nStopping KrushiSetu Live Server...")
    finally:
        try:
            backend_proc.terminate()
            tunnel_proc.terminate()
        except Exception:
            pass
        print("Server stopped cleanly.")

if __name__ == "__main__":
    main()
