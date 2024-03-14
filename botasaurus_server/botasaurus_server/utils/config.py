from os import environ

is_in_kubernetes = 'KUBERNETES_SERVICE_HOST' in environ
is_worker = is_in_kubernetes and environ.get('NODE_TYPE') == "WORKER"
is_master = is_in_kubernetes and environ.get('NODE_TYPE') == "MASTER"    