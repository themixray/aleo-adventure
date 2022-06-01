from translate import translate
import threading
import textwrap
import random
import pygame
import saves
import time
import util
import sys
import os
import m

def main(level=None,levelWave=0):
    pygame.init()

    menu = m.Menu()
    win = pygame.display.set_mode((1280,720),pygame.FULLSCREEN)
    pygame.display.set_caption("Aleo's Trip > Game")
    m.init(win,pygame)

    font = pygame.font.Font(util.get_path("font.ttf"),15)

    fps = 60

    def to_menu():
        import levels
        levels.main()
        sys.exit()

    menu.add_page(0,[m.Button("Quit",(1155,5),(120,50),to_menu,(128,25,25),sbg=(64,5,5))])
    menu.select_page(0)

    class scene_manager:
        def __init__(self,scene):
            self.after_name = scene
            self.name = scene
            self.bg = get_background(scene)
            self.is_trans = False
            self.trans_count = 0
            self.callback = None
        def get_name(self):
            return self.after_name
        def set_scene(self,name,callback=None):
            self.after_name = name
            self.callback = callback
            self.is_trans = True
        def _filled(self,w,h,r,g,b,a):
            s = pygame.Surface((w,h),pygame.SRCALPHA)
            s.fill((r,g,b,a))
            return s
        def draw_bg(self):
            win.blit(self.bg,(0,0))
        def draw_trans(self):
            if self.is_trans:
                if self.trans_count < 256:
                    s = self._filled(*win.get_size(),
                            0,0,0,self.trans_count)
                elif self.trans_count > 255:
                    s = self._filled(*win.get_size(),
                         0,0,0,510-self.trans_count)
                if self.trans_count == 255:
                    self.name = self.after_name
                    self.bg = get_background(self.name)
                    if self.callback != None:self.callback()
                win.blit(s,(0,0))
                self.trans_count += 5
                if self.trans_count > 510:
                    self.trans_count = 0
                    self.is_trans = False

    class dialog:
        def __init__(self,rect,right,offset,font_size):
            self.rect = rect
            self.hidden_x = -rect.width if right else win.get_width()
            self.showing_x = rect.x
            self.rect.x = self.hidden_x
            self.is_hiding = False
            self.is_showing = False
            self.visible = False
            self.showing_time = time.time()
            self.text = "текст"
            self.image = pygame.transform.scale(util.get_image("dialog.png"),rect.size)
            if not right: self.image = pygame.transform.flip(self.image,1,0)
            self.offset = offset
            self.font = pygame.font.Font(util.get_path("font.ttf"),font_size)
            self.wait_seconds = 2
            self.right = right
            self.callback = lambda:None
        def draw(self):
            s = self.image.copy()
            n = 0
            for i in self.text.split("\n"):
                t = self.font.render(i,1,(20,20,20))
                s.blit(t,(self.offset[0]if self.right else self.rect.width-t.get_width()-self.offset[0],self.offset[1]+n))
                n += t.get_height()+5
            skiptext = self.font.render("Click to skip",1,(100,100,100))
            s.blit(skiptext,(30,self.rect.height-30-skiptext.get_height()) if not self.right else (55,self.rect.height-10-skiptext.get_height()))
            if self.is_showing:
                if self.right:
                    self.rect.x += 5
                else:
                    self.rect.x -= 5
                if (self.right and self.rect.x >= self.showing_x) or (not self.right and self.rect.x <= self.showing_x):
                    self.rect.x = self.showing_x
                    self.is_showing = False
                    self.visible = True
                    self.showing_time = time.time()
            if self.visible:
                if pygame.mouse.get_pressed()[0]:
                    if self.rect.collidepoint(pygame.mouse.get_pos()):
                        nonlocal mouse_click_enable
                        mouse_click_enable = True
                        self.is_hiding = True
                        self.callback()
            if self.is_hiding:
                if self.right:
                    self.rect.x -= 5
                else:
                    self.rect.x += 5
                if (self.right and self.rect.x <= self.hidden_x) or (not self.right and self.rect.x >= self.hidden_x):
                    self.rect.x = self.hidden_x
                    self.is_hiding = False
            win.blit(s,self.rect)
        def set_text(self,text,callback=lambda:None):
            self.callback = callback
            self.text = text
            if not self.visible:
                self.is_showing = True
                nonlocal mouse_click_enable
                mouse_click_enable = False


    class player:
        def __init__(self):
            self.speed = 7
            self.rect = pygame.Rect(50,200,350,550)
            self.type = 1
            self.right = True
            self.flipOffset = (-125,0)
            self.shotCount = 0
            self.isShotAnim = False
            self.isJump = False
            self.jumpStep = 0.5
            self.jumpHeight = 9
            self.jumpCount = self.jumpHeight
            self.arrowWidth = 500
            self.shotPressedUp = False
            self.health = 1000
            self.max_health = 1000
            self.hitbox = pygame.Rect(30,220,200,270)
            self.strong = 80
            self.shotDelay = 1
            self.lastShot = time.time()
            self.dialog = dialog(pygame.Rect(5,100,300,300),True,(70,20),20)
            self.reload_sprites()
        def reload_sprites(self):
            self.shotSprites = util.get_sprites(f"player{self.type}")
            for n,v in enumerate(self.shotSprites):
                self.shotSprites[n] = pygame.transform.scale(v,self.rect.size)
            self.idleSprite = self.shotSprites[0]
        def draw(self):
            if self.isShotAnim:
                sprite = self.shotSprites[round(self.shotCount)]
                if self.shotCount+1 > len(self.shotSprites):
                    if self.shotPressedUp and time.time() > self.lastShot+self.shotDelay:
                        self.lastShot = time.time()
                        self.isShotAnim = False
                        self.shotCount = 0
                        self.showPressedUp = False
                        self._shot()
                        shot_delay_stamina.value = 0
                else:
                    self.shotCount += 0.2
            else:
                sprite = self.idleSprite
            sprite = sprite.copy()

            shot_delay_stamina.value = time.time()-self.lastShot

            if not self.right:
                sprite = pygame.transform.flip(sprite,1,0)

            if self.isJump:
                if self.jumpCount >= -self.jumpHeight:
                    if self.jumpCount < 0:
                        self.rect.y += (self.jumpCount ** 2) / 2
                    else:
                        self.rect.y -= (self.jumpCount ** 2) / 2
                    self.jumpCount -= self.jumpStep
                    self.jumpCount = round(self.jumpCount,1)
                else:
                    self.isJump = False
                    self.jumpCount = self.jumpHeight

            if self.health <= 0:
                self.respawn()
            else:
                if self.health < self.max_health:
                    self.setHealth(self.health+self.health*0.001)

            win.blit(sprite,self.rect)
            self.dialog.draw()
        def say(self,text,callback=lambda:None):
            self.dialog.set_text(text,callback)
        def get_speed(self,f):
            return fps/f*self.speed
        def flip(self,right):
            if self.right != right:
                self.right = right
                if right:
                    self.rect.x -= self.flipOffset[0]
                    self.rect.y -= self.flipOffset[1]
                    self.hitbox.x += self.flipOffset[0]
                else:
                    self.rect.x += self.flipOffset[0]
                    self.rect.y += self.flipOffset[1]
                    self.hitbox.x -= self.flipOffset[0]
        def move(self,right,fps_):
            if right:
                s = self.get_speed(fps_)
                if self.rect.x+self.hitbox.right+s <= win.get_width():
                    self.rect.x += s
                self.flip(True)
            else:
                s = self.get_speed(fps_)
                if self.rect.x+self.hitbox.x-s >= 0:
                    self.rect.x -= s
                self.flip(False)
        def jump(self):
            if not self.isJump:
                player.isJump = True
        def _shot(self):
            arrows.append(arrow(self.getStartShotX(),self.rect.y+20,
                    self.arrowWidth,self.right,self.strong,self.type))
        def shot(self,x=951):
            self.setShotX(x)
            self.isShotAnim = True
            self.shotPressedUp = False
        def setShotX(self,x):
            self.arrowWidth = x/951*500
        def getStartShotX(self):
            return self.rect.x-70
        def setMaxHealth(self,v):
            self.max_health = v
            health_stamina.max_value = v
        def setHealth(self,v):
            self.health = v
            health_stamina.value = v
        def setShotDelay(self,v):
            self.shotDelay = v
            shot_delay_stamina.value = v
        def respawn(self):
            nonlocal was_scene
            was_scene = scene.name
            scene.set_scene("death",unload)
            self.setHealth(self.max_health)
    player = player()

    class trader_quiz:
        def __init__(self,
                     rect,
                     question,
                     answers,
                     right_answer,
                     back_color,
                     question_color,
                     answer_color,
                     answer_active_color,
                     border_color,
                     right_callback,
                     left_callback):
            self.rect = pygame.Rect(rect.x,win.get_height(),*rect.size)
            self.final_rect = rect
            self.question = question
            self.answers = answers
            self.right_answer = right_answer
            question_font = pygame.font.Font(util.get_path("font.ttf"),25)
            answer_font = pygame.font.Font(util.get_path("font.ttf"),20)
            self.back_color = back_color
            self.border_color = border_color
            self.surface = pygame.Surface(rect.size)
            self.question_surface = question_font.render(question,1,question_color)
            self.answers_surfaces = [answer_font.render(i,1,answer_color)for i in answers]
            self.answers_active_surfaces = [answer_font.render(i,1,answer_active_color)for i in answers]
            self.answers_rects = []
            y = 15+self.question_surface.get_height()
            for v in self.answers_surfaces:
                self.answers_rects.append(pygame.Rect(10,y,*v.get_size()))
                y += 5+v.get_height()
            self.removed = False
            self.visible = False
            self.is_hiding = False
            self.is_showing = False
            self.start_speed = 15
            self.speed = self.start_speed
            self.right_callback = right_callback
            self.left_callback = left_callback
        def hide(self):
            self.is_hiding = True
            self.is_showing = False
        def show(self):
            self.is_hiding = False
            self.is_showing = True
        def draw(self):
            if not self.removed:
                relative_pos = pygame.mouse.get_pos()
                relative_pos = (relative_pos[0]-self.rect.x,relative_pos[1]-self.rect.y)

                nonlocal mouse_click_enable
                mouse_click_enable = not(relative_pos[0]>=0and relative_pos[0]<self.rect.width\
                                         and relative_pos[1]>=0and relative_pos[1]<self.rect.height)

                if self.is_showing:
                    self.rect.y -= self.speed
                    self.speed = (self.rect.y-self.final_rect.y)/self.speed
                    if self.rect.y <= self.final_rect.y:
                        self.rect.y = self.final_rect.y
                        self.is_showing = False
                        self.visible = True
                        self.speed = self.start_speed
                if self.is_hiding:
                    self.rect.y += self.speed
                    self.speed = (win.get_height()-self.rect.y)/self.speed
                    if self.rect.y >= win.get_height():
                        self.rect.y = self.final_rect.y
                        self.is_hiding = False
                        self.removed = True
                        self.speed = self.start_speed
                        mouse_click_enable = True
                self.surface.fill(self.back_color)
                pygame.draw.rect(self.surface,self.border_color,[0,0,*self.rect.size],5)
                self.surface.blit(self.question_surface,(10,10))

                for i in range(len(self.answers)):
                    r = self.answers_rects[i]
                    if r.collidepoint(relative_pos) and self.visible:
                        if pygame.mouse.get_pressed()[0]:
                            if i == self.right_answer:
                                self.right_callback(self.answers[i])
                            else:
                                self.left_callback(self.answers[i])
                        self.surface.blit(self.answers_active_surfaces[i],r)
                    else:
                        self.surface.blit(self.answers_surfaces[i],r)

                win.blit(self.surface,self.rect)

    class trader:
        def __init__(self,rect,image,question,answers,
                     right_answer,right_callback,left_callback):
            self.final_rect = rect
            self.rect = pygame.Rect(win.get_width(),rect.y,*rect.size)
            self.image = pygame.transform.scale(image,rect.size)
            self.is_showing = False
            self.is_hiding = False
            self.start_speed = 25
            self.speed = self.start_speed
            self.quiz = trader_quiz(
                pygame.Rect(320,180,640,210),
                question,answers,right_answer,(120,50,50),
                (250,200,200),(200,180,180),(220,220,220),
                (140,70,70),right_callback,left_callback)
            self.dialog = dialog(pygame.Rect(975,100,300,300),False,(70,20),15)
        def hide(self):
            self.quiz.hide()
            self.is_hiding = True
            self.is_showing = False
        def show(self):
            self.show_only_quiz()
            self.show_only_me()
        def show_only_quiz(self):
            self.quiz.show()
        def show_only_me(self):
            self.is_hiding = False
            self.is_showing = True
        def say(self,text,callback=lambda:None):
            self.dialog.set_text(text,callback)
        def draw(self):
            if self.is_showing:
                self.rect.x -= self.speed
                self.speed = (self.rect.x-self.final_rect.x)/self.speed
                if self.rect.x <= self.final_rect.x:
                    self.rect.x = self.final_rect.x
                    self.is_showing = False
                    self.speed = self.start_speed
            if self.is_hiding:
                self.rect.x += self.speed
                self.speed = (win.get_width()-self.rect.x)/self.speed
                if self.rect.x >= win.get_width():
                    self.rect.x = win.get_width()
                    self.is_hiding = False
                    self.speed = self.start_speed

            win.blit(self.image,self.rect)
            self.dialog.draw()
            self.quiz.draw()

    class arrow:
        def __init__(self,x,y,tick,right,strong,type):
            self.sprite = pygame.transform.scale(util.get_image(f"arrow{type}.png"),(500,500))
            if not right: self.sprite = pygame.transform.flip(self.sprite,1,0)
            if right:
                self.hitbox = pygame.Rect(300,235,180,15)
            else:
                self.hitbox = pygame.Rect(20,235,180,15)
            self._sx = x
            self._yt = 0
            self.rect = pygame.Rect(x,y,500,500)
            self.tick = tick
            self.right = right
            if right:
                self.rotate = 360
            else:
                self.rotate = 0
            self.strong = strong
            self.destroy_tick = 120
            self.stopped = False
        def draw(self,fps_):
            if self.tick > 0 and not self.stopped:
                self.tick -= 5
                if self.right:
                    self.rect.x += self.tick/25
                    self.rotate -= self.tick/1500
                    self.hitbox.x += self.tick/250
                else:
                    self.rect.x -= self.tick/25
                    self.rotate += self.tick/1500
                    self.hitbox.x -= self.tick/250
                self.hitbox.y += self.tick/175
                if self.rect.y < 400:
                    t = self.tick/2
                    if t != 0:
                        self.rect.y += (400-self.rect.y)/(t)
                    else:
                        self.rect.y = 400
                else:
                    self.rect.y = 400
            else:
                self.remove()

            if self.rect.right > 0 and \
               self.rect.x < win.get_width() and \
               self.rect.y < win.get_height() and \
               self.rect.bottom > 0:
                s = self.sprite.copy()
                s = pygame.transform.rotate(s,self.rotate)
                # pygame.draw.rect(s,(0,255,0),self.hitbox,2)
                win.blit(s,self.rect)
        def stop(self):
            self.stopped = True
        def resume(self):
            self.stopped = False
        def remove(self):
            arrows.remove(self)
            del self
    arrows = []

    class stamina:
        def __init__(self,rect,value,
                     max_value,fg,bg):
            self.rect = rect
            self.value = value
            self.max_value = max_value
            self.fg,self.bg = fg,bg
            self.surface = pygame.Surface(self.rect.size,pygame.SRCALPHA)
        def draw(self,surface=win):
            if self.value > self.max_value: self.value = self.max_value
            pygame.draw.rect(self.surface,self.bg,[0,0,self.rect.width,self.rect.height],border_radius=7)
            pygame.draw.rect(self.surface,self.fg,[0,0,self.value/self.max_value*self.rect.width,self.rect.height],border_radius=7)
            surface.blit(self.surface,self.rect)
    health_stamina = stamina(
        pygame.Rect(10,10,200,20),
        player.health,player.max_health,
        (30,200,30),(180,180,180))
    shot_delay_stamina = stamina(
        pygame.Rect(10,40,200,20),
        player.shotDelay,player.shotDelay,
        (30,150,200),(180,180,180))

    class mob:
        def __init__(self,rect,hp,sprites,strong,hitbox,flip,falling_y_pos,
                     health_stamina_y_offset=25,hit_width=50,shooter=None):
            self.rect = rect
            self.max_health = hp
            self.health = hp
            self.shotSprites = sprites
            self.flip = 0
            for n,v in enumerate(self.shotSprites):
                self.shotSprites[n]=pygame.transform.scale(v,self.rect.size)
                if flip:self.shotSprites[n]=pygame.transform.flip(self.shotSprites[n],1,0)
            self.idleSprite = self.shotSprites[0]
            self.strong = strong
            self.hitbox = hitbox
            self.falling_y_pos = falling_y_pos
            self.is_falling = True
            self.falling_speed = 25
            self.hiding_speed = 25
            self.health_stamina = stamina(pygame.Rect(hitbox.x+(hitbox.width/2-100),
                health_stamina_y_offset,200,20),hp,hp,(30,200,30),(180,180,180))
            self.surface = pygame.Surface(rect.size,pygame.SRCALPHA)
            self.hit_ticks = 0
            self.hit_width = hit_width
            self.is_hitting = False
            self.hit_count = 0
            self.shooter = shooter
            self.speed = 1280/(self.hit_width*2+player.rect.width)/2
        def draw(self,lfps):
            self.health_stamina.value = self.health

            surf = pygame.Surface(self.rect.size,pygame.SRCALPHA)
            if self.is_hitting:
                surf.blit(self.shotSprites[int(self.hit_count)],(0,0))
            else:
                surf.blit(self.idleSprite,(0,0))
            if self.flip:surf=pygame.transform.flip(surf,1,0)
            self.health_stamina.draw(surf)

            myhitbox = hitboxToAbsolute(self.rect,self.hitbox)

            for i in arrows:
                if hitboxToAbsolute(i.rect,i.hitbox).colliderect(myhitbox):
                    i.remove()
                    self.health -= i.strong

            myhitbox.x -= self.hit_width
            myhitbox.width += self.hit_width*2

            phb = hitboxToAbsolute(player.rect,player.hitbox)

            if self.is_hitting:
                self.hit_count += 0.3
                if self.hit_count >= len(self.shotSprites):
                    self.hit_count = 0
                    if self.shooter == None:
                        player.setHealth(player.health-self.strong)
                        self.hit_ticks = 60
                    else:
                        self.shooter.shot(self.rect.center,phb.center,self.strong)
                    self.hit_ticks = 60
                    self.is_hitting = False

            if self.hit_ticks == 0:
                if phb.colliderect(myhitbox) or (self.shooter != None and self.shooter.is_farsighted):
                    self.is_hitting = True
            else:
                self.hit_ticks -= 1

            if self.is_falling:
                self.rect.y += self.falling_speed
                if self.rect.bottom >= self.falling_y_pos:
                    self.rect.bottom = self.falling_y_pos
                    self.is_falling = False
                self.falling_speed = (self.falling_y_pos-self.rect.bottom)/self.falling_speed

            if self.health <= 0:
                self.rect.y += self.hiding_speed
                if self.rect.y >= win.get_height():
                    self.rect.y = win.get_height()
                    self.remove()
                self.hiding_speed = (win.get_height()-self.rect.y)/self.hiding_speed

            if player.rect.center[0] < self.rect.center[0]:
                self.rect.x -= 1
                self.flip = False
            if player.rect.center[0] > self.rect.center[0]:
                self.rect.x += 1
                self.flip = True

            if self.shooter != None:
                self.shooter.draw()

            win.blit(surf,self.rect)
        def remove(self):
            mobs.remove(self)
            del self

    class cherv_mob(mob):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.is_hiding = False
            self.hide_tick = -1
            self.is_showing = False
        def draw(self,lfps):
            if self.is_hitting:
                if self.hit_count >= len(self.shotSprites):
                    self.is_hiding = True

            if self.is_hiding:
                self.rect.y += 5
                if self.rect.y >= win.get_height():
                    self.rect.y = win.get_height()
                    self.hide_tick = 3
                    self.is_hiding = False
                    self.rect.x = random.randint(0,win.get_width()-self.rect.width)
            if self.hide_tick >= 0:
                self.hide_tick -= 60/lfps
                if self.hide_tick < 0:
                    self.is_showing = True
            if self.is_showing:
                self.rect.y -= 5
                if self.rect.bottom <= self.falling_y_pos:
                    self.rect.bottom = self.falling_y_pos
                    self.is_showing = False

            super().draw(lfps)

    class skorpion_mob(mob):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.isJump = False
            self.jumpStep = 0.2
            self.jumpHeight = 6
            self.jumpCount = self.jumpHeight
            self.start_speed = 8
            self.jumped = False
        def draw(self,lfps):
            if self.isJump:
                if self.jumpCount >= -self.jumpHeight:
                    if self.jumpCount < 0:
                        self.rect.y += (self.jumpCount ** 2) / 2
                    else:
                        self.rect.y -= (self.jumpCount ** 2) / 2
                    self.jumpCount -= self.jumpStep
                    self.jumpCount = round(self.jumpCount,1)
                else:
                    self.isJump = False
                    self.jumpCount = self.jumpHeight
                    self.health = 2000
                    self.strong = 370

            if self.health <= 1000 and not self.jumped:
                self.isJump = True
                self.jumped = True

            super().draw(lfps)

    mobs = []

    class meteor:
        def __init__(self,f,image,hitbox,strong,offset):
            pos = list(f)
            pos[0] += offset[0]
            pos[1] += offset[1]
            self.hitbox = hitbox
            self.rect = pygame.Rect(*pos,250,250)
            self.image = pygame.transform.scale(image,self.rect.size)
            self.image = pygame.transform.flip(self.image,1,0)
            self.strong = strong
            self.is_falling = False
            self.startspeed = 10
            self.speed = self.startspeed
            self.height = 350
            self.start_y = pos[1]
            self.start_x = pos[0]
            self.center_y = pos[1]-self.height
            self.removed = False
            self.damaged = False
        def remove(self):
            self.removed = True
        def draw(self):
            if not self.removed:
                if not self.damaged and hitboxToAbsolute(player.rect,player.hitbox
                        ).colliderect(hitboxToAbsolute(self.rect,self.hitbox)):
                    player.setHealth(player.health-self.strong)
                    self.damaged = True

                if not self.is_falling:
                    self.rect.y -= self.speed
                    self.speed = (self.rect.y-self.center_y)/self.speed
                    if self.rect.y <= self.center_y:
                        self.rect.y = self.center_y
                        self.speed = self.startspeed
                        self.is_falling = True
                else:
                    self.rect.y += self.speed
                    self.speed = (self.start_y-self.rect.y)/self.speed
                    if self.rect.y >= self.start_y:
                        self.remove()
                self.rect.x -= 10

                win.blit(self.image,self.rect)

    class meteor_shooter:
        def __init__(self,image,size,hitbox,offset):
            self.offset = offset
            self.image = pygame.transform.scale(image,size)
            self.hitbox = hitbox # pygame.Rect(0,29,165,69)
            self.meteors = []
            self.is_farsighted = True
        def shot(self,f,t,strong):
            self.meteors.append(meteor(f,self.image,self.hitbox,strong,self.offset))
        def draw(self):
            n = self.meteors
            for v in n:
                if not v.removed:
                    v.draw()
                    continue
                self.meteors.remove(v)

    class needle:
        def __init__(self,f,t,image,hitbox,strong):
            self.strong = strong
            self.f,self.t = f,t
            self.pos = list(f)
            self.removed = False
            self.hitbox = hitbox
            self.image = image.convert_alpha()
            self.speed = 10
            self.a = 255
            self.damaged = False
        def remove(self):
            self.removed = True
        def draw(self):
            if not self.removed:
                s = self.image.copy()

                if self.t[0] < self.pos[0]:
                    self.pos[0] -= (self.pos[0]-self.t[0])/self.speed
                if self.t[0] > self.pos[0]:
                    self.pos[0] += (self.t[0]-self.pos[0])/self.speed
                if self.t[1] < self.pos[1]:
                    self.pos[1] -= (self.pos[1]-self.t[1])/self.speed
                if self.t[1] > self.pos[1]:
                    self.pos[1] += (self.t[1]-self.pos[1])/self.speed
                self.a -= 0.5

                if self.pos[0] == self.t[0] and self.pos[1] == self.t[1]:
                    self.pos = list(self.t)
                    self.remove()
                if self.a <= 0:
                    self.remove()

                if not self.damaged and hitboxToAbsolute(player.rect,player.hitbox).colliderect(
                    hitboxToAbsolute(pygame.Rect(self.pos,self.image.get_size()),self.hitbox)):
                    player.setHealth(player.health-self.strong)
                    self.damaged = True

                s.set_alpha(self.a)

                # pygame.draw.rect(s,(0,255,0),(0,0,*self.image.get_size()),5)

                win.blit(s,self.pos)

    class needle_shooter:
        def __init__(self,image,size,hitbox):
            self.image = pygame.transform.scale(image,size)
            self.hitbox = hitbox # pygame.Rect(0,29,165,69)
            self.needles = []
            self.is_farsighted = False
        def shot(self,f,t,strong):
            self.needles.append(needle(f,t,self.image,self.hitbox,strong))
        def draw(self):
            n = self.needles
            for v in n:
                if not v.removed:
                    v.draw()
                    continue
                self.needles.remove(v)

    class attack_shooter:
        def __init__(self,image,size,hitbox,offset,one_shot_count=1):
            self.image = pygame.transform.scale(image,size)
            self.one_shot_count = one_shot_count
            self.offset = offset
            self.hitbox = hitbox # pygame.Rect(0,29,165,69)
            self.needles = []
            self.is_farsighted = True
        def shot(self,f,t,strong):
            f = (f[0]+self.offset[0],f[1]+self.offset[1])
            t = (t[0]+self.offset[0],t[1]+self.offset[1])
            if self.one_shot_count > 1:
                for i in range(self.one_shot_count):
                    self.needles.append(needle(
                           (f[0]+(random.randint(0,30)-15),
                            f[1]+(random.randint(0,30)-15)),
                           (t[0]+(random.randint(0,30)-15),
                            t[1]+(random.randint(0,30)-15)),
                           self.image,self.hitbox,strong))
            else:
                self.needles.append(needle(f,t,self.image,self.hitbox,strong))
        def draw(self):
            n = self.needles
            for v in n:
                if not v.removed:
                    v.draw()
                    continue
                self.needles.remove(v)

    class mob_arrow:
        def __init__(self,pos,tick,strong,image,offset,hitbox):
            self.sprite = pygame.transform.flip(
                pygame.transform.scale(
                    util.get_image(image),(500,500)),1,0)
            self.hitbox = pygame.Rect(*hitbox)
            self._sx = pos[0]
            self._yt = 0
            pos = list(pos)
            pos[0] += offset[0]
            pos[1] += offset[1]
            self.rect = pygame.Rect(*pos,500,500)
            self.tick = tick
            self.right = False
            self.rotate = 0
            self.strong = strong
            self.destroy_tick = 120
            self.removed = False
        def remove(self):
            self.removed = True
        def draw(self):
            if not self.removed:
                if self.tick > 0:
                    self.tick -= 5
                    self.rect.x -= self.tick/25
                    self.rotate += self.tick/1500
                    self.hitbox.x -= self.tick/250
                    self.hitbox.y += self.tick/175
                else:
                    self.remove()
                if hitboxToAbsolute(self.rect,self.hitbox).colliderect(
                    hitboxToAbsolute(player.rect,player.hitbox)):
                    player.setHealth(player.health-self.strong)
                    self.remove()

                if self.rect.right > 0 and \
                   self.rect.x < win.get_width() and \
                   self.rect.y < win.get_height() and \
                   self.rect.bottom > 0:
                    s = self.sprite.copy()
                    s = pygame.transform.rotate(s,self.rotate)
                    win.blit(s,self.rect)

    class arrow_shooter:
        def __init__(self,image,offset,hitbox):
            self.offset = offset
            self.hitbox = hitbox
            self.image = image
            self.shots = []
            self.is_farsighted = True
        def shot(self,f,t,strong):
            self.shots.append(mob_arrow(
                f,random.randint(200,400),strong,self.image,
                self.offset,self.hitbox))
        def draw(self):
            n = self.shots
            for v in n:
                if not v.removed:
                    v.draw()
                    continue
                self.shots.remove(v)

    def hitboxToAbsolute(relative_rect,hitbox):
        return pygame.Rect(relative_rect.x+hitbox.x,relative_rect.y+hitbox.y,*hitbox.size)

    class target_aim:
        def __init__(self,rect,hitbox):
            self.final_rect = rect
            self.image = pygame.transform.scale(util.get_image("target-aim.png"),rect.size)
            self.rect = pygame.Rect(rect.x,win.get_height(),*rect.size)
            self.hitbox = hitbox
            self.is_showing = False
            self.is_hiding = False
            self.start_speed = 20
            self.speed = self.start_speed
            self.targeted_arrows = 0
        def show(self):
            self.is_showing = True
        def hide(self):
            self.is_hiding = True
        def draw(self):
            if self.is_showing:
                self.rect.y -= self.speed
                self.speed = (self.final_rect.y-self.rect.y)/self.speed
                if self.rect.y <= self.final_rect.y:
                    self.is_showing = False
                    self.speed = self.start_speed
            if self.is_hiding:
                self.rect.y += self.speed
                self.speed = (win.get_height()-self.rect.y)/self.speed
                if self.rect.y >= win.get_height():
                    self.is_hiding = False
                    self.speed = self.start_speed
            absolute_hitbox = hitboxToAbsolute(self.rect,self.hitbox)
            for i in arrows:
                if hitboxToAbsolute(i.rect,i.hitbox).colliderect(absolute_hitbox):
                    if not i.stopped:
                        i.stop()
                        self.targeted_arrows += 1
                        viv.set_text(f"Try shot to the target ({3-self.targeted_arrows})")
                        if self.targeted_arrows >= 3:
                            i.remove()
                            self.hide()
                            vivSays(translate(24),start_waves)
            win.blit(self.image,self.rect)

    target_aim = target_aim(
        pygame.Rect(1100,450,200,200),
        pygame.Rect(100,30,40,120))

    class viv:
        def __init__(self,text):
            self.rect = pygame.Rect(295,-150,800,50)
            self.font = pygame.font.Font(util.get_path("font.ttf"),20)
            self.is_showing = False
            self.is_hiding = False
            self.hide_callback = lambda:None
            self.show_callback = lambda:None
            self.viv_image = pygame.transform.smoothscale(
                util.get_image("viv.png"),
                (self.rect.height,self.rect.height))
            self.set_text(text)
        def set_text(self,text):
            self.surface = pygame.Surface((self.rect.width+5+self.rect.height,self.rect.height),pygame.SRCALPHA)
            pygame.draw.rect(self.surface,(50,100,170),[0,0,*self.rect.size])
            pygame.draw.rect(self.surface,(70,120,190),[0,0,*self.rect.size],5)
            t = self.font.render(text,1,(220,220,220))
            if t.get_width() > self.rect.width-20:
                t = pygame.transform.smoothscale(t,(self.rect.width-20,t.get_height()))
            self.surface.blit(t,(self.rect.width/2-t.get_width()/2,
                                 self.rect.height/2-t.get_height()/2))
            self.surface.blit(self.viv_image,(self.rect.width+5,0))
        def show(self,callback=lambda:None):
            self.show_callback = callback
            self.is_hiding = False
            self.is_showing = True
        def hide(self,callback=lambda:None):
            self.hide_callback = callback
            self.is_hiding = True
            self.is_showing = False
        def draw(self):
            if self.is_hiding:
                if self.rect.y-1 >= -self.rect.height:
                    self.rect.y -= 1
                else:
                    self.rect.y = -self.rect.height
                    self.is_hiding = False
                    self.hide_callback()
            if self.is_showing:
                if self.rect.y+1 <= 0:
                    self.rect.y += 1
                else:
                    self.rect.y = 0
                    self.is_showing = False
                    self.show_callback()
            win.blit(self.surface,self.rect)

    viv = viv("AD - walk, Space - jump, LBM - shot")
    if level == None:viv.show()

    def vivSays(text,callback=viv.hide):
        def st():
            viv.set_text(text)
            viv.show()
            threading.Timer(len(text)/20,callback).start()
        viv.hide(st)

    def sst():
        nonlocal is_learning
        is_learning = False
        def st():
            viv.set_text("Try shot to the target (3)")
            viv.show()
            target_aim.show()
        viv.hide(st)
        saves.save(level="forest")

    def drevozigl(pos,falling_y_pos,hp=160,strong=15):
        return mob(pygame.Rect(*pos,350,350),hp,
            util.get_sprites("drevozigl"),strong,
            pygame.Rect(14,105,322,140),0,falling_y_pos,70,200)

    def drevopluy(pos,falling_y_pos,hp=150,strong=40):
        return mob(pygame.Rect(*pos,350,350),hp,
                   util.get_sprites("drevopluy"),strong,
                   pygame.Rect(100,70,300,400),0,
                   falling_y_pos,0,400,needle_shooter(
                   util.get_image("needle.png"),(150,150),
                   pygame.Rect(0,20,115,48)))

    def ditya_lesa(pos,falling_y_pos,hp=1200,strong=100):
        return mob(pygame.Rect(*pos,600,540),hp,
                   util.get_sprites("bear"),strong,
                   pygame.Rect(0,100,500,600),1,
                   falling_y_pos,25,300)

    def kentavr(pos,falling_y_pos,hp=300,strong=50):
        return mob(pygame.Rect(*pos,350,350),hp,util.get_sprites("kentavr"),
                   strong,pygame.Rect(140,140,210,189),1,falling_y_pos,25,300,
                   arrow_shooter("kentavr-arrow.png",(-320,-250),[170,250,150,25]))

    def kamnekril(pos,falling_y_pos,hp=700,strong=25):
        return mob(pygame.Rect(*pos,350,350),hp,
                   util.get_sprites("kamnekril"),
                   strong,pygame.Rect(140,140,210,189),
                   1,falling_y_pos,25,300,meteor_shooter(
                   util.get_image("meteor.png"),(500,500),
                   pygame.Rect(0,0,50,50),(-100,-25)))

    def snake(pos,falling_y_pos,hp=80,strong=10):
        return mob(pygame.Rect(*pos,350,350),hp,
                   util.get_sprites("snake"),strong,
                   pygame.Rect(140,171,175,140),1,
                   falling_y_pos,0,400,attack_shooter(
                   util.get_image("snake-attack.png"),(500,500),
                   pygame.Rect(345,295,60,50),(-300,-350)))

    def golem(pos,falling_y_pos,hp=2000,strong=200):
        return mob(pygame.Rect(*pos,600,540),hp,
                   util.get_sprites("golem"),strong,
                   pygame.Rect(120,100,500,600),1,
                   falling_y_pos,25,300)

    def moloh(pos,falling_y_pos,shots=5,hp=500,strong=30):
        return mob(pygame.Rect(*pos,350,350),hp,
                   util.get_sprites("moloh"),strong,
                   pygame.Rect(49,91,245,196),1,
                   falling_y_pos,0,400,attack_shooter(
                   util.get_image("moloh-attack.png"),(500,500),
                   pygame.Rect(200,420,60,50),(-300,-350),shots))

    def cherv(pos,falling_y_pos,hp=350,strong=90):
        return cherv_mob(pygame.Rect(*pos,350,350),hp,
            util.get_sprites("cherv"),strong,
            pygame.Rect(70,84,175,224),1,falling_y_pos,70,200)

    def ogr(pos,falling_y_pos,hp=450,strong=110):
        return mob(pygame.Rect(*pos,350,350),hp,
            util.get_sprites("ogr"),strong,
            pygame.Rect(70,84,175,221),0,
            falling_y_pos,70,200)

    def skorpion(pos,falling_y_pos,hp=4000,strong=30):
        return skorpion_mob(pygame.Rect(*pos,600,540),hp,
                   util.get_sprites("skorpion"),strong,
                   pygame.Rect(120,100,500,600),0,
                   falling_y_pos,25,300)

    def spawn_kentavr():
        nonlocal kentavr_spawned
        kentavr_spawned += 1
        mobs.append(kentavr((750,-500),700))

    def start_waves():
        nonlocal wave
        if scene.get_name() == "forest":
            vivSays(translate(25))
            for i in [500,750,1000]:
                mobs.append(drevozigl((i,-500),760))
            wave = 1
        elif scene.get_name() == "mountains":
            spawn_kentavr()
            wave = 0
        elif scene.get_name() == "desert":
            mobs.append(moloh((750,-500),760))
            wave = 0
            vivSays(translate(35))

    def tlcb(v):
        traders[0].hide()

    def ftrcb(v):
        nonlocal traders,mobs,wave,after_trader,last_stats


        for i in traders:
            i.hide()
        player.setMaxHealth(1300)
        player.setHealth(1300)
        player.strong = 120
        player.type = 2
        player.shotDelay = 0.6
        player.reload_sprites()
        mobs.append(ditya_lesa((500,-700),760))
        wave = 6

    def mtrcb(v):
        nonlocal traders,mobs,wave,after_trader,last_stats

        for i in traders:
            i.hide()
        player.setMaxHealth(1600)
        player.setHealth(1600)
        player.strong = 180
        player.type = 3
        player.speed = 14
        player.reload_sprites()
        mobs.append(golem((500,-700),760))
        vivSays(translate(33))
        wave = 8

    def dtrcb(v):
        nonlocal traders,mobs,wave,after_trader,last_stats

        for i in traders:
            i.hide()
        last_stats = (player.health,player.strong)
        after_trader = True
        player.setMaxHealth(2000)
        player.setHealth(2000)
        player.strong = 200
        player.type = 4
        player.shotDelay = 0.2
        player.reload_sprites()
        mobs.append(skorpion((500,-700),760))
        wave = 9
        vivSays(translate(38))

    def get_background(name):
        return pygame.transform.scale(util.get_image(name+".jpg"),win.get_size())

    moved = [0,0,0]
    wave = levelWave
    traders = []
    shooters = []
    mouse_click_enable = True
    kentavr_tick = 180
    kentavr_spawned = 0
    cherv_tick = 180
    cherv_spawned = 0
    was_scene = None
    after_trader = False
    last_stats = (player.health,player.strong)

    if saves.load("wave") < wave:
        saves.save(wave=wave)

    if level == None:
        scene = scene_manager("forest")
        is_learning = True
    else:
        scene = scene_manager(level)
        is_learning = False
        if wave == 0:
            start_waves()

    if level == "mountains":
        player.setMaxHealth(1300)
        player.setHealth(1300)
        player.strong = 120
        player.type = 2
        player.shotDelay = 0.6
        player.reload_sprites()
    elif level == "desert":
        player.setMaxHealth(1600)
        player.setHealth(1600)
        player.strong = 180
        player.type = 3
        player.speed = 14
        player.reload_sprites()



    # DEBUG

    # is_learning = False
    # scene = "desert"
    # background = get_background(scene)
    # player.setMaxHealth(1000)
    # player.setHealth(1000)
    # player.strong = 120
    # player.type = 3
    # player.reload_sprites()
    # # mobs = [snake((750,-500),700)]
    # def ass():
    #     nonlocal wave
    #     wave = 2
    # scene.set_scene("mountains",ass)

    # DEBUG



    def reload():
        unload()
        start_waves()

    def unload():
        nonlocal wave,traders,shooters,\
               mobs,mouse_click_enable,\
               kentavr_tick,kentavr_spawned,\
               cherv_tick,cherv_spawned,\
               after_trader,last_stats
        wave = 0
        traders = []
        shooters = []
        mobs = []
        mouse_click_enable = True
        kentavr_tick = 180
        kentavr_spawned = 0
        cherv_tick = 180
        cherv_spawned = 0
        if after_trader:
            after_trader = False
            player.setHealth(last_stats[0])
            player.setMaxHealth(last_stats[0])
            player.strong = last_stats[1]

    clock = pygame.time.Clock()

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if scene.name == "death":
                    scene.set_scene(was_scene,reload)
                else:
                    if mouse_click_enable:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                        if event.pos[0] > player.rect.center[0]:
                            player.flip(True)
                            player.shot(event.pos[0]-player.rect.x)
                        else:
                            player.flip(False)
                            player.shot(player.rect.x-event.pos[0])
            if event.type == pygame.MOUSEBUTTONUP:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                player.shotPressedUp = True
        scene.draw_bg()

        if scene.name == "forest":
            if mobs == []:
                if wave == 1:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal wave,mobs
                        for i in [500,600,800,900,1000]:
                            mobs.append(drevozigl((i,-500),760))
                        wave = 2
                        if saves.load("wave") < wave:
                            saves.save(wave=wave)
                    scene.set_scene(scene.name,fws)
                elif wave == 2:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal wave,mobs
                        vivSays(translate(26))
                        for i in [500,750,1000]:
                            mobs.append(drevopluy((i,-500),700))
                        wave = 3
                        if saves.load("wave") < wave:
                            saves.save(wave=wave)
                    scene.set_scene(scene.name,fws)
                elif wave == 3:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal wave,mobs
                        for i in [500,600,800,900,1000]:
                            mobs.append(drevopluy((i,-500),700))
                        wave = 4
                        if saves.load("wave") < wave:
                            saves.save(wave=wave)
                    scene.set_scene(scene.name,fws)
                elif wave == 4:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal wave,traders
                        t = trader(pygame.Rect(800,400,250,250),
                                   util.get_image("forest-trader.png"),
                                   translate(3),
                                   [translate(4),
                                    translate(5),
                                    translate(6),
                                    translate(7)],
                                   0,ftrcb,tlcb)
                        t.show_only_me()
                        def foo2():
                            vivSays(translate(32))
                            player.say(translate(2),t.show_only_quiz)
                        t.say("\n".join(textwrap.wrap(translate(1),30)),foo2)
                        traders.append(t)
                        wave = 5
                        if saves.load("wave") < wave:
                            saves.save(wave=wave)
                    scene.set_scene(scene.name,fws)
                elif wave == 6:
                    scene.set_scene("mountains",start_waves)
                    saves.save(level="mountains",wave=6)
        elif scene.name == "mountains":
            if mobs == []:
                if wave == 1:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal wave,mobs
                        for i in [500,800]:
                            mobs.append(kamnekril((i,-500),700))
                        wave = 2
                        saves.save(wave=7)
                        vivSays(translate(28))
                    scene.set_scene(scene.name,fws)
                elif wave == 2:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [475,600,760,850]:
                            mobs.append(kamnekril((i,-500),700))
                        wave = 3
                        saves.save(wave=5+wave)
                        vivSays(translate(29))
                    scene.set_scene(scene.name,fws)
                elif wave == 3:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [475,500,600,650,760,760,850]:
                            mobs.append(snake((i,-500),760))
                        wave = 4
                        saves.save(wave=5+wave)
                    scene.set_scene(scene.name,fws)
                elif wave == 4:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [475,550,600,650,760,760,850]:
                            mobs.append(snake((i,-500),760))
                        wave = 5
                        saves.save(wave=5+wave)
                        vivSays(translate(30),lambda:vivSays(translate(31),4))
                    scene.set_scene(scene.name,fws)
                elif wave == 5:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [475,550,600,650,760,760,850]:
                            mobs.append(snake((i,-500),760))
                        wave = 6
                        saves.save(wave=5+wave)
                    scene.set_scene(scene.name,fws)
                elif wave == 6:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal traders,wave
                        t = trader(pygame.Rect(800,400,272,408),
                                   util.get_image("mountains-trader.png"),
                                   translate(10),
                                   [translate(11),
                                    translate(12),
                                    translate(13),
                                    translate(14)],
                                   1,mtrcb,tlcb)
                        def foo():
                            player.say("\n".join(textwrap.wrap(translate(9),30)),t.show_only_quiz)
                        t.say("\n".join(textwrap.wrap(translate(8),30)),foo)
                        t.show_only_me()
                        traders.append(t)
                        wave = 7
                        saves.save(wave=5+wave)
                    scene.set_scene(scene.name,fws)
                elif wave == 8:
                    scene.set_scene("desert",start_waves)
                    saves.save(level="desert",wave=5+8)

            if wave == 0:
                if kentavr_spawned < 9:
                    kentavr_tick -= 1
                    if kentavr_tick <= 0:
                        kentavr_tick = 180
                        spawn_kentavr()
                else:
                    wave = 1
        elif scene.name == "desert":
            if mobs == []:
                if wave == 0:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [475,550,600,650,760,760,850,860,870,880]:
                            mobs.append(moloh((i,-500),760,1))
                        vivSays(translate(36))
                        wave = 1
                        saves.save(wave=14)
                    scene.set_scene(scene.name,fws)
                elif wave == 1:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [500,750,1000]:
                            mobs.append(cherv((i,-500),760))
                        wave = 2
                        saves.save(wave=15)
                    scene.set_scene(scene.name,fws)
                elif wave == 3:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [500,600,800,900,1000]:
                            mobs.append(ogr((i,-500),760))
                        wave = 4
                        saves.save(wave=17)
                    scene.set_scene(scene.name,fws)
                elif wave == 4:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [500,600,800,900,1000]:
                            mobs.append(ogr((i,-500),760))
                        wave = 5
                        saves.save(wave=18)
                    scene.set_scene(scene.name,fws)
                elif wave == 5:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [400,500,600,800,900,1000]:
                            mobs.append(ogr((i,-500),760))
                        wave = 6
                        saves.save(wave=19)
                    scene.set_scene(scene.name,fws)
                elif wave == 6:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal mobs,wave
                        for i in [475,550,600,650,700,760,850]:
                            mobs.append(ogr((i,-500),760))
                        wave = 7
                        saves.save(wave=20)
                    scene.set_scene(scene.name,fws)
                elif wave == 7:
                    player.setHealth(player.max_health)
                    def fws():
                        nonlocal traders,wave
                        t = trader(pygame.Rect(800,400,272,408),
                                   util.get_image("desert-trader.png"),
                                   translate(19),
                                   [translate(20),
                                    translate(21),
                                    translate(22),
                                    translate(23)],
                                   3,dtrcb,tlcb)
                        def foo1():
                            def foo2():
                                def foo3():
                                    def foo4():
                                        vivSays(translate(37))
                                        t.show_only_quiz()
                                    player.say(translate(18),foo4)
                                t.say("\n".join(textwrap.wrap(translate(17),15)),foo3)
                            player.say(translate(16),foo2)
                        t.say(translate(15),foo1)
                        t.show_only_me()
                        traders.append(t)
                        wave = 8
                        saves.save(wave=22)
                    scene.set_scene(scene.name,fws)
                elif wave == 9:
                    import end
                    end.main()
                    sys.exit()
            if wave == 2:
                if cherv_spawned < 10:
                    cherv_tick -= 1
                    if cherv_tick <= 0:
                        cherv_tick = 180
                        mobs.append(cherv((random.randint(500,1000),-500),random.randint(600,700)))
                        cherv_spawned += 1
                else:
                    wave = 3

        lfps = clock.get_fps()
        if lfps == 0: lfps = 0.1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] or keys[pygame.K_w]:
            player.move(True,lfps)
            if is_learning:
                if not moved[1]:moved[1]=1
                if moved==[1,1,1]:sst()
        if keys[pygame.K_a] or keys[pygame.K_s]:
            player.move(False,lfps)
            if is_learning:
                if not moved[0]:moved[0]=1
                if moved==[1,1,1]:sst()
        if keys[pygame.K_SPACE]:
            player.jump()
            if is_learning:
                if not moved[2]:moved[2]=1
                if moved==[1,1,1]:sst()
        if keys[pygame.K_F11]:
            pygame.display.toggle_fullscreen()
        if keys[pygame.K_F3]:
            t = font.render(" "+scene.name+" "+str(wave)+" ",1,(0,255,0),(0,0,0))
            win.blit(t,(0,win.get_height()-t.get_height()))

        if level==None and scene.name=="forest":target_aim.draw()
        for i in arrows:i.draw(lfps)

        player.draw()

        for i in mobs:i.draw(lfps)
        for i in traders:i.draw()

        health_stamina.draw()
        shot_delay_stamina.draw()

        viv.draw()

        scene.draw_trans()

        # win.blit(font.render(f"{round(lfps,2)} FPS",1,(0,255,0)),(0,0))
        menu.draw(events)

        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()

if __name__ == '__main__':
    main("mountains",0)
