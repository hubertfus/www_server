import requests

def send_http_response(client_socket, status_code, content_type, content=b"", location=None):
    response = f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}"
    if content_type.startswith("text/"):
        response += "; charset=utf-8"
    response += "\r\n"
    if location:
        response += f"Location: {location}\r\n"
    response += "\r\n"
    client_socket.sendall(response.encode('utf-8'))
    if content_type.startswith('image/') and status_code != "200 OK" and not content:
        try:
            code = status_code.split(' ')[0]
            image_response = requests.get(f"http://http.cat/{code}")
            client_socket.sendall(image_response.content)
        except requests.RequestException:
            pass
    else:
        if isinstance(content, bytes):
            client_socket.sendall(content)
        else:
            client_socket.sendall(content.encode('utf-8'))
