# import os


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

    def preventDefault(self):
        self.default = False

    def install(self):
        print("install")

    def log(self, msg: str):
        print("log")


class Rutas():
    paths = {}
    configs: list = []

    def call(self, srv, method):
        for config in self.configs:
            if hasattr(config, "log"):
                config.log(f"{method}:{srv.path}")
            if hasattr(config, "default"):
                if config.default == True:
                    srv.sendJson(500, {"status": "error"})
                # path, _, args = path.partition('?')
                # if path in self.paths:
                #     def action(fns):
                #         fns(self.paths[path])
                #     return action
                # elif "/" in self.paths:
                #     def action(fns):
                #         fns(self.paths["/"])
                #     return action

    def use(self, classhandler: Plugin):
        start = classhandler()
        self.configs.append(classhandler())
        # def action(res):
        #     directory = RutasEstaticas("./www")

        # self.paths[path] = ["GET", lambda _: action(srv)]

        def handler(fns):
            fns()
        return handler

        # def use(self, path: str, action):
        #     self.paths[path] = ["All", action]

        #     def handler(fns):
        #         fns()
        #     return handler

    def get(self, path: str, action):
        self.paths[path] = ["GET", action]

        def handler(fns):
            fns()
        return handler

    def post(self, path: str, action):
        self.paths[path] = ["POST", action]

        def handler(fns):
            fns()
        return handler
