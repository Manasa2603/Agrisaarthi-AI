"""
AgriSaarthi AI - Unified Application Runner
================================================================================
Allows launching the complete AgriSaarthi AI platform (FastAPI Backend + Vite Frontend)
directly from VS Code using a single command:

    python app.py

Options:
    python app.py            # Starts both Backend and Frontend & opens browser
    python app.py --restart  # Cleanly restarts existing instances on ports 8000 & 5173
    python app.py --backend-only   # Starts only the FastAPI backend
    python app.py --frontend-only  # Starts only the Vite frontend
    python app.py --no-browser     # Starts without automatically launching the browser
================================================================================
"""
import sys
import os
import time
import socket
import shutil
import argparse
import subprocess
import webbrowser
import threading

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a network port is currently listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def get_pids_on_port(port: int) -> list:
    """Find process IDs listening on a specific port on Windows."""
    pids = []
    if os.name == "nt":
        try:
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode(errors="ignore")
            for line in output.strip().splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and "LISTENING" in line.upper():
                    try:
                        pid = int(parts[-1])
                        if pid > 0 and pid not in pids:
                            pids.append(pid)
                    except ValueError:
                        continue
        except Exception:
            pass
    return pids

def kill_pids(pids: list):
    """Terminate given process IDs and their children."""
    for pid in pids:
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
            else:
                os.kill(pid, 9)
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(
        description="AgriSaarthi AI Platform Unified Launcher",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--backend-only", action="store_true", help="Start only the FastAPI backend on port 8000")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the Vite frontend on port 5173")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    parser.add_argument("--keep-existing", action="store_true", help="Do not terminate existing processes on ports 8000 and 5173")
    parser.add_argument("--port-backend", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--port-frontend", type=int, default=5173, help="Frontend port (default: 5173)")
    args = parser.parse_args()

    print("\n" + "=" * 76)
    print("🌾  AgriSaarthi AI Platform – Unified Runner")
    print("=" * 76)

    # 1. Clean up any stale or orphaned processes on target ports unless explicitly kept
    if not args.keep_existing:
        backend_pids = get_pids_on_port(args.port_backend)
        frontend_pids = get_pids_on_port(args.port_frontend)
        if backend_pids or frontend_pids:
            print("🔄  Clearing stale background processes to prevent port conflicts...")
            if backend_pids:
                kill_pids(backend_pids)
            if frontend_pids:
                kill_pids(frontend_pids)
            time.sleep(1.0)

    # Handle frontend-only mode
    if args.frontend_only:
        print(f"\n🌾 Starting Frontend Dev Server on http://127.0.0.1:{args.port_frontend}...")
        npm_cmd = shutil.which("npm.cmd") or shutil.which("npm") or "npm"
        subprocess.run([npm_cmd, "run", "dev", "--", "--port", str(args.port_frontend)], cwd=FRONTEND_DIR, shell=(os.name == "nt"))
        return

    # Handle backend-only mode
    if args.backend_only:
        print(f"\n🌾 Starting Backend API Server on http://127.0.0.1:{args.port_backend}...")
        import uvicorn
        uvicorn.run("app.main:app", host="127.0.0.1", port=args.port_backend, reload=True, app_dir=BACKEND_DIR)
        return

    # Standard Mode: Launch Frontend (Vite) + Backend (FastAPI)
    npm_cmd = shutil.which("npm.cmd") or shutil.which("npm")
    frontend_process = None

    if npm_cmd:
        print(f"⏳  Starting Vite Frontend Dev Server on http://127.0.0.1:{args.port_frontend}...")
        try:
            frontend_process = subprocess.Popen(
                [npm_cmd, "run", "dev", "--", "--port", str(args.port_frontend), "--host", "127.0.0.1"],
                cwd=FRONTEND_DIR,
                shell=(os.name == "nt")
            )
        except Exception as e:
            print(f"⚠️  Could not start Vite dev server: {e}")
            print("ℹ️   FastAPI will serve the pre-compiled frontend directly on port 8000.")
    else:
        print("ℹ️   Node.js/npm not found. FastAPI will serve the pre-compiled frontend on port 8000.")

    # Auto-open browser in background thread
    def open_browser_when_ready():
        time.sleep(2.5)
        target_url = f"http://127.0.0.1:{args.port_frontend}" if frontend_process else f"http://127.0.0.1:{args.port_backend}"
        if not args.no_browser:
            try:
                webbrowser.open(target_url)
            except Exception:
                pass

    threading.Thread(target=open_browser_when_ready, daemon=True).start()

    print("\n" + "-" * 76)
    print(f"🌐  Frontend Web App:     http://127.0.0.1:{args.port_frontend}")
    print(f"📡  Backend & Static UI:  http://127.0.0.1:{args.port_backend}")
    print(f"📖  API Swagger Docs:     http://127.0.0.1:{args.port_backend}/docs")
    print("-" * 76)
    print("💡  Press Ctrl+C anytime in this terminal to stop both servers.\n")

    # Prevent c:\Agri\app.py from shadowing backend\app package
    if ROOT_DIR in sys.path:
        sys.path.remove(ROOT_DIR)
    if "" in sys.path:
        sys.path.remove("")
    if BACKEND_DIR not in sys.path:
        sys.path.insert(0, BACKEND_DIR)

    os.environ["PYTHONPATH"] = BACKEND_DIR + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.chdir(BACKEND_DIR)

    try:
        import uvicorn
        uvicorn.run("app.main:app", host="127.0.0.1", port=args.port_backend, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AgriSaarthi AI Platform...")
    finally:
        if frontend_process and frontend_process.poll() is None:
            print("🧹 Cleaning up frontend process...")
            kill_pids([frontend_process.pid])
        print("👋 All services stopped.")


if __name__ == "__main__":
    main()

