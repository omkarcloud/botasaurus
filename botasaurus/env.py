from os import path, environ, name

IS_IN_KUBERNETES = 'KUBERNETES_SERVICE_HOST' in environ

def _is_docker():
    is_windows =  name == 'nt'
    # Early exit
    if is_windows:
        return False
    
    
    from sys import platform    
    is_mac =  platform == "darwin"
    # Early exit
    if is_mac:
        return False
    
    # Expensive Checks
    return path.exists('/.dockerenv') or path.isfile('/proc/self/cgroup') and 'docker' in open('/proc/self/cgroup').read() or IS_IN_KUBERNETES

IS_DOCKER = _is_docker()

IS_VM = environ.get('VM') == 'true'

IS_VM_OR_DOCKER = IS_DOCKER or IS_VM

IS_PRODUCTION = environ.get("ENV") == "production"
_os = None
def get_os():
    global _os

    if not _os:
        def getmyos():
            is_windows =  name == 'nt'
            # Early exit
            if is_windows:
                return 'windows'
            
            
            from sys import platform    
            is_mac =  platform == "darwin"
            # Early exit
            if is_mac:
                return 'mac'
            
            # Expensive Checks
            return 'linux'
        _os = getmyos()
    return _os
