import sys
import os

from pathlib import Path
def importpath(path):
    strpath = str(path)
    if not strpath.startswith("/"):
        parent_path = Path(
            sys._getframe().f_globals.get("__file__", ".")).parent
        path = parent_path / path
    else:
        path = Path(path)
    try:
        sys.path.insert(0, str(path.parent))
        module = __import__(path.stem)
    finally:
        sys.path.pop(0)
    return module


app = importpath("./src/api/webapp.py")
printer = importpath("./src/printer.py")

all_script: list = []
txtpath = os.path.abspath(os.path.join('www', 'all-scripts.txt'))

def concat_files(*paths, prefix_format='', buffer=4 * 1024 * 1024) -> bytes:
    for path in paths:
        yield prefix_format.format(path).encode('utf-8')
        with open(path, 'rb') as file:
            while data := file.read(buffer):
                yield data

file_scripts = open(txtpath, 'r', encoding='utf-8')
for path in file_scripts.read().split('\n'):
    if path != '':
        init_path = os.path.join('www', path)
        abspath = os.path.abspath(init_path)
        all_script.append(abspath)

file_scripts.close()

Srv = app.Server(('localhost', 8000), app.ServerHandler)


@Srv.Post("/print")
def print_app(res):
    res.send(200,"test")

@Srv.Post("/devices")
def devices(res):
    res.send(200,"test")

@Srv.Post("/query")
def query(res):
    res.send(200,"test")

@Srv.Post("/set")
def set(res):
    res.send(200,"test")

@Srv.Post("/connect")
def connect(res):
    res.send(200,"test")

@Srv.Post("/exit")
def exist(res):
    res.send(200,"test")

@Srv.Get("/~every.js")
def compress(res):
    wfile = res.sendFile(200, res.path)
    for data in concat_files(*(all_script), prefix_format='\n// {0}\n'):
        wfile(data)

@Srv.Get("/")
def Home(res):
    homedir = "./www"
    path, _, args = res.path.partition('?')
    file_path = os.path.abspath(homedir+path)
    if os.path.isfile(file_path):
        return res.sendFileFormDirectory(200, file_path)
    if path.startswith("/"):
        return res.sendFileFormDirectory(200, os.path.abspath(file_path+"/index.html"))
    return res.send(404, "Path Not Found")

Srv.start()
