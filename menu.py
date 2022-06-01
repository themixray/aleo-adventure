from tkinter import Tk
from tkinter import messagebox
import translate
import pygame
import saves
import util
import sys
import os
import m

def main():
    pygame.init()

    menu = m.Menu()
    win = pygame.display.set_mode((500,500))
    pygame.display.set_caption("Aleo's Trip > Start Menu")
    m.init(win,pygame)

    def intable(i):
        try:
            int(i)
            return True
        except:
            return False

    def play():
        nonlocal username_entry
        t = username_entry.text.split("#")
        if len(t) != 2 or len(t[1]) != 4 or not intable(t[1]):
            username_entry.text = ""
            t = Tk()
            t.withdraw()
            messagebox.showerror("Aleo's Trip > Error","Напишите ник#тег")
            t.destroy()
            return
        saves.save(username=username_entry.text)

        import levels
        levels.main()
        sys.exit()

    planet = pygame.transform.scale(util.get_image("planet.png"),(40,40))

    username_entry = m.Input("User#0001",(145,195),(210,50))
    username_entry.text = saves.load("username")

    menu.add_page(0,[
         username_entry,
         m.Button("Play",(190,250),(120,50),play),
         m.Button("",(5,5),(50,50),lambda:menu.select_page(1))
    ])

    def set_lang(n,m):
        nonlocal langs
        translate.set_language(n)
        for i in range(len(langs)):
            if i != m:
                langs[i].bg = (90,90,90)
            else:
                langs[i].bg = (25,128,25)

    lang = translate.get_language()
    langs = [
        m.Button("Русский",(130,60),(150,50),lambda:set_lang("russian",0),(25,128,25)if lang =="russian"else(90,90,90)),
        m.Button("English",(130,115),(150,50),lambda:set_lang("english",1),(25,128,25)if lang =="english"else(90,90,90)),
        m.Button("Deutsch",(130,170),(150,50),lambda:set_lang("deustch",2),(25,128,25)if lang =="deustch"else(90,90,90)),
        m.Button("Chinese",(130,225),(150,50),lambda:set_lang("china",3),(25,128,25)if lang =="china"else(90,90,90)),
        m.Button("Український",(285,60),(210,50),lambda:set_lang("ukraine",4),(25,128,25)if lang =="ukraine"else(90,90,90)),
        m.Button("Türk",(285,115),(150,50),lambda:set_lang("turk",5),(25,128,25)if lang =="turk"else(90,90,90)),
        m.Button("Polski",(285,170),(150,50),lambda:set_lang("polski",6),(25,128,25)if lang =="polski"else(90,90,90)),
        m.Button("Español",(285,225),(150,50),lambda:set_lang("espanol",7),(25,128,25)if lang =="espanol"else(90,90,90))
    ]

    menu.add_page(1,[m.Button("Back",(5,5),(120,50),lambda:menu.select_page(0),(128,25,25)),*langs])
    menu.select_page(0)


    clock = pygame.time.Clock()

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        win.fill((120,120,120))
        menu.draw(events)

        if menu.page == 0:
            pygame.draw.circle(win,(200,200,200),(30,30),19)
            win.blit(planet,(10,10))

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()
