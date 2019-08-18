import copy
import pygame
from pygame import *
import random

#constants
red = (255, 0, 0)
black = (0, 0, 0)
white = (255, 255, 255)
#neighbour coordinates
neighbours = [[-1,-1],[-1,0],[-1,+1],
              [0,-1],        [0,+1],   
              [+1,-1],[+1,0],[+1,+1],]

class cell(object):
        def __init__(self, ngb, state):
                self.state = state
                self.ngb = 0

#2d array for storing cells
cells = [[i for i in range(50)] for i in range(50)]

#random field generation
def generate():
        print "Generating"
        for y in xrange(50):
                for x in xrange(50):
                        cells[x][y] = cell(0, random.randint(0, 1))
        print "DoneGen"

#neighbour processing
def update():
        global cells2
        #saving this turn's state
        cells2=copy.deepcopy(cells)
        for y in xrange(50):
                for x in xrange(50):
                        cellv2=cells2[x][y]
                        cellv2.ngb=0
                        cellv = cells[x][y]
                        #processing 
                        for i in neighbours:
                                #offsetting neighbour coordinates
                                dy=i[0]+y
                                dx=i[1]+x
                                if dy < 0:
                                        dy = 49
                                if dy > 49:
                                        dy = 0
                                if dx < 0:
                                        dx = 49
                                if dx > 49:
                                        dx = 0
                                if cells2[dx][dy].state==1:
                                        cellv2.ngb+=1
                        #updating field
                        if cellv2.state==1 and 2<=cellv2.ngb<=3:
                                cellv.state=1
                        else:
                                cellv.state=0
                        if cellv2.state==0 and cellv2.ngb==3:
                                cellv.state=1

#main game function        
def play():                
        #initialization
        pygame.init()
        scrn = pygame.display.set_mode((500, 500))
        mainsrf = pygame.Surface((500, 500))
        mainsrf.fill(white)
        generate()
        #game cycle
        while 1:
                #tracking quitting
                for event in pygame.event.get():
                        if event.type == QUIT:
                                pygame.quit()
                                sys.exit()
                #drawing
                for y in xrange(50):
                        for x in xrange(50):
                                if cells[x][y].state==1:
                                        pygame.draw.rect(mainsrf, black, (x*10, y*10, 10, 10))
                                else:
                                        pygame.draw.rect(mainsrf, white, (x*10, y*10, 10, 10))
                update()
                scrn.blit(mainsrf, (0, 0))
                pygame.display.update()



#running the game
if __name__ == "__main__":
                                play()