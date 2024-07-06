import pygame
from Constants import *
import threading
clock = pygame.time.Clock()

class Cell:
    def __init__(self, id, x, y, radius, lerp = False):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = SPEED_FACTOR/(self.radius)**0.5
        self.id = id
        self.viewradius = self.radius
        if lerp:
            thread = threading.Thread(target = self.LerpRadius)
            thread.daemon = True
            thread.start()
        self.isRunning = True
        self.username =""
        self.bot = False

    def LerpRadius(self):
        while True:
            self.viewradius += (-self.viewradius+self.radius)*0.4
            clock.tick(30)

    def Update(self, x, y):
        self.x = min(max(x,0), GRID_WIDTH)
        self.y = min(max(y,0), GRID_HEIGHT)
        self.speed = SPEED_FACTOR/self.radius
    
    def UpdateRadius(self, radius):
        self.radius =radius
        self.speed= SPEED_FACTOR/self.radius

    def isEaten(self, other):
        if other.id != self.id\
            and ((other.x-self.x)**2+(other.y-self.y)**2)**0.5+self.radius<other.radius:
            return True
        return False


    def drawCell(self, screen, gridPos_x, gridPos_y):
        pygame.draw.circle(screen, (138, 154, 91) if self.bot else (0,0,0), (int(self.x+gridPos_x),int(self.y+gridPos_y)),int(self.viewradius))



