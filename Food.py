import pygame
from Constants import *
import threading
import time
import random


class Food:
    def __init__(self, lin, col, id):
        self.xmin = (GRID_WIDTH/NBHOR_FOODBOX)*col
        self.xmax = (GRID_WIDTH/NBHOR_FOODBOX)*(col+1)
        self.ymin = (GRID_WIDTH/NBVERT_FOODBOX)*lin
        self.ymax = (GRID_WIDTH/NBVERT_FOODBOX)*(lin+1)

        self.boxheight = GRID_WIDTH/NBHOR_FOODBOX

        self.radius = 5
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.id = id
        self.active = True
        self.x = random.randint(self.xmin, self.xmax)
        self.y = random.randint(self.ymin, self.ymax)



    def Draw(self, screen, gridPos_x, gridPos_y):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x+gridPos_x),int(self.y+gridPos_y)),int(self.radius))
            

    def Respawn(self):
        time.sleep(FOOD_RESPAWN)
        self.active = True
        self.x = random.randint(self.xmin, self.xmax)
        self.y = random.randint(self.ymin, self.ymax)
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))


    def isEaten(self, cell):

        if ((cell.x-self.x)**2+(cell.y-self.y)**2)**0.5+self.radius<cell.radius:
            self.active = False
            thread = threading.Thread(target = self.Respawn)
            thread.daemon = True
            thread.start()
            return True
        return False
