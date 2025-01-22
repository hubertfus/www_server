## Documentation for the Web Server

This documentation describes the structure and functionality of the Python-based web server, which provides a simple HTTP server with support for file access, redirects, access control, and logging.

### Overview

The server listens for HTTP requests on a specified host and port. The server serves static files from a defined working directory, applies access control based on a `.htaccess` file, handles HTTP redirects, and logs requests and errors.

### File Structure

```
C:.
│   .gitignore
│   .htaccess
│   access_log.txt
│   config.ini
│   Dockerfile
│   main.py
│   redirect_log.txt
│
└───www
    │   final_page.html
    │   index.html
    │
    └───private
            publiced.html
```

### Files Description

- **main.py**: This is the main script that starts the server. It handles HTTP requests, manages access control, handles redirects, and logs requests and errors.
- **config.ini**: Configuration file containing server settings such as host, port, working directory, and allowed file types.
- **Dockerfile**: Contains instructions for building a Docker container to run the server.
- **.htaccess**: Contains access control rules for restricting or allowing access to specific files and directories.
- **access_log.txt**: Log file where all HTTP requests are recorded.
- **redirect_log.txt**: Log file for managing redirects. It keeps track of old URLs and their corresponding new URLs.
- **requirements.txt**: Lists the Python dependencies for the server.
- **www/**: The root directory where the server looks for files to serve.
- **private/**: A subdirectory inside the `www` folder with restricted access.
- **final_page.html**, **index.html**, **publiced.html**, **secret.html**, **old_page.html**, **new_page.html**: HTML files served by the server.

### Configuration (config.ini)

```ini
[server]
HOST = 0.0.0.0
PORT = 8080
WORKING_DIR = www
ALLOWED_FILES = html,css,js,txt
```

- **HOST**: The host address the server listens on (default is `0.0.0.0` which means it will accept connections on all interfaces).
- **PORT**: The port number the server listens on (default is `8080`).
- **WORKING_DIR**: The directory where the server looks for files to serve (default is `www`).
- **ALLOWED_FILES**: Comma-separated list of file extensions the server will serve (e.g., `html,css,js,txt`).

### Server Features

1. **Serving Files**: 
   - The server serves files from the `WORKING_DIR`. If the path is valid and corresponds to an allowed file type, the server will return the file content with an appropriate `200 OK` response.
   - The server handles the following file types: `html`, `css`, `js`, `txt`.

2. **Redirects**: 
   - If a requested file is not found, the server checks the `redirect_log.txt` file for a redirect rule and responds with a `301 Moved Permanently` status and the new location.
   - Redirect rules are stored in the `redirect_log.txt` file with the format `old_path -> new_path`.

3. **Access Control**:
   - The server respects the access rules defined in the `.htaccess` file. The rules specify which paths are allowed or denied access. 
   - For example:
     - `Deny from secret.html` denies access to the `secret.html` file.
     - `Allow from private/publiced.html` allows access to `publiced.html` in the `private` directory.
   - Access control is checked using the `is_access_denied()` function.

4. **Error Handling**: 
   - The server logs errors in `error_log.txt` when unexpected issues occur while processing requests.
   - Common errors include missing files (404 Not Found), access denial (403 Forbidden), or internal server errors (500 Internal Server Error).
   - In case of an error, the server sends an appropriate HTTP response, such as an image of a cat related to the error code (e.g., HTTP 404).

5. **Logging**: 
   - The server logs all incoming HTTP requests to `access_log.txt`.
   - Each log entry contains the timestamp, client IP, requested path, and response status.

6. **Method Restriction**: 
   - The server only supports the `GET` method. If a client attempts to use any other HTTP method (e.g., `POST`), the server will respond with a `405 Method Not Allowed` status.

### Key Functions

- **start_server()**: 
  - Starts the server and listens for incoming client connections.
  - For each connection, it spawns a new thread to handle the client request.

- **handle_client()**: 
  - Handles each client request by reading the HTTP request, checking for valid paths, applying access controls, serving the file, or redirecting if necessary.
  - Logs requests and errors.

- **send_http_response()**: 
  - Sends an HTTP response to the client with the appropriate status code, content type, and content. If the file is an image, the content is fetched from a remote cat image service based on the status code.

- **log_request()**: 
  - Logs each request to `access_log.txt` for tracking and auditing purposes.

- **log_error()**: 
  - Logs error messages to `error_log.txt` for troubleshooting and monitoring.

- **find_redirect()**: 
  - Checks if there is a redirect rule in `redirect_log.txt` and returns the new path if a redirect is found.

- **is_access_denied()**: 
  - Checks the `.htaccess` file for access control rules and determines if the requested path is allowed or denied.

### Docker Setup

To run the server inside a Docker container, use the provided `Dockerfile`:

1. **Build the Docker image**:
   ```bash
   docker build -t python-web-server .
   ```

2. **Run the Docker container**:
   ```bash
   docker run -p 8080:8080 python-web-server
   ```

This will start the server and make it accessible at `http://localhost:8080`.

### Example Workflow

1. A client sends a `GET` request to `http://localhost:8080/index.html`.
2. The server looks for `index.html` in the `www` directory.
3. If the file is found, it is sent with a `200 OK` response.
4. If the file is not found, the server checks the `redirect_log.txt` for any redirect rules.
5. If a redirect is found, the server responds with a `301 Moved Permanently` status and the new location.
6. If no redirect is found, the server responds with a `404 Not Found` error.

### Conclusion

This simple HTTP server provides basic static file serving, access control, redirect handling, and error logging. It can be easily extended and customized to suit more complex use cases, such as adding more file types, advanced routing, or additional features like caching or authentication.