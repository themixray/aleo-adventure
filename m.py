screen = 0
pygame = 0
def init(screen_, pygame_):
    global screen, pygame
    screen = screen_
    pygame = pygame_

font = lambda x: pygame.font.SysFont('Console', x)

class Button:
    def __init__(self,
                 text,
                 pos,
                 size,
                 func=None,
                 bg=(90,90,90),
                 abg=(255,255,255),
                 sbg=(50,50,50),
                 fg=(200,200,200),
                 afg=(0,0,0),
                 sfg=(160,160,160),
                 font_size=30):
        self.bg = bg
        self.fg = fg
        self.pos = pos
        self.abg = abg
        self.afg = afg
        self.sfg = sfg
        self.sbg = sbg
        self.active = 0
        self.func = func
        self.size = size
        self.text = text
        self.last_active = 0
        self.font_size = font_size
        self.color(bg,fg)

    def color(self,bg,fg):
        text = font(self.font_size).render(self.text,1,fg)
        self.image = pygame.Surface(self.size)
        self.image.fill(bg)
        self.rect = self.image.get_rect()
        rect = text.get_rect(center=self.rect.center)
        self.image.blit(text,rect)
        self.rect.x, self.rect.y = self.pos

    def draw(self,s=False):
        if self.active:
            self.color(self.abg,self.afg)
            if not self.last_active:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.last_active = True
        elif s:
            self.color(self.sbg,self.sfg)
            if not self.last_active:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.last_active = True
        else:
            self.color(self.bg,self.fg)
            if self.last_active:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.last_active = False
        screen.blit(self.image,self.rect)

class Input:
    def __init__(self,hint,pos,wh,func=None,pretext="",color=(60,60,60),max=100,mask=None):
        self.image = pygame.Surface(wh)
        self.image.fill(color)
        pygame.draw.rect(self.image,(90,90,90),(0,0,*wh),5)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.hint = font(30).render(' ' + hint,1,(90,90,90))
        self.active = 0
        self.max = max
        self.text = pretext
        text = font(30).render(self.text,1,(200,200,200))
        self.tick = 0
        self.line = False
        self.mask = mask
        self.func = func

    def add_symbol(self, symbol):
        if len(self.text) < self.max:
            if self.mask == None or symbol in self.mask:
                self.text += symbol
                if self.func != None:
                    self.func(self.text)

    def del_symbol(self):
        if len(self.text) > 0:
            self.text = self.text[:-1]
            if self.func != None:
                self.func(self.text)

    def draw(self):
        tempsurf = pygame.Surface(self.rect.size)
        tempsurf.blit(self.image,(0,0))
        if self.text == '':
            tempsurf.blit(self.hint,(5,self.rect.height/2-self.hint.get_height()/2))
        if self.tick >= 30:
            self.tick = 0
            self.line = self.line == 0
        else:
            self.tick += 1
        text = font(30).render(self.text,1,(200,200,200))
        rect = text.get_rect(x=self.rect.x+10,centery=self.rect.centery)
        if rect.right+10 > self.rect.right:
            rect.x -= rect.right+10 - self.rect.right
        rect.x -= self.rect.x
        rect.y -= self.rect.y
        if self.line and self.active:
            pygame.draw.line(tempsurf,(200,200,200),(rect.right,rect.y),(rect.right,rect.y+30))
        tempsurf.blit(text,rect)
        screen.blit(tempsurf,self.rect)

class Label:
    def __init__(self,text,pos,color=(200,0,0)):
        self.image = font(30).render(text,1,color)
        self.rect = self.image.get_rect(center=pos)

    def draw(self):
        screen.blit(self.image,self.rect)

class Menu:
    def __init__(self):
        self.pages = {}
        self.page = None

    def reset_cursor(self):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def empty_page(self):
        self.page = None

    def select_page(self,num):
        self.page = num

    def add_page(self,num,elements=[]):
        self.pages[num] = elements

    def draw(self,events):
        if self.page is not None:
            page = self.pages[self.page]
        else:
            page = []

        self.labels = []
        self.inputs = []
        self.buttons = []

        for v in page:
            if type(v) == Label:
                v.draw()
                self.labels.append(v)
            elif type(v) == Input:
                v.draw()
                self.inputs.append(v)
            elif type(v) == Button:
                v.draw(v.rect.contains(
                    pygame.Rect(
                        (pygame.mouse.get_pos()[0]-1,
                         pygame.mouse.get_pos()[1]-1), (2, 2)
                    )))
                self.buttons.append(v)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                for button in self.buttons:
                    if event.button == 1:
                        button.active = False
                        if button.rect.collidepoint(event.pos):
                            if button.func != None:
                                button.func()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        if event.button == 1:
                            button.active = True
                for inp in self.inputs:
                    inp.active = (1 if inp.rect.collidepoint(event.pos) else 0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    for inp in self.inputs:
                        if inp.active:
                            inp.del_symbol()
                elif event.key != pygame.K_RETURN:
                    for inp in self.inputs:
                        if inp.active:
                            inp.add_symbol(event.unicode)

    def main(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(60)
            screen.fill((30,30,30))
            self.draw()
