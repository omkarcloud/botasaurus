import time
import click
import os
import subprocess
import requests

def get_vm_ip():
    """
    Fetches the external IP address of the current GCP VM instance from the metadata server.

    Returns:
    str: The external IP address of the instance, or None if it cannot be determined.
    """
    metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"
    headers = {"Metadata-Flavor": "Google"}

    try:
        response = requests.get(metadata_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error querying metadata server: {e}")
        return None

def create_visit_ip_text(ip):
    return "The Scraper is running. Visit http://{}/ to use the Scraper.".format(ip)

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
            response = requests.get(f"http://{ip}/", timeout=5)
            
            # If the response is successful, return without raising an exception
            if response.status_code == 200:
                print(f"The VM at http://{ip}/ is up and running.")
                return
        except requests.ConnectionError:
            # If a connection error occurs, just wait and try again
            pass

        time.sleep(interval)
        elapsed_time += interval

    # If the function hasn't returned after the loop, raise an exception
    raise Exception(f"The VM at http://{ip}/ is not up after {timeout} seconds. Please check the logs using "
                    '"journalctl -xeu launch-backend.service" or "journalctl -xeu launch-frontend.service".')

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

def create_clone_commands(git_repo_url, folder_name):
    clone_commands = "" if has_folder(folder_name) else f"\ngit clone {git_repo_url} {folder_name}"
    return  f"""
cd {folder_name}
python3 -m pip install -r requirements.txt && python3 run.py install"""
    
def createInstallReqsCommand(git_repo_url, folder_name):

    uname = get_username()

    launch_frontend_sh = r"""#!/bin/bash
sudo pkill -f "npm run start"
cd frontend
npm run start"""

    launch_backend_sh = r"""#!/bin/bash
sudo pkill chrome
sudo pkill -f "python3 run.py backend"
/usr/bin/python3 run.py backend"""

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
    
    
    install_dependencies = f"""sudo apt install python3-pip
alias python=python3
echo "alias python=python3" >> /home/{uname}/.bashrc
 


sudo apt-get install -y wget gnupg2 apt-transport-https ca-certificates software-properties-common && sudo rm -rf /var/lib/apt/lists/*


wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - &&  echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee -a /etc/apt/sources.list.d/google-chrome.list


sudo apt-get update && sudo apt-get install -y google-chrome-stable && sudo rm -rf /var/lib/apt/lists/*"""
    
    sysytemctl_commands=f"""
sudo dd of=/home/{uname}/{folder_name}/launch-frontend.sh << EOF
{launch_frontend_sh}
EOF
sudo chmod +x launch-frontend.sh


sudo dd of=/home/{uname}/{folder_name}/launch-backend.sh << EOF
{launch_backend_sh}
EOF
sudo chmod +x launch-backend.sh


sudo a2enmod proxy
sudo a2enmod proxy_http

sudo dd of=/etc/apache2/sites-available/000-default.conf << EOF
{apache_conf}
EOF
sudo systemctl restart apache2


sudo dd of=/etc/systemd/system/launch-backend.service << EOF
{launch_backend_service}
EOF
sudo systemctl daemon-reload
sudo systemctl enable launch-backend.service
sudo systemctl start launch-backend.service

sudo dd of=/etc/systemd/system/launch-frontend.service << EOF
{launch_frontend_service}
EOF

sudo systemctl daemon-reload
sudo systemctl enable launch-frontend.service
sudo systemctl start launch-frontend.service"""
    clone_commands = create_clone_commands(git_repo_url, folder_name)

    final_commands = f"""{install_dependencies}\n{clone_commands}\n{sysytemctl_commands}"""
    return remove_empty_lines(final_commands)


def install_scraper_in_vm(git_repo_url):
    validateRepository(git_repo_url)
    folder_name = extractRepositoryName(git_repo_url)
    created = createInstallReqsCommand(git_repo_url, folder_name)
    subprocess.run(created, shell=True, check=True)
    click.echo("Scraper Installation successful!")
    click.echo("Now, Checking VM Status...")
    ip = get_vm_ip()
    wait_till_up(ip)
    click.echo(create_visit_ip_text(ip))

if __name__ == "__main__":
    
    print(createInstallReqsCommand("https://github.com/google-github-actions/g2-scraper", "g2-scraper"))
    
    
    