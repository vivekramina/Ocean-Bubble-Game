import os
import random

import pygame


class OceanBackground:
    def __init__(self,w,h):
        self.w=w; self.h=h
        self.parts=[[random.randint(0,w),random.randint(0,h),random.randint(1,4),random.uniform(10,36)] for _ in range(110)]
        self.light=pygame.Surface((w,h),pygame.SRCALPHA)
        self.tint=pygame.Surface((w,h),pygame.SRCALPHA)
        self.tint.fill((0,42,72,52))
        self.background=self.load_background()

    def load_background(self):
        path=os.path.join('assets','underwater_background.jpg')
        if not os.path.exists(path):
            return None
        image=pygame.image.load(path).convert()
        scale=max(self.w/image.get_width(),self.h/image.get_height())
        size=(int(image.get_width()*scale),int(image.get_height()*scale))
        image=pygame.transform.smoothscale(image,size)
        x=(image.get_width()-self.w)//2
        y=(image.get_height()-self.h)//2
        return image.subsurface((x,y,self.w,self.h)).copy()

    def draw_fallback(self,screen):
        for y in range(self.h):
            depth=y/self.h
            pygame.draw.line(screen,(6,int(72+depth*35),int(125+depth*35)),(0,y),(self.w,y))

    def draw(self,screen):
        tick=pygame.time.get_ticks()*0.001
        if self.background:
            screen.blit(self.background,(0,0))
        else:
            self.draw_fallback(screen)

        self.light.fill((0,0,0,0))
        for i in range(7):
            x=int((i*210+tick*22)% (self.w+260))-150
            points=[(x,0),(x+64,0),(x+250,self.h),(x-95,self.h)]
            pygame.draw.polygon(self.light,(155,245,255,18),points)
        for i in range(10):
            x=int((i*170+tick*36)% (self.w+220))-110
            y=60+i*52
            pygame.draw.arc(self.light,(235,255,255,30),(x,y,210,58),0.1,3.0,2)
        screen.blit(self.light,(0,0))
        screen.blit(self.tint,(0,0))

        for p in self.parts:
            p[1]-=p[3]/120
            p[0]+=random.uniform(-0.12,0.12)
            if p[1]<0:
                p[1]=self.h
                p[0]=random.randint(0,self.w)
            pygame.draw.circle(screen,(205,245,255),(int(p[0]),int(p[1])),p[2],1)
