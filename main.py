import socket
import threading
import os
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('server', 'HOST', fallback='127.0.0.1')
PORT = config.getint('server', 'PORT', fallback=8080)
WORKING_DIR = config.get('server', 'WORKING_DIR', fallback='www')
ALLOWED_FILES = config.get('server', 'ALLOWED_FILES', fallback='html,css,js').split(',')

os.makedirs(WORKING_DIR, exist_ok=True)

def send_http_response(client_socket, status_code, content_type, content):
    cat_image_url = f"http://http.cat/{status_code.split(' ')[0]}"
    image_response = requests.get(cat_image_url)
    
    response = f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}; charset=utf-8\r\n\r\n"
    client_socket.sendall(response.encode('utf-8'))

    client_socket.sendall(image_response.content if content_type.startswith('image') else content.encode('UTF-8'))


def handle_client(client_socket, client_address):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        request_line = request.splitlines()[0]
        print(f"{client_address} -> {request_line}")

        parts = request_line.split()
        if len(parts) < 2:
            client_socket.close()
            return

        method = parts[0] 
        path = parts[1].lstrip('/')

        if method != 'GET': 
            send_http_response(client_socket, "405 Method Not Allowed", "text/html", "405 Method Not Allowed")
            return
        
        if not path:
            path = 'index.html'

        filepath = os.path.join(WORKING_DIR, path)
        file_extension = filepath.split('.')[-1]

        if is_access_denied(path) or file_extension not in ALLOWED_FILES:
            send_http_response(client_socket, "403 Forbidden", "image/jpeg", "")
        elif os.path.isfile(filepath) and file_extension in ALLOWED_FILES:
            with open(filepath, 'r', encoding='utf-8') as file: 
                content = file.read()
            send_http_response(client_socket, "200 OK", "text/html", content)
        else:
            send_http_response(client_socket, "404 Not Found", "image/jpeg", "")

    except Exception as e:
        print(f"Error handling request from {client_address}: {e}")
    finally:
        client_socket.close()

def is_access_denied(path):
    htaccess_path = '.htaccess'
    if os.path.isfile(htaccess_path):
        with open(htaccess_path, 'r') as htaccess_file:
            rules = htaccess_file.readlines()
            for rule in rules:
                rule_path = rule.strip().replace('Deny from ', '')
                if path.startswith(rule_path):
                    return True
    return False

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server is running on http://{HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
