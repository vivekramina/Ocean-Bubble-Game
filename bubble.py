import pygame, random, math

class Bubble:
    def __init__(self,w,h,score=0):
        self.radius=random.randint(25,60)
        self.x=random.randint(self.radius,w-self.radius)
        self.y=h+self.radius
        difficulty=min(1.9,1+score*0.035)
        self.speed=random.uniform(55,115)*difficulty
        self.offset=random.uniform(0,100)
        self.wobble=random.uniform(18,42)
        self.pop_scale=1
    def update(self,dt):
        seconds=dt/1000
        self.y-=self.speed*seconds
        self.x+=math.sin(pygame.time.get_ticks()*0.002+self.offset)*self.wobble*seconds
    def draw(self,screen):
        size=self.radius*2+16
        center=size//2
        s=pygame.Surface((size,size),pygame.SRCALPHA)
        pygame.draw.circle(s,(80,205,255,28),(center,center),self.radius+7)
        for r in range(self.radius,0,-4):
            alpha=max(8,int(46*(r/self.radius)))
            pygame.draw.circle(s,(185,238,255,alpha),(center,center),r)
        pygame.draw.circle(s,(230,255,255,130),(center,center),self.radius,3)
        pygame.draw.circle(s,(80,175,230,65),(center+3,center+4),max(5,self.radius-8),2)
        pygame.draw.arc(s,(255,255,255,185),(center-self.radius+8,center-self.radius+8,self.radius*2-16,self.radius*2-16),3.55,5.25,3)
        pygame.draw.arc(s,(125,225,255,95),(center-self.radius+6,center-self.radius+6,self.radius*2-12,self.radius*2-12),0.2,1.35,2)
        pygame.draw.circle(s,(255,255,255,210),(center-self.radius//3,center-self.radius//3),max(4,self.radius//5))
        pygame.draw.circle(s,(255,255,255,95),(center+self.radius//4,center+self.radius//5),max(2,self.radius//10))
        pygame.draw.ellipse(s,(255,255,255,110),(center-self.radius//2,center-self.radius//2,self.radius//2,self.radius//4))
        screen.blit(s,(self.x-center,self.y-center))
    def reached_top(self):
        return self.y<-self.radius
