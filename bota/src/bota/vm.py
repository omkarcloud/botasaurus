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
sudo apt-get install -y lsof wget gnupg2 apt-transport-https ca-certificates software-properties-common adwaita-icon-theme alsa-topology-conf alsa-ucm-conf at-spi2-core dbus-user-session dconf-gsettings-backend dconf-service fontconfig fonts-liberation glib-networking glib-networking-common glib-networking-services gsettings-desktop-schemas gtk-update-icon-cache hicolor-icon-theme libasound2 libasound2-data libatk-bridge2.0-0 libatk1.0-0 libatk1.0-data libatspi2.0-0 libauthen-sasl-perl libavahi-client3 libavahi-common-data libavahi-common3 libcairo-gobject2 libcairo2 libclone-perl libcolord2 libcups2 libdata-dump-perl libdatrie1 libdconf1 libdrm-amdgpu1 libdrm-common libdrm-intel1 libdrm-nouveau2 libdrm-radeon1 libdrm2 libencode-locale-perl libepoxy0 libfile-basedir-perl libfile-desktopentry-perl libfile-listing-perl libfile-mimeinfo-perl libfont-afm-perl libfontenc1 libgbm1 libgdk-pixbuf-2.0-0 libgdk-pixbuf2.0-bin libgdk-pixbuf2.0-common libgl1 libgl1-mesa-dri libglapi-mesa libglvnd0 libglx-mesa0 libglx0 libgraphite2-3 libgtk-3-0 libgtk-3-bin libgtk-3-common libharfbuzz0b libhtml-form-perl libhtml-format-perl libhtml-parser-perl libhtml-tagset-perl libhtml-tree-perl libhttp-cookies-perl libhttp-daemon-perl libhttp-date-perl libhttp-message-perl libhttp-negotiate-perl libice6 libio-html-perl libio-socket-ssl-perl libio-stringy-perl libipc-system-simple-perl libjson-glib-1.0-0 libjson-glib-1.0-common liblcms2-2 libllvm11 liblwp-mediatypes-perl liblwp-protocol-https-perl libmailtools-perl libnet-dbus-perl libnet-http-perl libnet-smtp-ssl-perl libnet-ssleay-perl libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpciaccess0 libpixman-1-0 libproxy1v5 librest-0.7-0 librsvg2-2 librsvg2-common libsensors-config libsensors5 libsm6 libsoup-gnome2.4-1 libsoup2.4-1 libtext-iconv-perl libthai-data libthai0 libtie-ixhash-perl libtimedate-perl libtry-tiny-perl libu2f-udev liburi-perl libvte-2.91-0 libvte-2.91-common libvulkan1 libwayland-client0 libwayland-cursor0 libwayland-egl1 libwayland-server0 libwww-perl libwww-robotrules-perl libx11-protocol-perl libx11-xcb1 libxaw7 libxcb-dri2-0 libxcb-dri3-0 libxcb-glx0 libxcb-present0 libxcb-randr0 libxcb-render0 libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxft2 libxi6 libxinerama1 libxkbcommon0 libxkbfile1 libxml-parser-perl libxml-twig-perl libxml-xpathengine-perl libxmu6 libxmuu1 libxrandr2 libxrender1 libxshmfence1 libxt6 libxtst6 libxv1 libxxf86dga1 libxxf86vm1 libz3-4 mesa-vulkan-drivers perl-openssl-defaults shared-mime-info termit x11-common x11-utils xdg-utils xvfb
sudo dpkg -i google-chrome-stable_current_amd64.deb
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

def install_desktop_app_in_vm(
        debian_installer_url,
        port,
        skip_apache_request_routing,
        api_base_path
    ):
    # Validate api_base_path
    api_base_path = clean_base_path(api_base_path)

    # Validate URL
    validate_url(debian_installer_url)

    # Install the app
    uname = get_username()
    install_chrome(uname)
    default_name = get_filename_from_url(debian_installer_url)

    delete_installer(default_name)
    

    
    subprocess.run(["wget", debian_installer_url], check=True, stderr=subprocess.STDOUT)
    package_name = subprocess.check_output(f"dpkg-deb -f ./{default_name} Package", shell=True).decode().strip()
    if is_package_installed(package_name):
        install_command = f"sudo dpkg -i ./{default_name}"
    else:
        install_command = f"sudo apt --fix-broken install ./{default_name} -y"
    subprocess.run(install_command, shell=True, check=True, stderr=subprocess.STDOUT)
    

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
ExecStart=/usr/bin/{package_name} --only-start-api --port {port} {'--api-base-path ' + api_base_path if api_base_path else ''}
Restart=on-failure
RestartSec=10
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

    click.echo("Successfully installed the Desktop App.")
    click.echo("Now, Checking API Status...")
    ip = get_vm_ip()
    wait_till_desktop_api_up(ip, api_base_path)
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
    apache_conf = f"""<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html
    ErrorLog ${{APACHE_LOG_DIR}}/error.log
    CustomLog ${{APACHE_LOG_DIR}}/access.log combined
    ProxyPass {api_base_path or '/'} http://127.0.0.1:{port}{api_base_path or '/'}
    ProxyPassReverse {api_base_path or '/'} http://127.0.0.1:{port}{api_base_path or '/'}
</VirtualHost>"""
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

def wait_till_desktop_api_up(ip, api_base_path):
    """
    Polls the given IP address every 10 seconds for 180 seconds to check if it's up.

    Args:
    ip (str): The IP address to check.
    api_base_path (str): The API path prefix.

    Raises:
    Exception: If the IP is not up after 180 seconds.
    """
    timeout = 60  # Total time to wait in seconds
    interval = 1  # Time to wait between checks in seconds
    end_time = time.time() + timeout

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

        time.sleep(interval)
    # If the function hasn't returned after the loop, raise an exception
    raise Exception(
        f'The Desktop Api at http://{ip}{api_base_path or "/"} is not running. You have surely forgotten to enable the Api in "api-config.ts".'
    )

# python -m bota.vm 
if __name__ == "__main__":
    pass
    # launch_file_path, service_name = create_main("botasaurus-starter", "USERNAME", 'unlimited',)
    # setup_systemctl_for_data_scraper(launch_file_path, service_name)