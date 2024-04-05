from os import path, environ

is_in_kubernetes = 'KUBERNETES_SERVICE_HOST' in environ
is_docker = path.exists('/.dockerenv') or path.isfile('/proc/self/cgroup') and 'docker' in open('/proc/self/cgroup').read() or is_in_kubernetes
is_vm = environ.get('VM') == 'true'

is_worker = is_in_kubernetes and environ.get('NODE_TYPE') == "WORKER"
is_master = is_in_kubernetes and environ.get('NODE_TYPE') == "MASTER"
is_gitpod_environment = 'GITPOD_WORKSPACE_ID' in environ

is_vmish = is_docker or is_vm or is_gitpod_environment