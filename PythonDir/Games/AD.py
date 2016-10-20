#Artificial Destiny
#By SoapDictator

import pygame, sys
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGTH = 480
CELLSIZE = 20

assert WINDOWWIDTH % CELLSIZE == 0
assert WINDOWHEIGTH % CELLSIZE == 0

CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGTH = int(WINDOWHEIGTH / CELLSIZE)

#             R    G    B
WHITE		= (255, 255, 255)
BLACK		= (  0,	  0,   0)
RED			= (155,   0,   0)
DARKRED		= (255,   0,   0)
GREEN		= (  0, 255,   0)
DARKGREEN	= (  0, 155,   0)
LIGHTGRAY	= (120, 120, 120)
BGCOLOR		= BLACK

TANKARRAY = []
ARRAYPOSITION = 0

class Window(object):
	def __init__(self):
		global FPSCLOCK, DISPLAYSURF, BASICFONT

		pygame.init()
		FPSCLOCK = pygame.time.Clock()
		DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGTH))
		BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
		pygame.display.set_caption('AD')
		
	def drawGrid(self):
		for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
			pygame.draw.line(DISPLAYSURF, LIGHTGRAY, (x, 0), (x, WINDOWHEIGTH))
		for y in range(0, WINDOWHEIGTH, CELLSIZE): # draw horizontal lines
			pygame.draw.line(DISPLAYSURF, LIGHTGRAY, (0, y), (WINDOWWIDTH, y))

	def terminate(self):
		pygame.quit()
		sys.exit()
		

class Unit(object):
	coordX = 0
	coordY = 0
	statHealth = 0
	statArmor = 0
	statDamage = 0
	
	def CreateUnit(self):
		pass
	
	def DrawUnit(self):
		pass
		
	def MoveUnit(self, toX, toY):
		pass

class Tank(Unit):
	coordX = -1 * CELLSIZE
	coordY = -1 * CELLSIZE
	statHealth = 0
	statArmor = 0
	statDamage = 0
	arrayPos = 0
	
	def CreateUnit(self, coordX, coordY): # new tank always needs to be the last one in the array
		print("A new tank appears!")
		global ARRAYPOSITION, TANKARRAY
		TANKARRAY.append(self)
		self.arrayPos = ARRAYPOSITION
		ARRAYPOSITION += 1 
		self.coordX = coordX * CELLSIZE
		self.coordY = coordY * CELLSIZE
	
	def DestroyUnit(self): #problem: if there is only one tank the delete function doesn't work
		global ARRAYPOSITION, TANKARRAY
		self.coordX = -1 * CELLSIZE #resets the position just in case
		self.coordY = -1 * CELLSIZE
		del TANKARRAY[self.arrayPos]
		for TANK in TANKARRAY: #shifts all tanks so the new tank will be last in the array
			if self.arrayPos > TANK.arrayPos:
				TANK.arrayPos -= 1
		ARRAYPOSITION -= 1
		print("A tank has been erased!")
	
	def DrawUnit(self):
		outerRect = pygame.Rect(self.coordX, self.coordY, CELLSIZE, CELLSIZE)
		innerRect = pygame.Rect(self.coordX +4, self.coordY +4, CELLSIZE -8, CELLSIZE -8)
		pygame.draw.rect(DISPLAYSURF, DARKRED, outerRect)
		pygame.draw.rect(DISPLAYSURF, RED, innerRect)
		
	def MoveUnit(self, toX, toY):
		self.coordX += toX * CELLSIZE
		self.coordY += toY * CELLSIZE

class Main(object):
	def __init__(self):
		Window0 = Window()
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					self.terminate()
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						self.terminate()
					elif event.key == K_DOWN:
						TANKARRAY[0].MoveUnit(0, +1)
						TANKARRAY[1].MoveUnit(0, +1)
					elif event.key == K_UP:
						TANKARRAY[0].MoveUnit(0, -1)
					elif event.key == K_RIGHT:
						TANKARRAY[0].MoveUnit(+1, 0)
					elif event.key == K_LEFT:
						TANKARRAY[0].MoveUnit(-1, 0)
					elif event.key == K_d:
						TANKARRAY[1].DestroyUnit()
	
			DISPLAYSURF.fill(BGCOLOR)
			Window0.drawGrid()
			for TANK in TANKARRAY:
				TANK.DrawUnit()
				print(TANK.coordX)
			pygame.display.update()
			FPSCLOCK.tick(FPS)
			
	def checkForKeyPress(self):
		if len(pygame.event.get(QUIT)) > 0:
			self.terminate()

		keyUpEvents = pygame.event.get(KEYUP)
		if len(keyUpEvents) == 0:
			return None
		if keyUpEvents[0].key == K_ESCAPE:
			self.terminate()
		return keyUpEvents[0].key
		
	def terminate(self):
		pygame.quit()
		sys.exit()

Bulldozer = Tank()
Bulldozer.CreateUnit(1, 1)
Blinker = Tank()
Blinker.CreateUnit(3, 1)
Assault = Tank()
Assault.CreateUnit(5, 1)
StartShenanigans = Main()