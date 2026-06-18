import json
import os

import pygame
from bubble import Bubble
from effects import OceanBackground
from hand_tracking import HandTracker
from particles import Particle
from settings import *


pygame.init()
fullscreen=False
screen=pygame.display.set_mode((WIDTH,HEIGHT))
game_surface=pygame.Surface((WIDTH,HEIGHT))
pygame.display.set_caption('Ocean Bubble')
clock=pygame.time.Clock()

font=pygame.font.SysFont('arial',30)
small=pygame.font.SysFont('arial',22)
big=pygame.font.SysFont('arial',76,True)
title_font=pygame.font.SysFont('arial',92,True)
button_font=pygame.font.SysFont('arial',26,True)

os.makedirs(DATA_DIR,exist_ok=True)
highscore_file=os.path.join(DATA_DIR,HIGHSCORE_FILE)


def load_highscore():
    if not os.path.exists(highscore_file):
        save_highscore(0)
    with open(highscore_file,'r') as file:
        return json.load(file).get('highscore',0)


def save_highscore(value):
    with open(highscore_file,'w') as file:
        json.dump({'highscore':value},file)


def draw_center(text,font_obj,y,color=(255,255,255)):
    image=font_obj.render(text,True,color)
    game_surface.blit(image,(WIDTH//2-image.get_width()//2,y))


def draw_panel(rect,alpha=70):
    panel=pygame.Surface((rect.width,rect.height),pygame.SRCALPHA)
    pygame.draw.rect(panel,(12,39,68,alpha),(0,6,rect.width,rect.height-6),border_radius=22)
    pygame.draw.rect(panel,(32,116,154,alpha),(0,0,rect.width,rect.height-6),border_radius=22)
    pygame.draw.rect(panel,(190,245,255,95),(0,0,rect.width,rect.height-6),3,border_radius=22)
    game_surface.blit(panel,rect)


def draw_button(rect,label,mouse_pos):
    hover=rect.collidepoint(mouse_pos)
    shadow=pygame.Rect(rect.x,rect.y+5,rect.width,rect.height)
    pygame.draw.rect(game_surface,(8,42,64),shadow,border_radius=18)
    color=(255,210,96) if hover else (72,218,235)
    edge=(255,245,190) if hover else (202,255,255)
    pygame.draw.rect(game_surface,color,rect,border_radius=18)
    pygame.draw.rect(game_surface,edge,rect,3,border_radius=18)
    text=button_font.render(label,True,(18,50,70))
    game_surface.blit(text,(rect.centerx-text.get_width()//2,rect.centery-text.get_height()//2-1))


def button_pressed(rect,cursor,mouse_pos,mouse_clicked,hand_clicked):
    return (mouse_clicked and rect.collidepoint(mouse_pos)) or (hand_clicked and cursor and rect.collidepoint(cursor))


def toggle_fullscreen():
    global screen,fullscreen
    fullscreen=not fullscreen
    if fullscreen:
        info=pygame.display.Info()
        screen=pygame.display.set_mode((info.current_w,info.current_h),pygame.FULLSCREEN)
    else:
        screen=pygame.display.set_mode((WIDTH,HEIGHT))


def to_game_pos(pos):
    if not fullscreen:
        return pos
    sw,sh=screen.get_size()
    scale=min(sw/WIDTH,sh/HEIGHT)
    ox=(sw-WIDTH*scale)/2
    oy=(sh-HEIGHT*scale)/2
    return ((pos[0]-ox)/scale,(pos[1]-oy)/scale)


def present():
    if fullscreen:
        sw,sh=screen.get_size()
        scale=min(sw/WIDTH,sh/HEIGHT)
        scaled=(int(WIDTH*scale),int(HEIGHT*scale))
        x=(sw-scaled[0])//2
        y=(sh-scaled[1])//2
        screen.fill((0,10,22))
        screen.blit(pygame.transform.smoothscale(game_surface,scaled),(x,y))
    else:
        screen.blit(game_surface,(0,0))
    pygame.display.flip()


def bubble_limits(score):
    max_bubbles=min(MAX_ACTIVE_BUBBLES,START_ACTIVE_BUBBLES+score//BUBBLE_SCORE_STEP)
    spawn_delay=max(MIN_SPAWN_MS,SPAWN_MS-score*SPAWN_SCORE_ACCEL)
    return max_bubbles,spawn_delay


def draw_hud(score,high,lives,misses):
    draw_panel(pygame.Rect(18,16,318,106),104)
    pygame.draw.circle(game_surface,(255,218,93),(55,56),25)
    pygame.draw.circle(game_surface,(255,244,173),(48,48),8)
    game_surface.blit(font.render(f'{score}',True,(255,255,255)),(91,25))
    game_surface.blit(small.render(f'Best  {high}',True,(198,246,255)),(92,68))

    for i in range(START_LIVES):
        color=(255,92,112) if i<lives else (70,85,102)
        pygame.draw.circle(game_surface,color,(WIDTH-42-i*34,38),11)

    bar_width=160
    x=WIDTH-bar_width-30
    y=70
    pygame.draw.rect(game_surface,(25,67,91),(x,y,bar_width,12),border_radius=6)
    fill=int(bar_width*(misses/MISSES_PER_LIFE))
    pygame.draw.rect(game_surface,(255,194,82),(x,y,fill,12),border_radius=6)


def draw_hand_cursor(cursor,closed,visible,pulse):
    if not cursor:
        return
    x=int(cursor[0])
    y=int(cursor[1])
    t=min(1,pulse/HAND_ANIM_MS)
    squash=1+(0.22*t if closed else -0.10*t)
    color=(255,198,98) if closed else (255,226,155)
    outline=(74,47,68)
    glow=(255,220,100,80) if closed else (95,235,255,80)

    aura=pygame.Surface((110,110),pygame.SRCALPHA)
    pygame.draw.circle(aura,glow,(55,55),34 if closed else 42,4)
    game_surface.blit(aura,(x-55,y-55))

    if closed:
        pygame.draw.circle(game_surface,outline,(x,y),24)
        pygame.draw.circle(game_surface,color,(x,y),21)
        pygame.draw.ellipse(game_surface,(255,235,170),(x-16,y-20,18,12))
        pygame.draw.ellipse(game_surface,(255,235,170),(x-1,y-21,18,12))
        pygame.draw.circle(game_surface,outline,(x+19,y+11),13)
        pygame.draw.circle(game_surface,color,(x+18,y+10),10)
    else:
        palm=pygame.Rect(x-20,y-4,int(40*squash),35)
        pygame.draw.ellipse(game_surface,outline,palm.inflate(7,7))
        pygame.draw.ellipse(game_surface,color,palm)
        for offset,height in [(-26,42),(-10,50),(6,48),(22,38)]:
            finger=pygame.Rect(x+offset,y-height,14,height)
            pygame.draw.rect(game_surface,outline,finger.inflate(6,6),border_radius=8)
            pygame.draw.rect(game_surface,color,finger,border_radius=8)
        thumb=[(x-20,y+4),(x-48,y-9),(x-39,y+15),(x-21,y+20)]
        pygame.draw.polygon(game_surface,outline,thumb)
        pygame.draw.polygon(game_surface,color,[(x-20,y+7),(x-43,y-7),(x-35,y+12),(x-20,y+17)])

    if not visible:
        label=small.render('mouse',True,(210,245,255))
        game_surface.blit(label,(x-label.get_width()//2,y+42))


def reset_game():
    return {
        'bubbles':[],
        'particles':[],
        'score':0,
        'lives':START_LIVES,
        'misses':0,
        'spawn':0,
        'state':'title',
        'pulse':0,
        'hand_closed':False,
        'hand_anim':120,
    }


high=load_highscore()
tracker=HandTracker()
ocean=OceanBackground(WIDTH,HEIGHT)
game=reset_game()

run=True
while run:
    dt=clock.tick(FPS)
    game['pulse']+=dt
    mouse_pos=to_game_pos(pygame.mouse.get_pos())
    mouse_pressed=pygame.mouse.get_pressed()[0]
    clicked=False

    buttons={
        'resume':pygame.Rect(WIDTH//2-135,322,270,52),
        'restart':pygame.Rect(WIDTH//2-135,388,270,52),
        'quit':pygame.Rect(WIDTH//2-135,454,270,52),
    }

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            clicked=True
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                if game['state']=='playing':
                    game['state']='paused'
                elif game['state']=='paused':
                    game['state']='playing'
                else:
                    run=False
            if event.key==pygame.K_p and game['state'] in ('playing','paused'):
                game['state']='paused' if game['state']=='playing' else 'playing'
            if event.key==pygame.K_r and game['state'] in ('playing','paused','game_over'):
                game=reset_game()
                game['state']='playing'
            if event.key==pygame.K_q:
                run=False
            if event.key==pygame.K_F11:
                toggle_fullscreen()
            if event.key==pygame.K_m:
                pygame.display.iconify()
            if event.key in (pygame.K_SPACE,pygame.K_RETURN):
                if game['state'] in ('title','game_over'):
                    game=reset_game()
                    game['state']='playing'
                elif game['state']=='paused':
                    game['state']='playing'

    ocean.draw(game_surface)

    cursor,fist,hand_visible=tracker.update(WIDTH,HEIGHT)
    if not cursor:
        cursor=mouse_pos
    popping=fist or (mouse_pressed and not hand_visible)
    hand_clicked=hand_visible and popping and not game['hand_closed']
    if game['hand_closed']!=popping:
        game['hand_closed']=popping
        game['hand_anim']=0
    else:
        game['hand_anim']+=dt

    if game['state']=='title':
        draw_center('OCEAN BUBBLE',title_font,190,(245,255,255))
        draw_center('Pop bubbles with a fist or mouse click',font,304,(185,235,255))
        alpha=160+int(70*abs(pygame.math.Vector2(1,0).rotate(game['pulse']*0.12).x))
        start_button=pygame.Rect(WIDTH//2-165,398,330,58)
        glow=pygame.Surface((start_button.width+36,start_button.height+24),pygame.SRCALPHA)
        pygame.draw.rect(glow,(75,210,255,alpha),(0,0,glow.get_width(),glow.get_height()),border_radius=28)
        game_surface.blit(glow,(start_button.x-18,start_button.y-12))
        draw_button(start_button,'Start Game',cursor)
        if button_pressed(start_button,cursor,mouse_pos,clicked,hand_clicked):
            game=reset_game()
            game['state']='playing'
        draw_hand_cursor(cursor,popping,hand_visible,game['hand_anim'])

    elif game['state']=='playing':
        game['spawn']+=dt
        max_bubbles,spawn_delay=bubble_limits(game['score'])
        if game['spawn']>spawn_delay and len(game['bubbles'])<max_bubbles:
            game['bubbles'].append(Bubble(WIDTH,HEIGHT,game['score']))
            game['spawn']=0

        for bubble in game['bubbles'][:]:
            bubble.update(dt)
            bubble.draw(game_surface)

            if bubble.reached_top():
                game['bubbles'].remove(bubble)
                game['misses']+=1
                if game['misses']>=MISSES_PER_LIFE:
                    game['misses']=0
                    game['lives']-=1
                continue

            if cursor and hand_clicked:
                dx=bubble.x-cursor[0]
                dy=bubble.y-cursor[1]
                if (dx*dx+dy*dy)**0.5 < bubble.radius+BUBBLE_HIT_PADDING:
                    game['bubbles'].remove(bubble)
                    game['score']+=1
                    high=max(high,game['score'])
                    for _ in range(22):
                        game['particles'].append(Particle(bubble.x,bubble.y))

        for particle in game['particles'][:]:
            particle.update(dt)
            particle.draw(game_surface)
            if not particle.alive():
                game['particles'].remove(particle)

        draw_hand_cursor(cursor,popping,hand_visible,game['hand_anim'])
        draw_hud(game['score'],high,game['lives'],game['misses'])
        pause_button=pygame.Rect(WIDTH-74,24,50,44)
        draw_button(pause_button,'II',cursor)
        if button_pressed(pause_button,cursor,mouse_pos,clicked,hand_clicked):
            game['state']='paused'

        if game['lives']<=0:
            game['state']='game_over'

    elif game['state']=='paused':
        for bubble in game['bubbles']:
            bubble.draw(game_surface)
        for particle in game['particles']:
            particle.draw(game_surface)
        draw_hud(game['score'],high,game['lives'],game['misses'])
        overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        overlay.fill((3,18,32,112))
        game_surface.blit(overlay,(0,0))
        draw_panel(pygame.Rect(WIDTH//2-245,198,490,410),104)
        draw_center('PAUSED',big,228,(255,255,255))
        draw_button(buttons['resume'],'Resume',cursor)
        draw_button(buttons['restart'],'Restart',cursor)
        draw_button(buttons['quit'],'Quit',cursor)
        window_full=pygame.Rect(WIDTH//2-220,548,210,46)
        window_min=pygame.Rect(WIDTH//2+10,548,210,46)
        draw_button(window_full,'Fullscreen',cursor)
        draw_button(window_min,'Minimize',cursor)
        if clicked or hand_clicked:
            if button_pressed(buttons['resume'],cursor,mouse_pos,clicked,hand_clicked):
                game['state']='playing'
            elif button_pressed(buttons['restart'],cursor,mouse_pos,clicked,hand_clicked):
                game=reset_game()
                game['state']='playing'
            elif button_pressed(buttons['quit'],cursor,mouse_pos,clicked,hand_clicked):
                run=False
            elif button_pressed(window_full,cursor,mouse_pos,clicked,hand_clicked):
                toggle_fullscreen()
            elif button_pressed(window_min,cursor,mouse_pos,clicked,hand_clicked):
                pygame.display.iconify()
        draw_hand_cursor(cursor,popping,hand_visible,game['hand_anim'])

    else:
        for bubble in game['bubbles']:
            bubble.update(dt*0.35)
            bubble.draw(game_surface)
        for particle in game['particles'][:]:
            particle.update(dt)
            particle.draw(game_surface)
            if not particle.alive():
                game['particles'].remove(particle)

        draw_panel(pygame.Rect(WIDTH//2-245,185,490,255),88)
        draw_center('GAME OVER',big,218,(255,255,255))
        draw_center(f'Score  {game["score"]}',font,314,(185,235,255))
        draw_center(f'Best  {high}',font,354,(255,236,150))
        draw_center('Press Space to Try Again',small,405,(230,245,255))
        restart_button=pygame.Rect(WIDTH//2-135,452,270,52)
        quit_button=pygame.Rect(WIDTH//2-135,516,270,52)
        draw_button(restart_button,'Restart',cursor)
        draw_button(quit_button,'Quit',cursor)
        if clicked or hand_clicked:
            if button_pressed(restart_button,cursor,mouse_pos,clicked,hand_clicked):
                game=reset_game()
                game['state']='playing'
            elif button_pressed(quit_button,cursor,mouse_pos,clicked,hand_clicked):
                run=False
        draw_hand_cursor(cursor,popping,hand_visible,game['hand_anim'])

    present()

save_highscore(high)
tracker.release()
pygame.quit()
