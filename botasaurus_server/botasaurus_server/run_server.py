import subprocess
import os
from threading import Thread
import sys
from time import sleep
from .config import is_vmish
from .app import run_backend
from .port_kill_adapter import killfrontendandbackendports, killfrontendport, killbackendport

def install():
    print("Installing frontend dependencies...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    subprocess.check_call("npm install && npm run build", shell=True, cwd=frontend_dir)

def start_frontend(is_dev):
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    cmd = "npm run dev" if is_dev else "npm run start"
    result = subprocess.run(cmd, shell=True,
    stdout=subprocess.DEVNULL,  # Suppress the standard output
    stderr=subprocess.PIPE,  # Capture the standard error
    check=True,
    cwd=frontend_dir  # Return outputs as strings
)
    return result

def open_browser():
    # Wait for a few seconds before opening the browser
    sleep(3)
    import webbrowser
    webbrowser.open('http://localhost:3000/')

def run_frontend(is_dev):
    try:
        start_frontend(is_dev)
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode('utf-8'))
        # Resolve Errors, When user forgets to install frontend
        install()
        start_frontend(is_dev)


def run_server():
    if len(sys.argv) == 1:
        print("Starting frontend server at http://localhost:3000/")
        killfrontendandbackendports()
        # No arguments provided, run both backend and frontend
        Thread(target=run_backend, daemon=True).start()
        if not is_vmish:
            Thread(target=open_browser, daemon=True).start()
        run_frontend(False)
    elif sys.argv[1] == "backend":
        # Argument "backend" provided, run only backend
        killbackendport()
        run_backend()
    elif sys.argv[1] == "install":
        install()
    elif sys.argv[1] == "dev":
        print("Starting frontend server at http://localhost:3000/")
        killfrontendandbackendports()
        # No arguments provided, run both backend and frontend
        Thread(target=run_backend, daemon=True).start()
        if not is_vmish:
            Thread(target=open_browser, daemon=True).start()
        run_frontend(True)
    else:
        # Unknown argument provided, raise an exception with the argument
        raise Exception(f"Unknown argument: {sys.argv[1]}")


if __name__ == "__main__":
    run_server()
