import os
from src.utils.logger import log_request, log_error
from src.utils.config_utils import WORKING_DIR, ALLOWED_FILES, REDIRECTS, is_access_denied
from src.utils.http_utils import send_http_response

def handle_client(client_socket, client_address):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        if not request:
            return

        request_line = request.splitlines()[0]
        print(f"{client_address} -> {request_line}")

        parts = request_line.split()
        if len(parts) < 2:
            send_http_response(client_socket, "400 Bad Request", "text/html", "400 Bad Request")
            log_request(client_address, request_line, "400 Bad Request")
            return

        method, path = parts[0], parts[1].lstrip('/')
        if method != 'GET':
            send_http_response(client_socket, "405 Method Not Allowed", "text/html", "405 Method Not Allowed")
            log_request(client_address, request_line, "405 Method Not Allowed")
            return

        if not path:
            path = 'index.html'

        filepath = os.path.join(WORKING_DIR, path)
        file_extension = filepath.split('.')[-1]

        if is_access_denied(path) or file_extension not in ALLOWED_FILES:
            send_http_response(client_socket, "403 Forbidden", "image")
            log_request(client_address, request_line, "403 Forbidden")
        elif os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            send_http_response(client_socket, "200 OK", f"text/{file_extension}", content)
            log_request(client_address, request_line, "200 OK")
        else:
            redirect_to = REDIRECTS.get(path)
            if redirect_to:
                send_http_response(client_socket, "301 Moved Permanently", "text/html", location=redirect_to)
                log_request(client_address, request_line, "301 Moved Permanently")
            else:
                send_http_response(client_socket, "404 Not Found", "image")
                log_request(client_address, request_line, "404 Not Found")
    except Exception as e:
        log_error(f"Error handling request from {client_address}: {e}")
        send_http_response(client_socket, "500 Internal Server Error", "image")
    finally:
        client_socket.close()
