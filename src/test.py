class Main():
    part:list = {}
    def __init__(self,name,port):
        self.name = name
        self.port = port

    def __call__(self):
        def act(f):
            name = ""
            if f.__class__ is type:
                name = f"/{f().__class__.__name__}"
            elif callable(f):
                name = f"/{f.__name__}"
            else:
                raise Exception("Action must be callable")
            
            if name in self.part:
                raise Exception("Path already exists")

            if name == "/default":
                name = "/"
            
            self.part[name] = f
            print(name)
        return act

    def call(self,name:str):
        if name in self.part:
            return self.part[name]
        else:
            path = [p for p in name.split("/") if p != ""]
            print(path)
            return None



if __name__ == "__main__":
    main = Main("local",8000)

    @main()
    class default():
        def default(self):
            print("default")

    @main()
    class api():
        def api(self):
            print("default")
        class auth():
            def auth(self):
                print("auth")
    
    print(main.call("/api/auth"))
