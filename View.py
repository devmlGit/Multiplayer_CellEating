import pygame
from Constants import *



def drawScene(screen, currCellId, cellMap, foodList):
    
    screen.fill((255,255,255))
    
    gridPos_x = SCREEN_WIDTH/2 - cellMap[currCellId].x
    gridPos_y = SCREEN_HEIGHT/2 - cellMap[currCellId].y

    # Grid borders
    pygame.draw.rect(screen, (10, 10, 10), (gridPos_x, gridPos_y, GRID_WIDTH, GRID_HEIGHT),3)

    # Food
    for lin in range(NBHOR_FOODBOX):
        for col in range(NBVERT_FOODBOX):
            for food in foodList[lin][col]:
                food.Draw(screen, gridPos_x, gridPos_y)

    # Draw cells
    for cell in cellMap.values():
        if gridPos_x +cell.x + cell.radius >= 0 and gridPos_x +cell.x-cell.radius <= SCREEN_WIDTH\
            and gridPos_y +cell.y + cell.radius >= 0 and gridPos_y +cell.y-cell.radius <= SCREEN_HEIGHT:
            cell.drawCell(screen, gridPos_x, gridPos_y)


    pygame.display.update()

def drawEnd(screen):
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    s.set_alpha(180)
    s.fill((0,0,0))
    screen.blit(s,(0,0))

    text = "Happy Birthday Hanâ!"
    font = pygame.font.Font('freesansbold.ttf',35)
    textSurf = font.render(text, True, (255,255,255))
    textRect = textSurf.get_rect()
    textRect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)
    screen.blit(textSurf, textRect)

    text = "Tap the screen to restart"
    font = pygame.font.Font('freesansbold.ttf',20)
    textSurf = font.render(text, True, (255,255,255))
    textRect = textSurf.get_rect()
    textRect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)
    screen.blit(textSurf, textRect)
    
    pygame.display.update()




        