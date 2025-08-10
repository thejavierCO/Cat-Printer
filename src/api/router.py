class Rutas():
    paths = {}

    def call(self, path: str):
        if path in self.paths:
            def action(fns):
                fns(self.paths[path])
            return action
        else:
            def action(fns):
                print("not exist action")
            return action

    def use(self, method: str, path: str):
        def handler(fns):
            self.paths[path] = [method, fns]
        return handler

    def get(self, path: str):
        def handler(fns):
            self.paths[path] = ["GET", fns]
            fns()
        return handler

    def post(self, path: str):
        def handler(fns):
            self.paths[path] = ["POST", fns]
            fns()
        return handler
