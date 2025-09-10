# import os
import sys


class Rutas():
    paths = {}
    allowMethods: list = [
        "POST",
        "GET"
    ]

    def __init__(self):
        "loop"

    def Log(self, msg):
        if '-D' in sys.argv or '--debug' in sys.argv:
            print(msg)
        return self

    def call(self, path, method):
        "loop"
        # path, _, args = srv.path.partition('?')
        # if path in self.paths:
        #     expected_method, handler = self.paths[path]
        # elif "/" in self.paths:
        #     expected_method, handler = self.paths["/"]
        # else:
        #     return self.config.defaultResponse(srv, f"Not exist path:{path}")

        # if expected_method in self.allowMethods:
        #     if callable(handler):
        #         return handler(srv)
        #     if isinstance(handler, str):
        #         return srv.send(200, handler)
        # else:
        #     return self.config.defaultResponse(srv, f"Method {method} not allowed for {path}")

    def use(self, method: str):
        def act(fn):
            if not callable(fn):
                raise Exception("Action must be callable")
            elif fn.__class__ is type:
                raise Exception("Class not allowed here")
            else:
                fn.isPath = True
                fn.method = method
                fn.name = fn.__name__
                return fn
        return act

    def set(self, path: str, method: str, action=None):
        if method not in self.allowMethods:
            raise Exception(f"Method not allowed {method}")
        if path in self.paths:
            raise Exception(f"Path already exists {path}")

        if action is None or not callable(action):
            def act(action):
                if not callable(action):
                    raise Exception("Action must be callable")
                if action.__class__ is type:
                    start = action()
                    start.use = self.use
                    paths = [fn for fn in dir(start) if callable(getattr(start, fn)) and hasattr(
                        getattr(start, fn), "isPath") and getattr(start, fn).isPath]
                    for fn in paths:
                        action = getattr(start, fn)
                        if fn == start.__class__.__name__:
                            self.set(path, action.method, action)
                            continue
                        pth = f"{path}/{action.name}" if path != "/" else f"/{action.name}"
                        self.set(pth, action.method, action)
                else:
                    self.set(path, method, action)
            return act
        else:
            self.paths[path] = [method, action]
            self.Log(f"{method}:{path} registered")


if __name__ == "__main__":
    Main = Rutas()

    @Main.set("/api")
    class api():
        def api(self):
            return "home"
        def query(self):
            return "query"
        def set(self):
            return "set"
        def print(self):
            return "print"

    @Main.set("/")
    def Home():
        return "Home"
