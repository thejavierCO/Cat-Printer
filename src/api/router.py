class Rutas():
    paths = {}

    def call(self, path: str):
        path, _, args = path.partition('?')
        if path in self.paths:
            def action(fns):
                fns(self.paths[path])
            return action
        elif "/" in self.paths:
            def action(fns):
                fns(self.paths["/"])
            return action


    def use(self, method: str, path: str,action):
        def handler(fns):
            self.paths[path] = [method, action]
        return handler

    def get(self, path: str,action):
        def handler(fns):
            self.paths[path] = ["GET", action]
            fns()
        return handler

    def post(self, path: str,action):
        def handler(fns):
            self.paths[path] = ["POST", action]
            fns()
        return handler
