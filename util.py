import os,sys,pygame

try:path=sys._MEIPASS
except:path="assets/"

def get_sprites(name):
    sprites = []
    i = 0
    while True:
        p = os.path.join(path,f"{name}{i}.png")
        if os.path.exists(p):
            sprites.append(pygame.image.load(p))
            i += 1
        else:
            break
    return sprites

def get_image(filename):
    return pygame.image.load(os.path.join(path,filename))

def get_path(filename):
    return os.path.join(path,filename)
