#!/usr/bin/env python3
"""ALIAS setup script — installs backend and frontend dependencies."""
import subprocess
import sys
import os


def run(cmd, cwd=None):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"ERROR: command failed (exit {result.returncode})")
        sys.exit(result.returncode)


root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(root, "frontend")

print("=== ALIAS Setup ===\n")

print("[1/3] Installing backend dependencies...")
run(f"{sys.executable} -m pip install -e .[dev]", cwd=root)

print("\n[2/3] Installing frontend dependencies...")
run("npm install", cwd=frontend_dir)

print("\n[3/3] Initializing database...")
run(
    f'{sys.executable} -c '
    '"import asyncio; from alias_core.database.init_db import init_db; asyncio.run(init_db())"',
    cwd=root,
)

print("\n✓ ALIAS setup complete!")
print()
print("  Start both servers: python scripts/dev.py")
print("  Backend only:       uvicorn alias_core.api.main:app --reload")
print("  Frontend only:      cd frontend && npm run dev")
print("  Run tests:          pytest backend/tests/ -v")
