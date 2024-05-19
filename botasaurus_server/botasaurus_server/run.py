import subprocess
import os
from threading import Thread
import sys
import webbrowser
import urllib.request
from .env import is_vmish
from .app import run_backend
from .port_kill_adapter import killfrontendandbackendports, killbackendport
from .server import Server
from time import sleep
def show_help():
    print("""
Botasaurus Server CLI

Options:
  --help  Show this message and exit.

Commands:
  (no arguments)    Runs both the backend and frontend services.
  backend           Runs only the backend api service.
  install           Installs the frontend service.
  dev               Run the backend normally, and the frontend in development mode with hot reloading, allowing you to see UI changes immediately as you update the Next.js frontend code in the "frontend/src" folder.  This functionality is mostly not needed and is only useful when you need to change frontend ui's appearance. 
""")

def is_server_ready(url):
  """Checks if the server at the given URL is reachable using a HEAD request.

  Args:
      url (str): The URL to check.

  Returns:
      bool: True if the server responds with a successful status code (2xx), False otherwise.
  """
  try:
    req = urllib.request.Request(url, method='HEAD')

    with urllib.request.urlopen(req, timeout=4) as response:
      return response.getcode() > 199 and response.getcode() < 300  # Check using > and <
  except:
    return False


def open_browser():
  sleep(1)
  while not is_server_ready('http://localhost:3000/'):
    sleep(1)    
    # Wait for a few seconds before opening the browser
  webbrowser.open('http://localhost:3000/')

def open_browser_in_thread():
    if not is_vmish:
        Thread(target=open_browser, daemon=True).start()

def install():
    print("Installing frontend...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    subprocess.check_call("npm install && npm run build", shell=True, cwd=frontend_dir)

def print_frontend_run_message():
    print("Starting frontend server at http://localhost:3000/")

def start_frontend(is_dev):
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    cmd = "npm run dev" if is_dev else "npm run start"
    result = subprocess.run(cmd, shell=True,
    stdout = None if is_dev else subprocess.DEVNULL,  # Suppress the standard output
    stderr= None if is_dev else subprocess.PIPE,  # Capture the standard error
    check=True,
    cwd=frontend_dir  # Return outputs as strings
)
    return result

def run_frontend(is_dev):
    try:
        start_frontend(is_dev)
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(e.stderr.decode('utf-8'))
        # Resolve Errors, When user forgets to install frontend
        install()
        print_frontend_run_message()
        open_browser_in_thread()
        start_frontend(is_dev)

def run_backend_in_thread():
    sleep(1)
    Thread(target=run_backend, daemon=True).start()

def run():
    if "--help" in sys.argv:
            show_help()
    else:
        if not Server.get_scrapers_names():
            raise RuntimeError("No scrapers found. Please add a scraper using Server.add_scraper.")
        
        if len(sys.argv) == 1:
            print_frontend_run_message()
            killfrontendandbackendports()
            # No arguments provided, run both backend and frontend
            run_backend_in_thread()
            open_browser_in_thread()
            run_frontend(False)
        elif sys.argv[1] == "install":
            install()
        elif sys.argv[1] == "backend":
            # Argument "backend" provided, run only backend
            killbackendport()
            run_backend()
        elif sys.argv[1] == "dev":
            print_frontend_run_message()
            killfrontendandbackendports()
            # No arguments provided, run both backend and frontend
            run_backend_in_thread()
            open_browser_in_thread()
            run_frontend(True)
        else:
            print(f"Error: No such command: {sys.argv[1]}")
            print("Try '--help' for help.")
            sys.exit(1) 