#!/usr/bin/env python3
"""Start backend and frontend dev servers concurrently."""
import subprocess
import sys
import os
import time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(root, "frontend")

backend = subprocess.Popen(
    [
        sys.executable, "-m", "uvicorn",
        "alias_core.api.main:app",
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000",
    ],
    cwd=root,
)

frontend = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=frontend_dir,
    shell=(sys.platform == "win32"),
)

print("Backend:  http://127.0.0.1:8000")
print("Frontend: http://127.0.0.1:5173")
print("GraphiQL: http://127.0.0.1:8000/lab/<scenario>/vulnerable/graphql")
print("\nPress Ctrl+C to stop both servers.")

try:
    while True:
        if backend.poll() is not None:
            print("Backend exited unexpectedly.")
            frontend.terminate()
            sys.exit(1)
        if frontend.poll() is not None:
            print("Frontend exited unexpectedly.")
            backend.terminate()
            sys.exit(1)
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    backend.terminate()
    frontend.terminate()
    backend.wait()
    frontend.wait()
