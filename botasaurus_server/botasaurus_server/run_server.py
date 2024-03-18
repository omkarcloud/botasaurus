import subprocess
import os
from threading import Thread
import sys
from .app import run_backend


def install():
    print("Installing frontend dependencies...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    subprocess.check_call("npm install && npm run build", shell=True, cwd=frontend_dir)


def start_frontend():
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    subprocess.check_call("npm run start", shell=True, cwd=frontend_dir)

def run_frontend():
    # Change to frontend directory
    try:
        start_frontend()
    except subprocess.CalledProcessError as e:
        # Resolve Errors, When user forgets to install frontend
        install()
        start_frontend()

def run_server():
    if len(sys.argv) == 1:
        # No arguments provided, run both backend and frontend
        Thread(target=run_backend, daemon=True).start()
        run_frontend()
    elif sys.argv[1] == "backend":
        # Argument "backend" provided, run only backend
        run_backend()
    elif sys.argv[1] == "lint":
        # Checks Import Only
        pass
    elif sys.argv[1] == "install":
        install()
    elif sys.argv[1] == "prod:backend":
        # Argument "prod:backend" provided, run only backend
        run_backend()
    elif sys.argv[1] == "prod":
        # Argument "prod" provided, run only backend
        run_backend()
    else:
        # Unknown argument provided, raise an exception with the argument
        raise Exception(f"Unknown argument: {sys.argv[1]}")


if __name__ == "__main__":
    run_server()
