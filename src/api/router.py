# import os
import sys
# class RutasEstaticas():
#     def __init__(self, path: (str, None)):
#         self.raiz = ""
#         self.dir: list = []
#         if path is None:
#             self.raiz = "./www"
#         if os.path.isdir(os.path.abspath(self.raiz)):
#             self.dir = os.listdir(os.path.abspath(self.raiz))


class Plugin():
    def __init__(self):
        self.default = True

    def defaultResponse(self, res, msg: str = ""):
        if self.default == True:
            if msg != "":
                self.log(msg)
                res.sendJson(500, {"status": "error", "msg": msg})
            else:
                res.sendJson(500, {"status": "error"})

    def log(self, msg: str):
        if '-D' in sys.argv or '--debug' in sys.argv:
            print(msg)
        return self


class Rutas():
    paths = {}
    config: Plugin = None
    allowMethods: list = [
        "POST",
        "GET"
    ]

    def __init__(self):
        self.config = Plugin()

    def Log(self, msg):
        if hasattr(self.config, "log"):
            self.config.log(msg)

    def call(self, srv, method):
        path, _, args = srv.path.partition('?')
        if path in self.paths:
            expected_method, handler = self.paths[path]
        elif "/" in self.paths:
            expected_method, handler = self.paths["/"]
        else:
            return self.config.defaultResponse(srv, f"Not exist path:{path}")

        if expected_method in self.allowMethods:
            if callable(handler):
                return handler(srv)
            if isinstance(handler, str):
                return srv.send(200, handler)
        else:
            return self.config.defaultResponse(srv, f"Method {method} not allowed for {path}")

    def use(self, rute, classhandler):
        if classhandler is None:
            if isinstance(rute, Plugin):
                classhandler = rute
            elif isinstance(rute, str):
                return self.Log(f"rute is str")
            elif rute is None:
                return self.Log(f"default Plugin")
        start = classhandler()
        if hasattr(start, "install"):
            start.install(self)
        self.config = start

    def set(self, path: str, method: str, action):
        self.paths[path] = [method, action]
        self.Log(f"add: {method} {path}")
