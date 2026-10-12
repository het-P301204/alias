# ALIAS — Installation Guide

## Requirements

| Dependency | Minimum version | Check |
|------------|----------------|-------|
| Python | 3.12 | `python --version` |
| pip | 23+ | `pip --version` |
| Node.js | 20 | `node --version` |
| npm | 9+ | `npm --version` |
| Git | any | `git --version` |

---

## Quick install (all platforms)

```bash
git clone <repo-url>
cd alias
python scripts/setup.py
python scripts/dev.py
```

Open http://127.0.0.1:5173 in your browser.

---

## Windows (detailed)

### 1. Install Python 3.12

Download from https://www.python.org/downloads/ and run the installer.  
**Check "Add Python to PATH"** before clicking Install.

Verify:
```
python --version
# Python 3.12.x
```

### 2. Install Node.js 20

Download the LTS installer from https://nodejs.org/ and run it. npm is included.

Verify:
```
node --version
# v20.x.x
npm --version
# 10.x.x
```

### 3. Clone and set up

```
git clone <repo-url>
cd alias
python scripts\setup.py
```

### 4. Run

```
python scripts\dev.py
```

The script starts both servers. Open http://127.0.0.1:5173.

### Windows notes

- If `python` is not found, try `py -3.12` instead
- The `scripts\dev.py` launcher passes `shell=True` to `npm` on Windows automatically
- If port 8000 is busy: `netstat -ano | findstr :8000` to find the process, then `taskkill /PID <pid> /F`

---

## macOS (detailed)

### 1. Install Python 3.12

Using Homebrew (recommended):
```bash
brew install python@3.12
```

Or download from https://www.python.org/downloads/macos/

Verify:
```bash
python3 --version
```

### 2. Install Node.js 20

```bash
brew install node@20
```

Or download from https://nodejs.org/

### 3. Clone and set up

```bash
git clone <repo-url>
cd alias
python3 scripts/setup.py
```

### 4. Run

```bash
python3 scripts/dev.py
```

Open http://127.0.0.1:5173.

### macOS notes

- On Apple Silicon, all dependencies compile natively — no Rosetta needed
- If `python3` maps to the system Python (<3.12), use the Homebrew-installed path: `/opt/homebrew/bin/python3.12`
- If port 8000 is busy: `lsof -i :8000` then `kill -9 <pid>`

---

## Linux (Ubuntu/Debian)

### 1. Install Python 3.12

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

### 2. Install Node.js 20

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 3. Clone and set up

```bash
git clone <repo-url>
cd alias
python3.12 scripts/setup.py
```

### 4. Run

```bash
python3.12 scripts/dev.py
```

Open http://127.0.0.1:5173.

---

## Manual setup (without scripts/setup.py)

If you prefer full control:

```bash
# Backend
pip install -e ".[dev]"

# Frontend
cd frontend
npm install
cd ..

# Database
python -c "import asyncio; from alias_core.database.init_db import init_db; asyncio.run(init_db())"
```

Start backend:
```bash
uvicorn alias_core.api.main:app --reload --host 127.0.0.1 --port 8000
```

Start frontend (separate terminal):
```bash
cd frontend
npm run dev
```

---

## Virtual environment (recommended for Python isolation)

```bash
python -m venv .venv
# Activate:
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

pip install -e ".[dev]"
```

Run everything from the activated environment.

---

## Verifying the installation

```bash
# Backend health check
curl http://127.0.0.1:8000/api/health

# Should return:
# {"data":{"status":"ok","version":"...","scenarios_loaded":6,"db_ok":true,...},"error":null,"meta":{}}

# List scenarios
curl http://127.0.0.1:8000/api/scenarios
```
