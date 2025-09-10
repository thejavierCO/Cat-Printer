class Main():
    def __init__(self):
        self.r = {}
    
    def call(self,name):
        if name in self.r:
            master = self.r[name]
            def get(fns):
                name = fns.__name__
                if name in dir(master):
                    fns(getattr(master,name))
                else:
                    raise Exception("not exist")
            return get
        else:
            raise Exception("not exist")

    def set(self):
        def act(fns):
            if fns.__class__ is type:
                start = fns()
                name = f"{start.__class__.__name__}"
                self.r[name] = start
            else:
                print(fns)
            return fns
        return act



if __name__ == "__main__":
    main = Main()

    @main.set()
    class robot():
        def Move(self):
            print("move")
    
    @main.call("robot")
    def Move(act):
        act()


