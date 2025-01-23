import time
import threading
import os

LOG_LOCK = threading.Lock()

def log_message(file_name, message):
    log_dir = os.path.dirname(file_name)
    os.makedirs(log_dir, exist_ok=True)
    with LOG_LOCK:
        with open(file_name, "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def log_request(ip, request, status, file_path="logs/access_log.txt"):
    with LOG_LOCK:
        with open(file_path, "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {ip} - {request} - {status}\n")


def log_error(message, file_path="logs/error_log.txt"):
    with LOG_LOCK:
        with open(file_path, "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {message}\n")

