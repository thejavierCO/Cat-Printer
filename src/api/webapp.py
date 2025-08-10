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


# class ServerPathHandler():
#     homedir = ""
#     buffer = 4 * 1024 * 1024
#     max_payload = buffer * 16

#     def handle_request(self, request, method, path):
#         # path, _, _args = path.partition('?')
#         # if self.homedir != "":
#         #     file_path = os.path.abspath(self.homedir+path)
#         #     if os.path.isfile(file_path):
#         #         return request.sendFileFormDirectory(200, file_path)
#         # if path in self.paths:
#         #     handler, expected_method = self.paths[path]
#         #     if method == expected_method:
#         #         if callable(handler):
#         #             return handler(request)
#         #         if isinstance(handler, str):
#         #             return request.send(200, handler)
#         #     else:
#         #         return request.send(405, f"Method {method} not allowed for {path}")
#         # if path.startswith("/"):
#         #     return request.sendFileFormDirectory(
#         #         200, os.path.abspath(file_path+"/index.html"))
#         return request.send(404, "Path Not Found")


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

    def do_GET(self):
        try:
            @self.Rute.call(self.path)
            def fnc(rute):
                print(rute)
                request.send(200, "test")
                # expected_method, handler = rute
                # if "GET" == expected_method:
                #     if callable(handler):
                #         return handler(request)
                #     if isinstance(handler, str):
                #         return request.send(200, handler)
                # else:
                #     return request.send(405, f"Method {method} not allowed for {path}")
        except json.JSONDecodeError:
            self.send(400, "Invalid JSON")
        except Exception as e:
            self.send(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        try:
            @self.Rute.call(self.path)
            def fnc(rute):
                print(rute)
                request.send(200, "test")
                # expected_method, handler = rute
                # if "GET" == expected_method:
                #     if callable(handler):
                #         return handler(request)
                #     if isinstance(handler, str):
                #         return request.send(200, handler)
                # else:
                #     return request.send(405, f"Method {method} not allowed for {path}")
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
        print(path)

        @self.RequestHandlerClass.Rute.get(path)
        def Alert():
            if '-D' in sys.argv or '--debug' in sys.argv:
                print(f'add rute:{path}')
        return Alert

    def Post(self, path):
        print(path)

        @self.RequestHandlerClass.Rute.post(path)
        def Alert():
            if '-D' in sys.argv or '--debug' in sys.argv:
                print(f'add rute:{path}')
        return Alert

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
        # all_script: list = []
        # txtpath = os.path.abspath(os.path.join('www', 'all-scripts.txt'))

        # def concat_files(*paths, prefix_format='', buffer=4 * 1024 * 1024) -> bytes:
        #     for path in paths:
        #         yield prefix_format.format(path).encode('utf-8')
        #         with open(path, 'rb') as file:
        #             while data := file.read(buffer):
        #                 yield data

        # def compress(res, name):
        #     wfile = res.sendFile(200, name)
        #     for data in concat_files(*(all_script), prefix_format='\n// {0}\n'):
        #         wfile(data)

        # file_scripts = open(txtpath, 'r', encoding='utf-8')
        # for path in file_scripts.read().split('\n'):
        #     if path != '':
        #         init_path = os.path.join('www', path)
        #         abspath = os.path.abspath(init_path)
        #         all_script.append(abspath)

        # file_scripts.close()

        Srv = Server(('localhost', 8000), ServerHandler)

        @Srv.Get("/")
        def Home(res):
            print("tets")
        # Srv.setGet("/~every.js", lambda res: compress(res, "/~every.js"))
        # Srv.setPost("/print", "play")
        # Srv.setPost("/devices", "play")
        # Srv.setPost("/query", "play")
        # Srv.setPost("/set", "play")
        # Srv.setPost("/connect", "play")
        # Srv.setPost("/exit", lambda res: sys.exit(0))
        # Srv.start()
    except KeyboardInterrupt:
        print("Server stopped by user.")
    except Exception as e:
        print(f"Error starting server: {str(e)}")
