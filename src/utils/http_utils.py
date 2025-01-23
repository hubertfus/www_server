import requests

def send_http_response(client_socket, status_code, content_type, content="", location=None):
    response = f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}; charset=utf-8\r\n"
    if location:
        response += f"Location: {location}\r\n"
    response += "\r\n"
    client_socket.sendall(response.encode('utf-8'))
    if content_type.startswith('image'):
        try:
            image_response = requests.get(f"http://http.cat/{status_code.split(' ')[0]}")
            client_socket.sendall(image_response.content)
        except requests.RequestException:
            pass
    else:
        client_socket.sendall(content.encode('utf-8'))
