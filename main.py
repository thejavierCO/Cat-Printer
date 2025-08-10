# import sys
# from pathlib import Path


# def importpath(path):
#     strpath = str(path)
#     if not strpath.startswith("/"):
#         parent_path = Path(
#             sys._getframe().f_globals.get("__file__", ".")).parent
#         path = parent_path / path
#     else:
#         path = Path(path)
#     try:
#         sys.path.insert(0, str(path.parent))
#         module = __import__(path.stem)
#     finally:
#         sys.path.pop(0)
#     return module


# server = importpath("./src/server.py")
# print(server.serve())

# asdhioashjoidoaisd

# def test(func):

#     def wrapper(*args, **kwargs):
#         print(args, kwargs)
#         func("test")
#     return wrapper


# @test
# def play(name):
#     print("init "+name)


# play(name="dad")
# asdhioashjoidoaisd

class app1():
    def __init__(self):
        self.init = False

    def send(self, msg: str):
        print(msg)

    def get(self, rute: str):
        def msg(func):
            func(self)
        return msg


app = app1()


@app.get("/")
def rute(res):
    res.send("ok")
