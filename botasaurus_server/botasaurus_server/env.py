from sys import platform
from os import path, environ, name

is_in_kubernetes = 'KUBERNETES_SERVICE_HOST' in environ

def _is_docker():

    is_mac =  platform == "darwin"
    # Easly exit
    if is_mac:
        return False
    is_windows =  name == 'nt'
    
    # Easly exit
    if is_windows:
        return False
    
    # Expensive Checks
    return path.exists('/.dockerenv') or path.isfile('/proc/self/cgroup') and 'docker' in open('/proc/self/cgroup').read() or is_in_kubernetes

is_docker = _is_docker()

is_vm = environ.get('VM') == 'true'
is_gitpod_environment = 'GITPOD_WORKSPACE_ID' in environ

is_vmish = is_docker or is_vm or is_gitpod_environment


is_worker = is_in_kubernetes and environ.get('NODE_TYPE') == "WORKER"
is_master = is_in_kubernetes and environ.get('NODE_TYPE') == "MASTER"
