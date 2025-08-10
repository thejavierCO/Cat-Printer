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
