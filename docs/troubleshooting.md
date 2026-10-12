# ALIAS — Troubleshooting

---

## Port 8000 already in use

**Error**: `ERROR: [Errno 98] Address already in use` or `[WinError 10048]`

**Find the process**:

Windows:
```
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

macOS / Linux:
```bash
lsof -i :8000
kill -9 <pid>
```

**Alternative**: Change the port:
```
ALIAS_PORT=8001 uvicorn alias_core.api.main:app --reload
```
Then update the frontend proxy target in `frontend/vite.config.ts` to match.

---

## Port 5173 already in use (frontend)

Vite will try 5173, 5174, 5175, … automatically. Check the console output for the actual URL. If you need to fix the port:

```
cd frontend
npm run dev -- --port 5174
```

---

## Frontend can't reach backend (CORS / network error)

**Symptom**: Browser console shows `Network Error` or `CORS policy` error.

**Check 1** — is the backend running?
```bash
curl http://127.0.0.1:8000/api/health
```
If this fails, start the backend first.

**Check 2** — is the Vite proxy configured?  
Open `frontend/vite.config.ts`. It should proxy `/api` and `/lab` to `http://127.0.0.1:8000`. If you changed the backend port, update the proxy target.

**Check 3** — are both servers using the same host?  
The backend must be on `127.0.0.1:8000` for the default proxy to work. If you used `localhost` instead of `127.0.0.1`, they may not match (on some systems `localhost` resolves to `::1`).

---

## Python version too old

**Error**: `SyntaxError` or `requires Python >=3.12`

Check your version:
```bash
python --version
```

If it prints `3.11` or older, install Python 3.12:
- Windows: download from https://www.python.org/downloads/
- macOS: `brew install python@3.12`
- Ubuntu: `sudo apt install python3.12`

Ensure you're calling the right binary:
```bash
python3.12 scripts/setup.py
python3.12 scripts/dev.py
```

---

## pip install fails — `pydantic-settings` or `strawberry-graphql` not found

**Try upgrading pip first**:
```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If you see `No module named 'pydantic_settings'` at runtime, the editable install may not have resolved correctly:
```bash
pip install pydantic-settings>=2.3
```

---

## npm install fails

**Check Node version**:
```bash
node --version
# Must be 20.x or later
```

If you have an older Node:
- macOS: `brew install node@20`
- Windows: download from https://nodejs.org/
- Linux: `sudo apt install nodejs` (may need NodeSource for v20)

**Clear npm cache** if a partial install is corrupted:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Database locked

**Error**: `sqlite3.OperationalError: database is locked`

Another process is holding the SQLite WAL lock.

**Fix**: Stop all running ALIAS processes, then delete and reinitialize the database:

```bash
# Stop everything (Ctrl+C in the dev.py terminal)

# Delete the database
del alias.db           # Windows
rm alias.db            # macOS/Linux

# Reinitialize
python -c "import asyncio; from alias_core.database.init_db import init_db; asyncio.run(init_db())"
```

---

## `ModuleNotFoundError: No module named 'alias_core'`

The package is not installed in the current Python environment.

```bash
pip install -e .
```

If using a virtual environment, make sure it is activated before running anything:
```bash
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # macOS/Linux
```

---

## Experiments stuck in `running` status

**Cause**: The experiment engine timed out or a scenario's `run_experiment()` coroutine did not return.

**Check**: The 30-second timeout will transition the experiment to `timeout` automatically. If it does not:

1. Restart the backend (`Ctrl+C`, then `uvicorn alias_core.api.main:app --reload`)
2. The status will be corrected on the next startup via the database reconcile pass

---

## `TypeError: ... is not a coroutine function` at startup

**Cause**: A scenario module's `run_experiment` or `reset` method is synchronous (missing `async`).

**Fix**: Check the scenario's `__init__.py` and ensure the module-level `scenario` object satisfies the `ScenarioModule` protocol with async methods.

---

## Frontend build fails (`npm run build`)

**Check for TypeScript errors first**:
```bash
cd frontend
npx tsc --noEmit
```

Common causes:
- A component import path typo (case-sensitive on Linux)
- A missing type export from `src/services/api.ts`
- An incompatible `@types/react` version

---

## Can't find the `alias` CLI command after install

The CLI entry point `alias` is registered in `pyproject.toml`. If it is not on PATH:

```bash
# Run directly
python -m alias_core.cli.main

# Or check where pip installed it
python -m pip show -f alias-graphql-security | grep "alias"
```

On Windows, pip installs scripts to `%APPDATA%\Python\Python312\Scripts\` which may not be on PATH. Add it, or use `python -m alias_core.cli.main` directly.
