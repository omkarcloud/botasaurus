import time
import click
import os
import subprocess
import requests
from requests.exceptions import ReadTimeout
import traceback
import re

from .apache_utils import make_apache_content, read_conf, remove_apache_proxy_config
def find_ip(attempts=5, proxy=None) -> str:
    """Finds the public IP address of the current connection."""
    url = 'https://checkip.amazonaws.com/'
    proxies = None

    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        return response.text.strip()

    except ReadTimeout:
        if attempts > 1:
            print("ReadTimeout occurred. Retrying...")
            return find_ip(attempts - 1, proxy)
        else:
            print("Max attempts reached. Failed to get IP address.")
            return None

    except Exception as e:
        traceback.print_exc()
        return None

def is_running_on_gcp():
    try:
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance",
            headers={"Metadata-Flavor": "Google"},
        )
        return response.status_code == 200  # Success
    except requests.exceptions.RequestException:
        return False  # Assume not on GCP if request fails 


def get_gcp_ip():
    metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text

def get_vm_ip():
    if is_running_on_gcp():
        return get_gcp_ip()
    else:
        return find_ip()

def create_visit_ip_text(ip):
    return "Hurray! your scraper is up and running. Visit http://{}/ to use it.".format(ip)
def wait_till_up(ip):
    """
    Polls the given IP address every 10 seconds for 180 seconds to check if it's up.

    Args:
    ip (str): The IP address to check.

    Raises:
    Exception: If the IP is not up after 180 seconds.
    """
    timeout = 60  # Total time to wait in seconds
    interval = 1  # Time to wait between checks in seconds
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            # Attempt to connect to the IP address
            response = requests.get(f"http://{ip}/api", timeout=5)
            
            # If the response is successful, return without raising an exception
            if response.status_code == 200:
                return
        except requests.ConnectionError:
            # If a connection error occurs, just wait and try again
            pass

        time.sleep(interval)

    # If the function hasn't returned after the loop, raise an exception
    raise Exception(f"The VM at http://{ip}/ is not up after {timeout} seconds. Please check the logs using "
                    '"journalctl -u backend.service -b" or "journalctl -u frontend.service -b".')

def remove_empty_lines(text):
    """
    Removes all empty lines from the given string.
    
    Args:
    text (str): The input string from which empty lines should be removed.

    Returns:
    str: A new string with all empty lines removed.
    """
    return '\n'.join(line for line in text.split('\n') if line.strip())
