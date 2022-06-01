import pygame
import util

def main():
    pygame.init()

    win = pygame.display.set_mode((853,480))
    pygame.display.set_caption("Aleo's Trip > Start")
    pygame.display.set_icon(util.get_image("favicon.png"))

    button = pygame.Rect(46,273,171,33)
    button_pressed_layout = pygame.Surface(button.size,pygame.SRCALPHA)
    pygame.draw.rect(button_pressed_layout,(0,0,0,64),(0,0,*button.size),0,13)
    pygame.draw.rect(button_pressed_layout,(0,0,0,128),(0,0,*button.size),5,13)
    start_img = pygame.transform.smoothscale(util.get_image("start-image.jpg"),win.get_size())

    clock = pygame.time.Clock()

    is_button_pressed = False

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(event.pos):
                    if event.button == 1:
                        is_button_pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if button.collidepoint(event.pos):
                        if event.button == 1:
                            import menu
                            menu.main()
                            sys.exit()
                    is_button_pressed = False
        win.blit(start_img,(0,0))
        if is_button_pressed:
            win.blit(button_pressed_layout,(button.x,button.y))

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()
