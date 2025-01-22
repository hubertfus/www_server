import socket
import threading
import os
import requests
import configparser
import time

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('server', 'HOST', fallback='0.0.0.0')
PORT = config.getint('server', 'PORT', fallback=8080)
WORKING_DIR = config.get('server', 'WORKING_DIR', fallback='www')
ALLOWED_FILES = config.get('server', 'ALLOWED_FILES', fallback='html,css,js,txt,png,jpg').split(',')

os.makedirs(WORKING_DIR, exist_ok=True)


def log_request(client_address, request_line, status_code):
    with open("access_log.txt", "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {client_address} - {request_line} - {status_code}\n")


def log_error(error_message):
    with open("error_log.txt", "a") as error_file:
        error_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error: {error_message}\n")


def find_redirect(path):
    if os.path.isfile("redirect_log.txt"):
        with open("redirect_log.txt", "r") as log_file:
            redirects = log_file.readlines()

        for redirect in reversed(redirects):
            if redirect.startswith(path):
                return redirect.split(' -> ')[1].strip()

    return None


def send_http_response(client_socket, status_code, content_type, content, location=None):
    cat_image_url = f"http://http.cat/{status_code.split(' ')[0]}"
    image_response = requests.get(cat_image_url)

    response = f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}; charset=utf-8\r\n"

    if location:
        response += f"Location: {location}\r\n"

    response += "\r\n"

    client_socket.sendall(response.encode('utf-8'))

    if content_type.startswith('image'):
        client_socket.sendall(image_response.content)
    else:
        client_socket.sendall(content.encode('UTF-8'))


def handle_client(client_socket, client_address):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        request_line = request.splitlines()[0]
        print(f"{client_address} -> {request_line}")

        log_request(client_address, request_line, "200 OK")  # Log request

        parts = request_line.split()
        if len(parts) < 2:
            send_http_response(client_socket, "400 Bad Request", "text/html", "400 Bad Request")
            log_request(client_address, request_line, "400 Bad Request")
            return

        method = parts[0]
        path = parts[1].lstrip('/')

        if method != 'GET':
            send_http_response(client_socket, "405 Method Not Allowed", "text/html", "405 Method Not Allowed")
            log_request(client_address, request_line, "405 Method Not Allowed")
            return

        if not path:
            path = 'index.html'

        filepath = os.path.join(WORKING_DIR, path)
        file_extension = filepath.split('.')[-1]

        if is_access_denied(path) or file_extension not in ALLOWED_FILES:
            send_http_response(client_socket, "403 Forbidden", "image", "")
            log_request(client_address, request_line, "403 Forbidden")
        elif os.path.isfile(filepath) and file_extension in ALLOWED_FILES:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            send_http_response(client_socket, "200 OK", "text/html", content)
            log_request(client_address, request_line, "200 OK")
        else:
            if not os.path.isfile(filepath) and file_extension in ALLOWED_FILES:
                redirect_to = find_redirect(path)
                if redirect_to:
                    send_http_response(client_socket, "301 Moved Permanently", "text/html", "301 Moved Permanently",
                                       location=redirect_to)
                    log_request(client_address, request_line, "301 Moved Permanently")
                    return
            send_http_response(client_socket, "404 Not Found", "image", "")
            log_request(client_address, request_line, "404 Not Found")

    except Exception as e:
        log_error(f"Error handling request from {client_address}: {e}")
        send_http_response(client_socket, "500 Internal Server Error", "image", "")
        log_request(client_address, request_line, "500 Internal Server Error")
    finally:
        client_socket.close()


def is_access_denied(path):
    htaccess_path = '.htaccess'
    allowed_paths = []
    denied_paths = []

    if os.path.isfile(htaccess_path):
        with open(htaccess_path, 'r') as htaccess_file:
            rules = htaccess_file.readlines()
            for rule in rules:
                rule = rule.strip()
                if rule.startswith('Deny from '):
                    denied_paths.append(rule.replace('Deny from ', ''))
                elif rule.startswith('Allow from '):
                    allowed_paths.append(rule.replace('Allow from ', ''))

    for allowed_path in allowed_paths:
        if path.startswith(allowed_path):
            return False

    for denied_path in denied_paths:
        if path.startswith(denied_path):
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


