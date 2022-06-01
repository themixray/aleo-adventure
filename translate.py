import saves
import util
import json

languages = json.load(open(util.get_path("languages.json"),"r",encoding="utf8"))

def set_language(name):
    saves.save(language=name)

def get_language():
    return saves.load("language")

def translate(index):
    return languages[get_language()][index]
