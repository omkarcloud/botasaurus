import time
import click
import os
import subprocess
import requests
from requests.exceptions import ReadTimeout
import traceback

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
    timeout = 180  # Total time to wait in seconds
    interval = 10  # Time to wait between checks in seconds
    elapsed_time = 0

    while elapsed_time <= timeout:
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
        elapsed_time += interval

    # If the function hasn't returned after the loop, raise an exception
    raise Exception(f"The VM at http://{ip}/ is not up after {timeout} seconds. Please check the logs using "
                    '"journalctl -u launch-backend.service -b" or "journalctl -u launch-frontend.service -b".')

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
        response = requests.head(git_repo_url)
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
    return  f"""
{clone_commands}    
cd {folder_name}
python3 -m pip install -r requirements.txt && python3 run.py install"""
    
def installreqs(git_repo_url, folder_name):
    
    uname = get_username()

    launch_frontend_sh = r"""#!/bin/bash
sudo pkill -f "npm run start"
cd frontend
npm run start"""

    launch_backend_sh = r"""#!/bin/bash
sudo pkill chrome
sudo pkill -f "python3 run.py backend"
VM=true /usr/bin/python3 run.py backend"""

    launch_backend_service = f"""[Unit]
Description=Launch Backend
After=network.target

[Service]
Type=simple
User={uname}
WorkingDirectory=/home/{uname}/{folder_name}
ExecStart=/bin/bash /home/{uname}/{folder_name}/launch-backend.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"""
    
    launch_frontend_service = f"""[Unit]
Description=Launch Frontend
After=network.target

[Service]
Type=simple
User={uname}
WorkingDirectory=/home/{uname}/{folder_name}
ExecStart=/bin/bash /home/{uname}/{folder_name}/launch-frontend.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"""

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
    
    # lsof install as we need it.
    
    install_dependencies = f"""sudo apt install -y python3-pip
alias python=python3
echo "alias python=python3" >> /home/{uname}/.bashrc
 

sudo apt-get update
sudo apt-get install -y lsof wget gnupg2 apt-transport-https ca-certificates software-properties-common && sudo rm -rf /var/lib/apt/lists/*


wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - &&  echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee -a /etc/apt/sources.list.d/google-chrome.list



sudo apt-get install -y google-chrome-stable 
sudo apt-get install -y google-chrome-stable && sudo rm -rf /var/lib/apt/lists/*"""
    
    sysytemctl_commands=f"""
sudo chmod +x /home/{uname}/{folder_name}/launch-backend.sh || true
sudo chmod +x /home/{uname}/{folder_name}/launch-frontend.sh || true

sudo systemctl daemon-reload
sudo systemctl enable launch-backend.service
sudo systemctl start launch-backend.service

sudo systemctl daemon-reload
sudo systemctl enable launch-frontend.service
sudo systemctl start launch-frontend.service

sudo a2enmod proxy
sudo a2enmod proxy_http

sudo systemctl restart apache2
"""
    subprocess.run(remove_empty_lines(install_dependencies),     shell=True, 
            check=True,
            stderr=subprocess.STDOUT,)

    clone_commands = create_clone_commands(git_repo_url, folder_name)
    subprocess.run(remove_empty_lines(clone_commands),     shell=True, 
            check=True,
            stderr=subprocess.STDOUT,)
    
    write_file(launch_backend_sh, f"/home/{uname}/{folder_name}/launch-backend.sh")
    write_file(launch_frontend_sh, f"/home/{uname}/{folder_name}/launch-frontend.sh")

    write_file_sudo(launch_backend_service, "/etc/systemd/system/launch-backend.service")
    write_file_sudo(launch_frontend_service, "/etc/systemd/system/launch-frontend.service")

    write_file_sudo(apache_conf, "/etc/apache2/sites-available/000-default.conf")
    subprocess.run(remove_empty_lines(sysytemctl_commands),     shell=True, 
            check=True,
            stderr=subprocess.STDOUT,)



def install_scraper_in_vm(git_repo_url, folder_name):
    validateRepository(git_repo_url)
    installreqs(git_repo_url, folder_name)
    click.echo("Successfully installed the Scraper.")
    click.echo("Now, Checking VM Status...")
    ip = get_vm_ip()
    wait_till_up(ip)
    click.echo(create_visit_ip_text(ip))

if __name__ == "__main__":
    pass