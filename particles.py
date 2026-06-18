import pygame, random

class Particle:
    def __init__(self,x,y):
        self.x=x; self.y=y
        self.dx=random.uniform(-180,180); self.dy=random.uniform(-210,90)
        self.life=random.randint(360,620)
        self.max_life=self.life
        self.radius=random.randint(2,5)
    def update(self,dt):
        seconds=dt/1000
        self.dy+=260*seconds
        self.x+=self.dx*seconds; self.y+=self.dy*seconds
        self.life-=dt
    def draw(self,screen):
        if self.life>0:
            alpha=max(0,min(255,int(210*(self.life/self.max_life))))
            s=pygame.Surface((self.radius*4,self.radius*4),pygame.SRCALPHA)
            pygame.draw.circle(s,(190,235,255,alpha),(self.radius*2,self.radius*2),self.radius)
            screen.blit(s,(self.x-self.radius*2,self.y-self.radius*2))
    def alive(self): return self.life>0