def validateRepository(git_repo_url):
    """Checks if a GitHub repository exists. Raises an exception if not."""
    try:
        response = requests.head(git_repo_url, allow_redirects=True, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if "Not Found" in str(e):
            raise Exception(f"No repository found with URL: {git_repo_url}. Kindly check the URL.")
        raise Exception(f"Repository validation failed: {e}")

def extractRepositoryName(git_repo_url):
    """Extracts repository name from a GitHub URL"""
    parts = [x for x in git_repo_url.split('/') if x.strip()]
    repo_name = parts[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    return repo_name

def has_folder(folder_name):
    return os.path.isdir(folder_name)


def get_username():
    return os.getlogin()

def write_file( data, path,):
    with open(path, 'w', encoding="utf-8") as fp:
        fp.write(data)


def write_file_sudo( data, path,):
        echo_command = f"echo '{data}'"
        
        # The command to append the text to the Apache config file
        append_command = "sudo tee " + path
        
        # Complete command with a pipe from echo to tee
        command = f"{echo_command} | {append_command}"
        
        subprocess.run(command, shell=True, 
            check=True,
            stderr=subprocess.STDOUT,)

def create_clone_commands(git_repo_url, folder_name):
    clone_commands = "" if has_folder(folder_name) else f"git clone {git_repo_url} {folder_name}"
    return clone_commands.strip()

def safe_download(url: str, folder_name: str, print_ignore: bool):
    import zipfile
    import shutil
    from io import BytesIO
    # Download the file
    is_zip_file, response = is_zip(url)

    if is_zip_file:    
        try:
            os.makedirs(folder_name, exist_ok=True)
            
            # Read the zip file from the response content
            with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
                # Extract all contents to the folder
                zip_file.extractall(folder_name)

                # Get the list of files and directories in the extracted folder
                extracted_items = os.listdir(folder_name)
                
                # If there is exactly one folder inside, move its contents up
                if len(extracted_items) == 1 and os.path.isdir(os.path.join(folder_name, extracted_items[0])):
                    inner_folder = os.path.join(folder_name, extracted_items[0])
                    
                    # Move all files from the inner folder to the main folder
                    for item in os.listdir(inner_folder):
                        shutil.move(os.path.join(inner_folder, item), folder_name)
                    
                    # Remove the now-empty inner folder
                    os.rmdir(inner_folder)
                
                if print_ignore:
                    print("Kindly ignore the previous errors, as we have successfully installed the repository")
                    
        except Exception:
            # Clean up the folder if there was an error
            if os.path.exists(folder_name):
                shutil.rmtree(folder_name)
            raise
                         
    else:
        raise Exception("The URL does not point to a valid git repository or zip file.")

def is_zip(url):
    try:
        response = requests.get(url)
            # Check if the URL returns a valid zip file
        content_type = response.headers.get('Content-Type')
        meta_content_type = response.headers.get('x-amz-meta-content-type')
        return response.status_code == 200 and ('application/zip' in [content_type, meta_content_type]), response
    except:
      return False, None
    
def is_package_installed(package):
    import shutil
    return shutil.which(package) is not None

def is_google_chrome_installed():
    return is_package_installed("google-chrome")

def install_chrome(uname):
    if is_google_chrome_installed():
        return
    # lsof install as we need it.
    install_dependencies = f"""sudo apt install -y python3-pip
alias python=python3
echo "alias python=python3" >> /home/{uname}/.bashrc

sudo apt-get update
wget  https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y lsof xvfb
sudo apt --fix-broken install ./google-chrome-stable_current_amd64.deb -y
rm -rf google-chrome-stable_current_amd64.deb
"""    
    subprocess.run(remove_empty_lines(install_dependencies),     shell=True, 
            check=True,
            stderr=subprocess.STDOUT,)

def install_requirements(folder_name):
    def create_install_commands(folder_name):
        return  f"""
    cd {folder_name}
    python3 -m pip install -r requirements.txt && python3 run.py install"""


    install_commands = create_install_commands(folder_name)
    subprocess.run(remove_empty_lines(install_commands),     shell=True, 
            check=True,
            stderr=subprocess.STDOUT,)
    


def install_python_requirements_only(folder_name):
    def create_install_python_requirements_only(folder_name):
        return  f"""
    cd {folder_name}
    python3 -m pip install -r requirements.txt"""

    install_commands = create_install_python_requirements_only(folder_name)
    subprocess.run(remove_empty_lines(install_commands),     shell=True, 
            check=True,
            stderr=subprocess.STDOUT,)


def get_domain(url):
    from urllib.parse import urlparse

    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc
    return domain

def clone_repository(git_repo_url, folder_name):
    SUPPORTED_GIT_PROVIDERS = [
        "github.com",
        "gitlab.com",
        "bitbucket.org",
        "azure.com",
        "dev.azure.com",
        "gitea.com",
        "sourceforge.net",
        "git.sr.ht",  # Sourcehut
        "codeberg.org",
        "git.code.tencent.com",
        "pagure.io",
        "git.kernel.org",
        "git.eclipse.org",
        "salsa.debian.org",
        "invent.kde.org",
        "gitlab.gnome.org",
    ]

    domain = get_domain(git_repo_url)
    if domain not in SUPPORTED_GIT_PROVIDERS and is_zip(git_repo_url)[0]:
        return safe_download(git_repo_url, folder_name, False)
    clone_commands = create_clone_commands(git_repo_url, folder_name)
    if clone_commands:
        try:
          subprocess.run(remove_empty_lines(clone_commands), shell=True, check=True, stderr=subprocess.STDOUT,)
        except Exception as e:
          safe_download(git_repo_url, folder_name, True)

def create_backend(folder_name, uname):
    backend_sh = r"""#!/bin/bash
sudo pkill chrome
sudo pkill -f "python3 run.py backend"
VM=true /usr/bin/python3 run.py backend"""

    backend_service = f"""[Unit]
Description=Launch Backend
After=network.target
[Service]
Type=simple
User={uname}
WorkingDirectory=/home/{uname}/{folder_name}
ExecStart=/bin/bash /home/{uname}/{folder_name}/backend.sh
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target"""
    
    write_file(backend_sh, f"/home/{uname}/{folder_name}/backend.sh")
    write_file_sudo(backend_service, "/etc/systemd/system/backend.service")




def create_frontend(folder_name, uname):
    frontend_sh = r"""#!/bin/bash
sudo pkill -f "npm run start"
cd frontend
npm run start"""

    frontend_service = f"""[Unit]
Description=Launch Frontend
After=network.target
[Service]
Type=simple
User={uname}
WorkingDirectory=/home/{uname}/{folder_name}
ExecStart=/bin/bash /home/{uname}/{folder_name}/frontend.sh
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target"""

    write_file(frontend_sh, f"/home/{uname}/{folder_name}/frontend.sh")
    write_file_sudo(frontend_service, "/etc/systemd/system/frontend.service")

def setup_apache_load_balancer():
    apache_conf = r"""<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
    ProxyPass /api http://127.0.0.1:8000/api
    ProxyPassReverse /api http://127.0.0.1:8000/api
    ProxyPass / http://127.0.0.1:3000/
    ProxyPassReverse / http://127.0.0.1:3000/
</VirtualHost>"""
    
    
    write_file_sudo(apache_conf, "/etc/apache2/sites-available/000-default.conf")
    
def setup_systemctl(folder_name, uname):
    systemctl_commands=f"""
sudo chmod +x /home/{uname}/{folder_name}/backend.sh || true
sudo chmod +x /home/{uname}/{folder_name}/frontend.sh || true
sudo systemctl daemon-reload
sudo systemctl enable backend.service
sudo systemctl start backend.service
sudo systemctl enable frontend.service
sudo systemctl start frontend.service
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl restart apache2
"""
    subprocess.run(remove_empty_lines(systemctl_commands),     shell=True, 
            check=True,
            stderr=subprocess.STDOUT,)

def install_ui_scraper(git_repo_url, folder_name):
    uname = get_username()
    
    install_chrome(uname)

    clone_repository(git_repo_url, folder_name)

    install_requirements(folder_name)

    create_backend(folder_name, uname)
    create_frontend(folder_name, uname)


    setup_apache_load_balancer()
    
    setup_systemctl(folder_name, uname)
def create_main(folder_name, uname, max_retry):
    launch_file_path = f"/home/{uname}/{folder_name}/main.sh"
    
    service_name = f"{folder_name}.service"
    
    # Create launch script
    main = r"""#!/bin/bash
sudo pkill chrome
sudo pkill -f "python3 main.py"
VM=true /usr/bin/python3 main.py"""
    
    # Create service file with retry configuration
    service = create_service_content(folder_name, uname, max_retry, launch_file_path)
    
    # Write files
    write_file(main, f"/home/{uname}/{folder_name}/main.sh")
    write_file_sudo(service, "/etc/systemd/system/"+service_name)

    return launch_file_path, service_name

def create_service_content(folder_name, uname, max_retry, launch_file_path):
    # Add restart configuration based on max_retry
    if max_retry == 'unlimited':
        # will be retries unlimited number of time's
        return f"""[Unit]
Description=Run {folder_name}
After=network.target
StartLimitInterval=0
[Service]
Type=simple
User={uname}
WorkingDirectory=/home/{uname}/{folder_name}
ExecStart=/bin/bash {launch_file_path}
Restart=on-failure
RestartSec=10
[Install]
WantedBy=multi-user.target
"""


    elif max_retry is not None and int(max_retry) > 0:
        return f"""[Unit]
Description=Run {folder_name}
After=network.target
StartLimitInterval=3153600000
StartLimitBurst={max_retry}
[Service]
Type=simple
User={uname}
WorkingDirectory=/home/{uname}/{folder_name}
ExecStart=/bin/bash {launch_file_path}
Restart=on-failure
RestartSec=10
[Install]
WantedBy=multi-user.target
"""
        
    else:  # No retry or max_retry = 0
                return f"""[Unit]
Description=Run {folder_name}
After=network.target
[Service]
Type=simple
User={uname}
WorkingDirectory=/home/{uname}/{folder_name}
ExecStart=/bin/bash {launch_file_path}
Restart=no
[Install]
WantedBy=multi-user.target
"""

def setup_systemctl_for_data_scraper(launch_file_path, service_name):
    systemctl_commands=f"""
sudo chmod +x {launch_file_path} || true
sudo systemctl daemon-reload
sudo systemctl enable {service_name}
sudo systemctl start {service_name}
"""
    subprocess.run(remove_empty_lines(systemctl_commands),     shell=True, 
            check=True,
            stderr=subprocess.STDOUT)

def install_scraper(git_repo_url, folder_name, max_retry):
    uname = get_username()
    install_chrome(uname)
    clone_repository(git_repo_url, folder_name)

    install_python_requirements_only(folder_name)

    launch_file_path, service_name = create_main(folder_name, uname, max_retry)
    
    setup_systemctl_for_data_scraper(launch_file_path, service_name)

def install_ui_scraper_in_vm(git_repo_url, folder_name):
    validateRepository(git_repo_url)
    install_ui_scraper(git_repo_url, folder_name)
    click.echo("Successfully installed the Web Scraper.")
    click.echo("Now, Checking VM Status...")
    ip = get_vm_ip()
    wait_till_up(ip)
    click.echo(create_visit_ip_text(ip))

def install_scraper_in_vm(git_repo_url, folder_name, max_retry):
    validateRepository(git_repo_url)
    install_scraper(git_repo_url, folder_name, max_retry)
    click.echo("Successfully installed the Scraper.")
    # todo check status is it running or error?

def get_filename_from_url(url):
        from urllib.parse import urlparse
        return os.path.basename(urlparse(url).path.rstrip("/"))

def wget(debian_installer_url, temp_filename):
    subprocess.run(["wget", "-O", temp_filename, debian_installer_url], 
                      check=True, stderr=subprocess.STDOUT)

def get_package_name_from_debian_url(debian_installer_url):
    """
    Downloads a debian installer file temporarily and extracts the package name.
    
    Args:
        debian_installer_url (str): URL to the debian installer
        
    Returns:
        str: Package name extracted from the debian file
    """
    # Validate URL first
    validate_url(debian_installer_url)
    
    temp_filename = get_filename_from_url(debian_installer_url)
    delete_installer(temp_filename)
    try:
        # Download the file temporarily
        wget(debian_installer_url, temp_filename)
        
        # Extract package name
        package_name = subprocess.check_output(
            f"dpkg-deb -f ./{temp_filename} Package", 
            shell=True
        ).decode().strip()
        
        return package_name
        
    finally:
        delete_installer(temp_filename)


def get_api_base_path_from_content(content):
        # Find ExecStart line using regex
        exec_start_match = re.search(r'^ExecStart=(.*)$', content, re.MULTILINE)
        if not exec_start_match:
            return None
        
        exec_start_line = exec_start_match.group(1)
        
        # Extract --api-base-path value using regex
        api_base_path_match = re.search(r'--api-base-path\s+([^\s]+)', exec_start_line)
        if api_base_path_match:
            a = api_base_path_match.group(1)
            if a:
              a = a.strip()
            return a
        
        return "/" 

def get_api_base_path_from_service(service_file_path):

    """
    Reads a systemd service file and extracts the --api-base-path value from ExecStart.
    
    Args:
        service_file_path (str): Path to the systemd service file
        
    Returns:
        str or None: The api-base-path value if found, "/" if ExecStart exists but no --api-base-path, 
                     None if service doesn't exist, no ExecStart found, or error occurs
    """
    try:
        if not os.path.exists(service_file_path):
            return None
            
        with open(service_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return get_api_base_path_from_content(content)
    except Exception as e:
        # If any error occurs, return None
        return None

def kill_process(name):
    """
    Terminates all processes matching the given name.

    Args:
    name (str): The name of the process to terminate.

    Behavior:
    - Iterates through all processes to find those matching the given name.
    - Extracts the process ID (PID) and sends a SIGKILL signal to terminate it.
    - If an error occurs during termination, it prints an error message.

    Note:
    This function uses the `ps` command to find processes and may not work on non-Unix systems.
    """
    import os, signal
    try:
        # iterating through each instance of the process
        for line in os.popen(f'ps ax | grep "usr/bin/{name}" | grep -v grep'): 
            fields = line.split()
            
            # extracting Process ID from the output
            pid = fields[0] 
            
            # terminating process 
            os.kill(int(pid), signal.SIGKILL) 
    except Exception as e:
        print(f"Error Encountered while killing {name}", e)




def remove_service(service_file_path):
    """
    removes a systemd service.
    
    Args:
        service_name (str): Name of the service (with .service extension)
    """
    if os.path.exists(service_file_path):
            subprocess.run(
                ["sudo", "rm", service_file_path],
                check=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )

def stop_service(service_name):
    """
    Stops a systemd service.
    
    Args:
        service_name (str): Name of the service (with .service extension)
    """
    try:
        # Stop the service
        subprocess.run(
            ["sudo", "systemctl", "stop", service_name],
            check=False,  # Don't fail if service is already stopped
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )
        
        # Disable the service
        subprocess.run(
            ["sudo", "systemctl", "disable", service_name],
            check=False,  # Don't fail if service is already disabled
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )
        
        click.echo(f"Successfully removed service: {service_name}")
        
    except Exception as e:
        click.echo(f"Warning: Could not fully remove service {service_name}: {e}")

def stop_desktop_app_services(package_name):
    """
    Removes systemd services associated with a desktop app.
    
    Args:
        package_name (str): Name of the package
    """
    # Remove the package service
    package_service_name = f"{package_name}.service"
    stop_service(package_service_name)
    

def install_desktop_app_in_vm(
        debian_installer_url,
        port,
        skip_apache_request_routing,
        api_base_path,
        custom_args
    ):
    # Validate api_base_path
    api_base_path = clean_base_path(api_base_path)

    # Validate URL
    validate_url(debian_installer_url)

    # Install the app
    uname = get_username()
    install_chrome(uname)
    default_name = get_filename_from_url(debian_installer_url)

    

    # remove any interrupted downloads
    delete_installer(default_name)
    wget(debian_installer_url, default_name)
    package_name = subprocess.check_output(f"dpkg-deb -f ./{default_name} Package", shell=True).decode().strip()
    if custom_args and package_name == 'google-maps-extractor-api' and re.search(r'--auth-token\s+YOUR_AUTH_TOKEN\b', custom_args):
        raise Exception(
            "Authentication Error: YOUR_AUTH_TOKEN is a placeholder and must be replaced with your actual token.\n\n"
            "To get your authentication token:\n"
            "1. Log in to your omkar.cloud account\n"
            "2. Once logged in, view the README - the YOUR_AUTH_TOKEN placeholder will be automatically replaced with your actual authentication token\n"
            "3. Copy that actual token and use it in the --custom-args parameter\n\n"
            "Example:\n"
            'python3 -m bota install-desktop-app --debian-installer-url https://google-maps-extractor-with-api-omkar-cloud.s3.amazonaws.com/Google+Maps+Extractor+Api-amd64.deb --custom-args "--auth-token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6OTk5OSwidG9vbF9pZCI6MzMsImRlbW8iOnRydWV9.9wg6VYsPxGKsa6UNbxUPQEevnrckJd00UKWmYTNUy2I"'
        )
    is_already_installed = is_package_installed(package_name)
    if is_already_installed:
        install_command = f"sudo dpkg -i ./{default_name}"
    else:
        install_command = f"sudo apt --fix-broken install ./{default_name} -y"
    subprocess.run(install_command, shell=True, check=True, stderr=subprocess.STDOUT)
    delete_installer(default_name)
    
    # Create systemd service for Xvfb
    xvfb_service_name = f"xvfb.service"
    xvfb_service_content = f"""[Unit]
Description=Xvfb Service
After=network.target
[Service]
Type=simple
User={uname}
ExecStart=/usr/bin/Xvfb -ac :99 -screen 0 1280x1024x16
Restart=no
[Install]
WantedBy=multi-user.target"""
    write_file_sudo(xvfb_service_content, f"/etc/systemd/system/{xvfb_service_name}")

    # Create systemd service for the package
    package_service_name = f"{package_name}.service"
    package_service_content = f"""[Unit]
Description={package_name} Service
After=network.target {xvfb_service_name}
Requires={xvfb_service_name}
StartLimitInterval=0
[Service]
Type=simple
User={uname}
Environment="DISPLAY=:99"
ExecStart=/usr/bin/{package_name} --no-sandbox --only-start-api --port {port}{' --api-base-path ' + api_base_path if api_base_path else ''}{' ' +custom_args if custom_args else ''}
Restart=always
RestartSec=1
[Install]
WantedBy=multi-user.target"""
    write_file_sudo(package_service_content, f"/etc/systemd/system/{package_service_name}")

    if not skip_apache_request_routing:
        setup_apache_load_balancer_desktop_app(port, api_base_path)
    # Enable and start services
    systemctl_commands = f"""
sudo systemctl daemon-reload
sudo systemctl enable {xvfb_service_name}
sudo systemctl start {xvfb_service_name}
sudo systemctl enable {package_service_name}
sudo systemctl start {package_service_name}"""
    if not skip_apache_request_routing:
        systemctl_commands += """
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl restart apache2"""
    subprocess.run(remove_empty_lines(systemctl_commands), shell=True, check=True, stderr=subprocess.STDOUT)


    if is_already_installed:
        kill_process(package_name)

    click.echo("Successfully installed the Desktop App.")
    click.echo("Now, Checking API Status...")
    
    ip =  f"127.0.0.1:{port}" if skip_apache_request_routing else get_vm_ip()
    wait_till_desktop_api_up(ip, api_base_path, package_service_name)
    
    if skip_apache_request_routing:
        click.echo(f"Hurray! your desktop app is up and running at http://{ip}{api_base_path or '/'}")
    else:
        click.echo(f"Hurray! your desktop app is up and running. Visit http://{ip}{api_base_path or '/'} to see the API Docs.")

def clean_base_path(api_base_path):
    api_base_path = os.path.normpath(api_base_path) if api_base_path else ""
    
    if api_base_path == ".":
        api_base_path = ""
    elif api_base_path:
        if not api_base_path.startswith("/"):
            api_base_path = "/" + api_base_path
        if api_base_path.endswith("/"):
            api_base_path = api_base_path[:-1]
    return api_base_path

def delete_installer(default_name):
    if os.path.exists(default_name):
        os.remove(default_name)

def setup_apache_load_balancer_desktop_app(port, api_base_path):
    root_path = api_base_path or '/'
    api_target = f"http://127.0.0.1:{port}{root_path}"
    apache_conf = make_apache_content(read_conf(), root_path, api_target)
    write_file_sudo(apache_conf, "/etc/apache2/sites-available/000-default.conf")

def validate_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Retry with GET if HEAD fails (some servers don't support HEAD)
        try:
            response = requests.get(url, allow_redirects=True, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e2:
            raise Exception(f"The URL {url} does not point to a valid Debian installer.")

def api_config_disabled(service_name, seconds):
        """
        Checks if the API is disabled by looking for specific error messages in service logs.
        
        Args:
            service_name (str): Name of the systemd service
            
        Returns:
            bool: True if API is disabled, False otherwise
        """
        try:
            logs = subprocess.check_output(
                f"sudo journalctl -u {service_name} --since '{seconds} seconds ago'",
                shell=True, text=True
            )
            return "Kindly enable the API in" in logs
        except subprocess.CalledProcessError:
            return False
def generate_api_not_enabled_message():
    return f"""The API is not enabled in "api-config.ts".
To enable it:
1. Follow the instructions at:
   https://www.omkar.cloud/botasaurus/docs/botasaurus-desktop/botasaurus-desktop-api/adding-api#how-to-add-an-api-to-your-app
2. Once enabled, rebuild and reinstall the app in your VM."""
    
def wait_till_desktop_api_up(ip, api_base_path, package_service_name):
    """
    Polls the given IP address every second for 30 seconds to check if it's up.
    Checks for API configuration issues after 12 seconds.

    Args:
    ip (str): The IP address to check.
    api_base_path (str): The API path prefix.
    package_service_name (str): The name of the service package.

    Raises:
    Exception: If the IP is not up after 30 seconds.
    """
    timeout = 30  # Total time to wait in seconds
    interval = 1  # Time to wait between checks in seconds
    end_time = time.time() + timeout
    api_config_check_time = 10  # Check for API config issues after 10 seconds
    api_config_checked = False

    while time.time() < end_time:
        try:
            # Attempt to connect to the IP address
            if api_base_path:
                response = requests.get(f"http://{ip}{api_base_path}/ui/app-props", timeout=5)
            else:
                response = requests.get(f"http://{ip}/ui/app-props", timeout=5)
            
            # If the response is successful, return without raising an exception
            if response.status_code == 200:
                return
        except requests.ConnectionError:
            # If a connection error occurs, just wait and try again
            pass

        # Check for API configuration issues after 12 seconds
        elapsed_time = timeout - (end_time - time.time())
        if elapsed_time >= api_config_check_time and not api_config_checked:
            if api_config_disabled(package_service_name,  api_config_check_time + 5):
                raise Exception(generate_api_not_enabled_message())
            api_config_checked = True

        time.sleep(interval)
    
    # After timeout, check if it's an API configuration issue
    api_url = f"http://{ip}{api_base_path or '/'}"
    
    if api_config_disabled(package_service_name, timeout + 5):
        error_message = generate_api_not_enabled_message()
    else:
        error_message = f"""The Desktop API at {api_url} is not running.

To troubleshoot, view the logs by running:
journalctl -u {package_service_name} -b"""
    
    raise Exception(error_message)

def uninstall_desktop_app_in_vm(debian_installer_url, package_name, skip_apache_request_routing):
    """
    Uninstalls a desktop app from the VM.
    
    Args:
        debian_installer_url (str, optional): URL to the debian installer
        package_name (str, optional): Name of the package to uninstall
    """
    # Determine package name
    if debian_installer_url:
        click.echo("Extracting package name from Debian installer URL...")
        final_package_name = get_package_name_from_debian_url(debian_installer_url)
    else:
        final_package_name = package_name
    
    click.echo(f"Uninstalling package: {final_package_name}")
    
    # 1. Stop and remove systemd services
    click.echo("Stopping and removing systemd services...")
    stop_desktop_app_services(final_package_name)
    
    # 2. Kill any running processes
    click.echo("Stopping running processes...")
    kill_process(final_package_name)
    
    service_file_path = f"/etc/systemd/system/{final_package_name}.service"
    
    path = get_api_base_path_from_service(service_file_path)
    # 3. Uninstall the package
    click.echo("Removing package...")
    try:
        subprocess.check_output(
                ["sudo", "apt", "remove", "-y", "--purge", final_package_name],
                stderr=subprocess.STDOUT,
            )
        click.echo(f"Successfully removed package: {final_package_name}")
    except subprocess.CalledProcessError as e:
        if e.stdout:
            if "Unable to locate package" in str(e.stdout.decode('utf-8')):
                pass
            else:
                raise
        else: 
            raise
        if not skip_apache_request_routing and path:
            # 4. Clean up Apache proxy configuration
            click.echo("Cleaning up Apache proxy configuration...")
            
            cleaned_conf = remove_apache_proxy_config(path) # Also clean root path just in case
            write_file_sudo(cleaned_conf, "/etc/apache2/sites-available/000-default.conf")
                
            systemctl_reload_commands = """
            sudo systemctl daemon-reload
            sudo systemctl restart apache2
            """
        else:
            systemctl_reload_commands = """
            sudo systemctl daemon-reload
            """
        
        remove_service(service_file_path)
        subprocess.run(remove_empty_lines(systemctl_reload_commands), shell=True, check=True, stderr=subprocess.STDOUT)
        click.echo(f"Successfully uninstalled {final_package_name}.")

# python -m bota.vm 
if __name__ == "__main__":
#     print(get_api_base_path_from_content("""
# StartLimitInterval=0
# [Service]
# Type=simple
# Environment="DISPLAY=:99"
# ExecStart=/usr/bin/aa --no-sandbox --only-start-api --port --api-base-path
# RestartSec=1
# [Install]
# """))
    pass
    # launch_file_path, service_name = create_main("botasaurus-starter", "USERNAME", 'unlimited',)
    # setup_systemctl_for_data_scraper(launch_file_path, service_name)