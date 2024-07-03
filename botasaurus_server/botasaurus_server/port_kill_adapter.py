import subprocess

import os

def catch_lsof_not_found_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print("""To use Botasaurus, it is recommended to install lsof by running the following command:
sudo apt-get update && sudo apt-get install -y lsof""")
        except subprocess.TimeoutExpired:
            print("""Timed Out clearing ports""")


    return wrapper

@catch_lsof_not_found_error
def kill_processes_using_port(port, method='tcp'):
    protocol = 'udp' if method == 'udp' else 'tcp'
    grep_keyword = 'UDP' if method == 'udp' else 'LISTEN'
    command = f"lsof -i {protocol}:{port} | grep {grep_keyword} | awk '{{print $2}}' | xargs kill -9"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def kill_process_on_port(port, method='tcp'):
    port = int(port)
    if not port:
        raise ValueError('Invalid port number provided')

    if method not in ['tcp', 'udp']:
        raise ValueError('Invalid method provided. Must be "tcp" or "udp".')

    targetport = f":{port}"
    if os.name == 'nt':
        # Windows
        result = subprocess.run(['netstat', '-nao'], capture_output=True, text=True)
        stdout = result.stdout
        # print(stdout)
        if not stdout:
            return result

        lines = stdout.split('\n')
        lines_with_local_port = [line for line in lines if targetport in line]
        # print(lines_with_local_port)
        pids = []
        import re
        for line in lines_with_local_port:
            match = re.search(r'(\d+)\s*\w*$', line)
            if match:
                x = match.group(1)
                if x and x != '0' and x not in pids:
                    pids.append(match.group(1))
        
        # pids = [for px in pids if px != 0 ]
        if pids:
            x = ' /PID '.join(pids)
            cmd = "TaskKill /F /PID " + x
            # print(cmd)
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

        # # print(lines_with_local_port, pids)
        # if pids:
        #     subprocess.run(command, shell=True, check=True)
            
        #     return sh(`TaskKill /F /PID ${pids.join(' /PID ')}`)

            # subprocess.run(['taskkill', '/F', '/PID', )], capture_output=True)

    else:
        # Unix-like systems
        result = get_lsof_text()
        # no lsof installed
        if not result:
            return None
        stdout = result.stdout

        if not stdout:
            return result

        lines = stdout.split('\n')
        exists_process = any(targetport in line for line in lines)

        if not exists_process:
            pass
            # raise ValueError(f'No process running on port {port}')
        else:
            kill_processes_using_port(port, method)

@catch_lsof_not_found_error
def get_lsof_text():
    return subprocess.run(['lsof', '-i', '-P'], capture_output=True, text=True, timeout=20)

# kill_process_on_port(8000)        
# def kill(port):
#     from javascript_fixes import require
#     killport = require("kill-port")
#     killport(port)

def killbackendport():
    # print("Killing port 8000...")
    kill_process_on_port(8000)

def killfrontendport():
    # print("Killing port 3000...")
    kill_process_on_port(3000)

def killfrontendandbackendports():
        # kill first else causes installation errors
        killbackendport()
        killfrontendport()   
# python -m botasaurus_server.port_kill_adapterpython -m botasaurus_server.port_kill_adapter
if __name__ == "__main__":
    kill_process_on_port(5000)