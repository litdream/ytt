#!/usr/bin/env python2

import sys
import pygame
import random
import copy
import time
from const import *
from keyboard import *

# Alice in Wonderland were from gutenberg.org.
#   https://www.gutenberg.org/ebooks/28885

class WordLine(pygame.sprite.Sprite):
    def __init__(self, font, color, line):
        pygame.sprite.Sprite.__init__(self)
        self.line = line
        self.font = font
        self.image = self.font.render( self.line, True, color)
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 280
        self.target_y = 250
        
    def update(self):
        while self.rect.y > self.target_y:
            self.rect.y -= 5

    def move_up(self):
        self.target_y -= 100

        
class UserLine(pygame.sprite.Sprite):
    def __init__(self, font):
        self.font = font

    def match_render(self, userlist, linelist):
        pass
        
font_size=18
font = None
def set_font():
    font = None
    if 'freemono' in pygame.font.get_fonts():
        # Linux
        font = pygame.font.SysFont("freemono", font_size)
    elif 'menlo' in pygame.font.get_fonts():
        # Apple
        font = pygame.font.SysFont("menlo", font_size)
    else:
        # Windows
        font = pygame.font.SysFont("consolas", font_size)
    return font

def get_xoffset():
    if 'freemono' in pygame.font.get_fonts():
        # linux
        return font_size/2
    elif 'menlo' in pygame.font.get_fonts():
        # apple
        return font_size/2 + 2
    else:
        # windows
        return font_size/2 + 1
    
def render_userinput( cur, user ):
    global font
    if not font:
        font = set_font()

    screen = pygame.display.get_surface()
    tx,ty = 10,180
    for i, c in enumerate(user):
        if cur[i] == c:
            text = font.render(c, True, GREEN)
        else:
            text = font.render(c, True, RED)            
        screen.blit(text, (tx, ty))
        tx+= get_xoffset()
    
def load_line(lst, line_length=None):
    if line_length is None:
        if sys.platform.startswith('linux'):
            line_length = 42
        elif sys.platform == 'darwin':
            line_length = 45
        else:
            line_length = 50
    
    rtn = list()
    while lst and line_length > len(' '.join(rtn)):
        rtn.append(lst.pop())
    if line_length > len(' '.join(rtn)):
        lst.append(rtn.pop())
    return rtn

def main_screen(fname):
    arr = list()
    with open(fname) as fh:
        for l in fh:
            if len(l.strip()) == 0: continue
            arr += l.strip().split()
    arr.reverse()

    screen = pygame.display.set_mode((600,600))
    allSprites = pygame.sprite.Group()
    keyimg = RealKeyboard()
    allSprites.add(keyimg)
    articleSprites = pygame.sprite.Group()
    
    done = False
    pressed_key = None
    clock = pygame.time.Clock()
    user = list()

    i = 0
    leave_key = None

    typed_line = None
    cur_line = ' '.join(load_line(arr)) + " "
    next_line = ' '.join(load_line(arr)) + " "

    user_line = list()
    global font
    if not font:
        font = set_font()
    # TEST
    l = WordLine(font,  WHITE, cur_line)
    l.move_up()
    allSprites.add(l)
    articleSprites.add(l)
    
    l2 = WordLine(font, WHITE, next_line)
    allSprites.add(l2)
    articleSprites.add(l2)
    idx = 0
    leave_key = None
    
    while not done:
        screen.fill(BLACK)
        #
        # Event handle
        #
        shifted = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                # TODO:
                #   Move back up, rather than quit.
                if event.key == pygame.K_q and ( event.mod & pygame.KMOD_LCTRL ):
                    pygame.quit()
                if event.mod & pygame.KMOD_SHIFT:
                    shifted = True
                pressed_key = get_key_pressed(event)

                # Early Sound Feedback
                if pressed_key == '\b':
                    if user:
                        load_and_play('key_press.ogg')
                        user.pop()
                        idx -= 1
                elif pressed_key in ( 'SHIFT', 'CTRL', 'ALT' ):
                    pass
                else:
                    if shifted:
                        if pressed_key.isupper():
                            pressed_key = pressed_key.lower()
                        elif pressed_key.islower():
                            pressed_key = pressed_key.upper()
                        else:
                            pass
                    
                    if pressed_key == cur_line[idx]:
                        load_and_play('key_press.ogg')
                        user.append(pressed_key)
                        leave_key = None
                    else:
                        load_and_play('pig-oink.ogg')
                        user.append(pressed_key)
                        leave_key = pressed_key
                    idx += 1
        allSprites.update()
        allSprites.draw(screen)
        render_userinput( cur_line, user )
        
        if cur_line == ''.join(user):
            # Scrolling
            cur_line = next_line
            next_line = ' '.join(load_line(arr)) + " "

            for linesprite in articleSprites:
                linesprite.move_up()
            linesprite = WordLine(font, WHITE, next_line)
            allSprites.add(linesprite)
            articleSprites.add(linesprite)

            for sp in articleSprites:
                if sp.rect.y < 0:
                    allSprites.remove(sp)
                    articleSprites.remove(sp)
            user = list()
            idx = 0
        clock.tick(90)
        pygame.display.flip()    
        done = ( len(cur_line.strip()) == 0 )

        
def main_loop():
    global score
    pygame.init()
    pygame.display.set_caption(TITLE)

    #article="alice.txt"
    article = "godey.txt"
    main_screen(article)
    pygame.quit()
    
if __name__ == '__main__':
    main_loop()