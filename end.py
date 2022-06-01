import threading
import win32gui
import win32api
import pygame
import random
import util

def main():
    pygame.init()

    win = pygame.display.set_mode((853,480))
    pygame.display.set_caption("Aleo's Trip > End")

    font = pygame.font.Font(util.get_path("pixel-font.otf"),30)
    hwnd = pygame.display.get_wm_info()["window"]
    clock = pygame.time.Clock()



    run = True

    metrics = (win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1))

    def get_win_rect(hwnd):
        r = win32gui.GetWindowRect(hwnd)
        return pygame.Rect(r[0],r[1],r[2]-r[0],r[3]-r[1])

    win_rect = get_win_rect(hwnd)
    def pos_checker():
        while True:
            nonlocal run
            if not run:
                break
            pos = get_win_rect(hwnd)
            nonlocal win_rect
            if win_rect != pos:
                win_rect = pos
    threading.Thread(target=pos_checker,daemon=1).start()


    complete_img = pygame.transform.smoothscale(util.get_image("complete-image.jpg"),win.get_size())
    creators_img = pygame.transform.smoothscale(util.get_image("creators-image.jpg"),win.get_size())
    translators_img = pygame.transform.smoothscale(util.get_image("translators-image.jpg"),win.get_size())
    index = 0
    pashalka = font.render("миксрей#5138",0,(255,255,255))
    pashalka_pos = None
    while True:
        pashalka_pos = (random.randint(10,metrics[0]-pashalka.get_width()-10),
                        random.randint(40,metrics[1]-pashalka.get_height()-10))
        if not win_rect.colliderect(pygame.Rect(*pashalka_pos,*pashalka.get_size())):
            break

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONUP:
                index += 1
                if index == 3:
                    run = False
        if index == 0:
            win.blit(complete_img,(0,0))
        elif index == 1:
            win.blit(creators_img,(0,0))
        elif index == 2:
            win.blit(translators_img,(0,0))
        win.blit(pashalka,(pashalka_pos[0]-win_rect.x+(random.randint(0,10)-5),
                           pashalka_pos[1]-win_rect.y+(random.randint(0,10)-5)))

        pygame.display.flip()
        clock.tick(25)
    pygame.quit()

if __name__ == '__main__':
    main()
