from tkinter import Tk
from tkinter import messagebox
import playing
import pygame
import saves
import util
import json
import sys
import os
import m

def main():
    pygame.init()

    menu = m.Menu()
    win = pygame.display.set_mode((500,500))
    pygame.display.set_caption("Aleo's Trip > Levels Menu")
    m.init(win,pygame)

    lvl = saves.load("level")
    if lvl == None: available = 0
    if lvl == "forest": available = 1
    if lvl == "mountains": available = 2
    if lvl == "desert": available = 3

    def forest():
        if available >= 0:
            menu.select_page(1)
            # playing.main(None if available == 0 else "forest")
    def mountains():
        if available >= 2:
            menu.select_page(2)
            # playing.main("mountains")
    def desert():
        if available >= 3:
            menu.select_page(3)
            # playing.main("desert")

    def back():
        menu.select_page(0)

    wave = saves.load("wave")

    menu.add_page(0,[
        m.Button("Forest",(5,5),(490,160),forest,(2,100,0)if available>=0else(90,90,90)),
        m.Button("Mountains",(5,170),(490,160),mountains,(86,82,134)if available>=2else(90,90,90)),
        m.Button("Desert",(5,335),(490,160),desert,(180,117,0)if available>=3else(90,90,90)),
    ])

    def play_forest(wave):
        if wave <= saves.load("wave"):
            playing.main(None if available==0else"forest",wave)
            sys.exit()
        else:
            print("skipped")

    menu.add_page(1,[
        m.Button("Back",(5,5),(490,120),back,(100,2,0),(128,20,20)),
        m.Button("1",(5,130),(94,94),lambda:play_forest(0if available==0else 1),(2,100,0)if wave>=0else(90,90,90)),
        m.Button("2",(5+99,130),(94,94),lambda:play_forest(2),(2,100,0)if wave>1else(90,90,90)),
        m.Button("3",(5+99*2,130),(94,94),lambda:play_forest(3),(2,100,0)if wave>2else(90,90,90)),
        m.Button("4",(5+99*3,130),(94,94),lambda:play_forest(4),(2,100,0)if wave>3else(90,90,90)),
        m.Button("5",(5+99*4,130),(94,94),lambda:play_forest(5),(2,100,0)if wave>4else(90,90,90))
    ])

    def play_mountains(wave):
        if 5+wave<=saves.load("wave"):
            playing.main("mountains",5+wave)
            sys.exit()

    menu.add_page(2,[
        m.Button("Back",(5,5),(490,120),back,(2,100,0),(128,20,20)),
        m.Button("1",(5,130),(94,94),lambda:play_mountains(0),(2,100,0)if wave>5else(90,90,90)),
        m.Button("2",(5+99,130),(94,94),lambda:play_mountains(1),(2,100,0)if wave>6else(90,90,90)),
        m.Button("3",(5+99*2,130),(94,94),lambda:play_mountains(2),(2,100,0)if wave>7else(90,90,90)),
        m.Button("4",(5+99*3,130),(94,94),lambda:play_mountains(3),(2,100,0)if wave>8else(90,90,90)),
        m.Button("5",(5+99*4,130),(94,94),lambda:play_mountains(4),(2,100,0)if wave>9else(90,90,90)),
        m.Button("6",(5,130+99),(94,94),lambda:play_mountains(5),(2,100,0)if wave>10else(90,90,90)),
        m.Button("7",(5+99,130+99),(94,94),lambda:play_mountains(6),(2,100,0)if wave>11else(90,90,90))
    ])



    def play_desert(wave):
        if 12+wave<=saves.load("wave"):
            playing.main("desert",wave)
            sys.exit()

    menu.add_page(3,[
        m.Button("Back",(5,5),(490,120),back,(2,100,0),(128,20,20)),
        m.Button("1",(5,130),(94,94),lambda:play_desert(0),(2,100,0)if wave>12else(90,90,90)),
        m.Button("2",(5+99,130),(94,94),lambda:play_desert(1),(2,100,0)if wave>13else(90,90,90)),
        m.Button("3",(5+99*2,130),(94,94),lambda:play_desert(2),(2,100,0)if wave>14else(90,90,90)),
        m.Button("4",(5+99*3,130),(94,94),lambda:play_desert(3),(2,100,0)if wave>15else(90,90,90)),
        m.Button("5",(5+99*4,130),(94,94),lambda:play_desert(4),(2,100,0)if wave>16else(90,90,90)),
        m.Button("6",(5,130+99),(94,94),lambda:play_desert(5),(2,100,0)if wave>17else(90,90,90)),
        m.Button("7",(5+99,130+99),(94,94),lambda:play_desert(6),(2,100,0)if wave>18else(90,90,90)),
        m.Button("8",(5+99*2,130+99),(94,94),lambda:play_desert(7),(2,100,0)if wave>19else(90,90,90))
    ])



    menu.select_page(0)

    clock = pygame.time.Clock()

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
        win.fill((0,0,0))
        menu.draw(events)

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()
