from win32com.shell import shell,shellcon
import win32api, os, json

path = os.path.join(os.path.abspath("."),"aleo.json")

def load(key=None):
    data = json.load(open(path,"r"))
    if key == None: return data
    else: return data[key]

def save(**items):
    data = load()
    for k in items:data[k]=items[k]
    win32api.SetFileAttributes(path,128)
    json.dump(data,open(path,"w"))
    win32api.SetFileAttributes(path,2)

if not os.path.exists(path):
    open(path,"w").close()
    json.dump({
        "username":"",
        "level":None,
        "wave":0,
        "language":"russian"
    },open(path,"w"))
    win32api.SetFileAttributes(path,2)
