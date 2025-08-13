import os
import io
import sys
import json
import warnings
import webbrowser
from router import Rutas

from http.server import HTTPServer, BaseHTTPRequestHandler

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


class DictAsObject(dict):
    " Let you use a dict like an object in JavaScript. "

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        self[key] = value


def mime(url: str):
    return mime_type.get(url.rsplit('.', 1)[-1], mime_type['octet-stream'])


class ServerHandler(BaseHTTPRequestHandler):
    Rute = Rutas()
    buffer = 4 * 1024 * 1024
    max_payload = buffer * 16

    def send(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"message": message}).encode('utf-8')
        self.wfile.write(response)
        return self

    def sendFileFormDirectory(self, status_code, file_path):
        if not os.path.isfile(file_path):
            return self.send(404, "Page Not Fount")
        self.send_response(status_code)
        self.send_header('Content-type', mime(file_path))
        self.end_headers()
        file_data = open(file_path, 'rb')
        while True:
            chunk = file_data.read(self.buffer)
            if not self.wfile.write(chunk):
                break
        file_data.close()
        return lambda data: print("load file exist")

    def sendFile(self, status_code, file_path):
        self.send_response(status_code)
        self.send_header('Content-type', mime(file_path))
        self.end_headers()
        return lambda data: self.wfile.write(data)

    def sendJson(self, status_code, body_json=None):
        'Called when an API call is being considered successful'
        self.send_response(status_code)
        self.send_header('Content-Type', mime('json'))
        self.end_headers()
        if body_json is None:
            self.wfile.write(b'{}')
        else:
            self.wfile.write(json.dumps(body_json).encode('utf-8'))

    def getBody(self):
        content_length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_length)
        return body

    def do_GET(self):
        try:
            @self.Rute.call(self.path)
            def fnc(rute):
                expected_method, handler = rute
                if "GET" == expected_method:
                    if callable(handler):
                        return handler(self)
                    if isinstance(handler, str):
                        return self.send(200, handler)
                else:
                    return self.send(405, f"Method {method} not allowed for {path}")
        except json.JSONDecodeError:
            self.send(400, "Invalid JSON")
        except Exception as e:
            self.send(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        try:
            @self.Rute.call(self.path)
            def fnc(rute):
                expected_method, handler = rute
                if "POST" == expected_method:
                    if callable(handler):
                        return handler(self)
                    if isinstance(handler, str):
                        return self.send(200, handler)
                else:
                    return self.send(405, f"Method {method} not allowed for {path}")
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

    def Get(self, path):
        def add(fns):
            @self.RequestHandlerClass.Rute.get(path, fns)
            def Alert():
                if '-D' in sys.argv or '--debug' in sys.argv:
                    print(f'add rute:{path}')
            return Alert
        return add

    def Post(self, path):
        def add(fns):
            @self.RequestHandlerClass.Rute.post(path, fns)
            def Alert():
                if '-D' in sys.argv or '--debug' in sys.argv:
                    print(f'add rute:{path}')
            return Alert
        return add

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
        Srv = Server(('localhost', 8000), ServerHandler)

        @Srv.Get("/")
        def Home(res):
            homedir = "./www"
            path, _, args = res.path.partition('?')
            file_path = os.path.abspath(homedir+path)
            if os.path.isfile(file_path):
                return res.sendFileFormDirectory(200, file_path)
            if path.startswith("/"):
                return res.sendFileFormDirectory(200, os.path.abspath(file_path+"/index.html"))
            return res.send(404, "Path Not Found")
        Srv.start()
    except KeyboardInterrupt:
        print("Server stopped by user.")
    except Exception as e:
        print(f"Error starting server: {str(e)}")
