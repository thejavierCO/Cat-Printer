class RoutherHandler():
    __init__(self, method, rute):
        self.method: str = method
        self.rute: str = rute

    isMethod(self, method: str):
        return self.method == method


class RoutherStaticHandler(RoutherHandler):
    __init__(self, method, rute, directory):
        self.path: str = directory
        super().__init__(method, rute)


class RouthersHandler():
    paths = {}

    def add(self, handler: (RoutherHandler, RoutherStaticHandler)):
        method = handler.method
        rute = handler.rute
        self.paths[rute] = handler
