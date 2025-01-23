import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('server', 'HOST', fallback='0.0.0.0')
PORT = config.getint('server', 'PORT', fallback=8080)
WORKING_DIR = config.get('server', 'WORKING_DIR', fallback='www')
ALLOWED_FILES = set(config.get('server', 'ALLOWED_FILES', fallback='html,css,js,txt,png,jpg').split(','))

os.makedirs(WORKING_DIR, exist_ok=True)

REDIRECTS = {}
HTACCESS_RULES = {'allow': [], 'deny': []}

def load_redirects():
    if os.path.isfile("redirects.txt"):
        with open("redirects.txt", "r") as file:
            for line in file:
                if "->" in line:
                    key, value = map(str.strip, line.split("->"))
                    REDIRECTS[key] = value


def load_htaccess():
    global HTACCESS_RULES
    if os.path.isfile('../../config/.htaccess'):
        with open('../../config/.htaccess', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('Deny from '):
                    HTACCESS_RULES['deny'].append(line.replace('Deny from ', ''))
                elif line.startswith('Allow from '):
                    HTACCESS_RULES['allow'].append(line.replace('Allow from ', ''))

def is_access_denied(path):
    for allowed_path in HTACCESS_RULES['allow']:
        if path.startswith(allowed_path):
            return False
    for denied_path in HTACCESS_RULES['deny']:
        if path.startswith(denied_path):
            return True
    return False
