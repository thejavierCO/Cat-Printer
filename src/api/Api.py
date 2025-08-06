import os
import io
import sys
import json
import warnings
import webbrowser

from http.server import HTTPServer, BaseHTTPRequestHandler
# from printer import PrinterDriver, PrinterError, i18n, info
# from bleak.exc import BleakDBusError, BleakError
# from printer_lib.ipp import IPP

mime_type = {
    'html': 'text/html;charset=utf-8',
    'css': 'text/css;charset=utf-8',
    'js': 'text/javascript;charset=utf-8',
    'txt': 'text/plain;charset=utf-8',
    'json': 'application/json;charset=utf-8',
    'png': 'image/png',
    'svg': 'image/svg+xml;charset=utf-8',
    'wasm': 'application/wasm',
    'octet-stream': 'application/octet-stream'
}


def mime(url: str):
    return mime_type.get(url.rsplit('.', 1)[-1], mime_type['octet-stream'])


class ServerPathHandler():
    homedir = ""
    paths = {}

    def get(self, path, handler):
        self.paths[path] = [handler, 'GET']
        return self

    def post(self, path, handler):
        self.paths[path] = [handler, 'POST']
        return self

    def handle_request(self, request, method, path):
        if method == "GET" and self.homedir != "":
            file_path = os.path.abspath(self.homedir+path)
            if path.startswith("/"):
                index = os.path.abspath(file_path+"/index.html")
                if not os.path.exists(index):
                    request.send(404, "Page Not Found")
                    return
                with open(path, 'rb') as file:
                    while True:
                        chunk = file.read(self.buffer)
                        if not self.wfile.write(chunk):
                        break
        request.send(404, "Path Not Found")


class ServerHandler(BaseHTTPRequestHandler):
    server_path_handler = ServerPathHandler()

    def send(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"message": message}).encode('utf-8')
        self.wfile.write(response)
        return self

    def sendFile(self, status_code, file_name):
        self.send_response(status_code)
        self.send_header('Content-type', mime(file_name))
        self.end_headers()
        return lambda data: self.wfile.write(data)

    def do_GET(self):
        try:
            self.server_path_handler.handle_request(self, 'GET', self.path)
        except json.JSONDecodeError:
            self.send(400, "Invalid JSON")
        except Exception as e:
            self.send(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        try:
            self.server_path_handler.handle_request(self, 'POST', self.path)
        except json.JSONDecodeError:
            self.send(400, "Invalid JSON")
        except Exception as e:
            self.send(500, f"Internal Server Error: {str(e)}")

    def log_request(self, _code=200, _size=0):
        if '-D' in sys.argv or '--debug' in sys.argv:
            print(f'{self.command} {self.path} {_code} ')
        pass


class Server(HTTPServer):
    def finish_request(self, request, client_address):
        try:
            self.RequestHandlerClass(request, client_address, self)
        except Exception as e:
            print(f"Error handling request: {str(e)}")
            request.close()

    def useHome(self, directory):
        self.RequestHandlerClass.server_path_handler.homedir = directory

    def setGet(self, path, handler):
        self.RequestHandlerClass.server_path_handler.get(path, handler)
        return self

    def setPost(self, path, handler):
        self.RequestHandlerClass.server_path_handler.post(path, handler)
        return self

    def open_browser(self):
        webbrowser.open(
            f'http://{self.server_address[0]}:{self.server_address[1]}')
        return self

    def start(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped by user.")
        except Exception as e:
            print(f"Error starting server: {str(e)}")
        finally:
            self.server_close()
            print("Server closed.")
        return self


if __name__ == "__main__":
    try:
        httpd = Server(('localhost', 8000), ServerHandler)
        httpd.useHome("./www")
        httpd.start()
    except KeyboardInterrupt:
        print("Server stopped by user.")
    except Exception as e:
        print(f"Error starting server: {str(e)}")
