import re

def clean_conf(apache_conf, root_path):
    apache_conf = re.sub(r'\n\s.*ProxyPass\s+' + re.escape(root_path) + r'\s+.*\n', '\n', apache_conf)
    apache_conf = re.sub(r'ProxyPass\s+' + re.escape(root_path) + r'\s+.*\n', '', apache_conf)
    apache_conf = re.sub(r'\n\s.*ProxyPassReverse\s+' + re.escape(root_path) + r'\s+.*\n', '\n', apache_conf)
    apache_conf = re.sub(r'ProxyPassReverse\s+' + re.escape(root_path) + r'\s+.*\n', '', apache_conf)
    # return apache_conf
    return re.sub(r'[ \t]+</VirtualHost>', '</VirtualHost>', apache_conf)

def collapse_empty_lines(conf: str) -> str:
    # Replace multiple consecutive newlines (with optional whitespace) with a single newline
    return re.sub(r'\n\s*\n+', '\n\n', conf.strip()) + '\n'

def sub_at_start(apache_conf, root_path, api_target):
    return re.sub(
            r'(<VirtualHost\b.*?>)', 
            f'\\1\n    ProxyPass {root_path} {api_target}\n    ProxyPassReverse {root_path} {api_target}', 
            apache_conf, 
            count=1
        )

def sub_at_end(apache_conf, root_path, api_target):
    return re.sub(r'</VirtualHost>', f'    ProxyPass {root_path} {api_target}\n    ProxyPassReverse {root_path} {api_target}\n</VirtualHost>', apache_conf)

def make_apache_content(apache_conf, root_path, api_target):
    # Remove existing ProxyPass and ProxyPassReverse directives for the root_path
    apache_conf = clean_conf(apache_conf, root_path)

    # Add new ProxyPass and ProxyPassReverse directives based on the root_path
    if root_path == "/":
        return collapse_empty_lines(sub_at_end(apache_conf, root_path, api_target))
    else:
        # Add new directives right after the VirtualHost opening tag
        return collapse_empty_lines(sub_at_start(apache_conf, root_path, api_target))
