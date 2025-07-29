import re


def read_file(path):
    with open(path, 'r', encoding="utf-8") as fp:
        content = fp.read()
        return content
        
def read_conf():
    return read_file("/etc/apache2/sites-available/000-default.conf")

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
    replace_conf = """\n\t# The ServerName directive sets the request scheme, hostname and port that\n\t# the server uses to identify itself. This is used when creating\n\t# redirection URLs. In the context of virtual hosts, the ServerName\n\t# specifies what hostname must appear in the request's Host: header to\n\t# match this virtual host. For the default virtual host (this file) this\n\t# value is not decisive as it is used as a last resort host regardless.\n\t# However, you must set it for any further virtual host explicitly.\n\t#ServerName www.example.com\n\n\tServerAdmin webmaster@localhost"""
    # Remove replace_conf content
    apache_conf = apache_conf.replace(replace_conf, "").replace(replace_conf.strip(), "")
      

    # Remove existing ProxyPass and ProxyPassReverse directives for the root_path
    apache_conf = clean_conf(apache_conf, root_path)

    # Add new ProxyPass and ProxyPassReverse directives based on the root_path
    if root_path == "/":
        return collapse_empty_lines(sub_at_end(apache_conf, root_path, api_target))
    else:
        # Add new directives right after the VirtualHost opening tag
        return collapse_empty_lines(sub_at_start(apache_conf, root_path, api_target))

def remove_apache_proxy_config(root_path):
    """
    Removes proxy configuration for a specific root path from Apache config.
    
    Args:
        root_path (str): The root path to remove from Apache config
    """
    apache_conf = read_conf()
    cleaned_conf = clean_conf(apache_conf, root_path)
    cleaned_conf = collapse_empty_lines(cleaned_conf)
    return cleaned_conf

# python -m src.bota.apache_utils
# if __name__ == "__main__":
#     apache_conf = read_conf().strip()
#     print(replace_conf in apache_conf)
#     # import json 
#     # print(json.dumps(apache_conf))
#     print("before",apache_conf)
    
#     print("after",apache_conf.replace(replace_conf, ""))