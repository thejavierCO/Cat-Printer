import sys
import os
import json
import io

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


class DictAsObject(dict):
    " Let you use a dict like an object in JavaScript. "

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        self[key] = value


app = importpath("./src/api/webapp.py")
printer = importpath("./src/printerApi.py")
PrinterApp = printer.PrinterHandler()

all_script: list = []
txtpath = os.path.abspath(os.path.join('www',"old", 'all-scripts.txt'))


def concat_files(*paths, prefix_format='', buffer=4 * 1024 * 1024) -> bytes:
    for path in paths:
        yield prefix_format.format(path).encode('utf-8')
        with open(path, 'rb') as file:
            while data := file.read(buffer):
                yield data


PrinterApp.load_config()
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
    body = res.getBody()
    # print(res)
    PrinterApp.update_printer()
    PrinterApp.printer.print(io.BytesIO(body))
    res.sendJson(200, {"status": "ok", "data": "Printed successfully"})


@Srv.Post("/devices")
def devices(res):
    data = DictAsObject(json.loads(res.getBody()))
    PrinterApp.printer.connect(None)
    devices_list = [{
        'name': device.name,
        'address': device.address
    } for device in PrinterApp.printer.scan(everything=data.get('everything'))]
    res.sendJson(200, {'devices': devices_list})


@Srv.Post("/query")
def query(res):
    PrinterApp.load_config()
    res.sendJson(200, PrinterApp.settings)


@Srv.Post("/set")
def set(res):
    data = DictAsObject(json.loads(res.getBody()))
    for key in data:
        PrinterApp.settings[key] = data[key]
    PrinterApp.save_config()
    PrinterApp.update_printer()
    res.sendJson(200)


@Srv.Post("/connect")
def connect(res):
    data = DictAsObject(json.loads(res.getBody()))
    name, address = data['device'].split(',')
    if not name or not address:
        res.sendJson(500, {
            'name': 'InvalidDevice',
            'details': 'Device name or address is empty'
        })
        return
    if PrinterApp.printer.device is None:
        PrinterApp.printer.connect(name, address)
        res.sendJson(200, {
            'status': 'ok',
            'data': 'Connected to {} at {}'.format(name, address)
        })
        return
    else:
        PrinterApp.printer.connect(name, address)
        res.sendJson(200, {
            'status': 'ok',
            'data': 'Reconnected to {} at {}'.format(name, address)
        })
        return


@Srv.Post("/exit")
def exist(res):
    res.sendJson(200, {'status': 'ok'})
    PrinterApp.exit()


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
