import socket
import threading
from src.handlers.client_handler import handle_client
from src.utils.config_utils import load_redirects, load_htaccess, HOST, PORT

def start_server():
    load_redirects()
    load_htaccess()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server is running on http://{HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True).start()

if __name__ == "__main__":
    start_server()
