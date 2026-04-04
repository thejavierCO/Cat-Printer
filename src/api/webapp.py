import os
import io
import sys
import json
import webbrowser
from router import Rutas, Plugin

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

    def setHeaders(self, status_code, mimetype: str):
        self.send_response(status_code)
        self.send_header('Content-type', mimetype)

        def action(fns):
            fns(
                lambda key, data: self.send_header(key, data),
                lambda: self.end_headers()
            )
        return action

    def defaultHeaders(self, status_code, mimetype: str):
        @self.setHeaders(status_code, mimetype)
        def action(add, end):
            end()

    def sendFileFormDirectory(self, status_code, file_path):
        if not os.path.isfile(file_path):
            return self.sendJson(404, {"status": "error", "msg": "not fount"})
        wfile = self.sendFile(status_code, file_path)
        file_data = open(file_path, 'rb')
        while True:
            chunk = file_data.read(self.buffer)
            if not wfile(chunk):
                break
        file_data.close()
        return lambda data: print("load file exist")

    def sendFile(self, status_code, file_path):
        self.defaultHeaders(status_code, mime(file_path))
        return lambda data: self.wfile.write(data)

    def sendJson(self, status_code, body_json=None):
        self.defaultHeaders(status_code, mime('json'))
        if body_json is None:
            self.wfile.write(b"{}")
        else:
            self.wfile.write(json.dumps(body_json).encode('utf-8'))

    def getBody(self):
        content_length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_length)
        return body

    def do_GET(self):
        try:
            self.Rute.call(self, "GET")
        except json.JSONDecodeError:
            self.sendJson(400, "Invalid JSON")
        except Exception as e:
            self.sendJson(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        try:
            self.Rute.call(self, "POST")
        except json.JSONDecodeError:
            self.sendJson(400, "Invalid JSON")
        except Exception as e:
            self.sendJson(500, f"Internal Server Error: {str(e)}")

    def log_request(self, _code=200, _size=0):
        self.Rute.Log(f'{self.command} {self.path} {_code} {_size}')
        pass


class Server(HTTPServer):
    def finish_request(self, request, client_address):
        try:
            self.RequestHandlerClass(request, client_address, self)
        except Exception as e:
            print(f"Error handling request: {str(e)}")
            request.close()

    def Use(self, *arg, **karg):
        return self.RequestHandlerClass.Rute.use(*arg, **karg)

    def Get(self, path):
        def add(fns):
            self.RequestHandlerClass.Rute.set(path, "GET", fns)
        return add

    def Post(self, path):
        def add(fns):
            self.RequestHandlerClass.Rute.set(path, "POST", fns)
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

        @Srv()
        class api():
            @use("GET")
            def api(self):
                return "home"

        Srv.start()
    except KeyboardInterrupt:
        print("Server stopped by user.")
    except Exception as e:
        print(f"Error starting server: {str(e)}")
