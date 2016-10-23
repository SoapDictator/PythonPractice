#Artificial Destiny
#By SoapDictator

import pygame, sys
from pygame.locals import *

FPS = 10
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

class InputManager(object):
	def handleInput(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				self.terminate()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:	self.terminate()
				elif event.key == K_UP:		Movement0.moveStore(TANKARRAY[0], 0, -1)
				elif event.key == K_DOWN:	Movement0.moveStore(TANKARRAY[0], 0, +1)
				elif event.key == K_RIGHT:	Movement0.moveStore(TANKARRAY[0], +1, 0)
				elif event.key == K_LEFT:	Movement0.moveStore(TANKARRAY[0], -1, 0)
				elif event.key == K_e:		Movement0.moveUnit(TANKARRAY[0])
								
	def terminate(self):
		pygame.quit()
		sys.exit()

class DrawingManager(object):
	def __init__(self):
		global FPSCLOCK, DISPLAYSURF, BASICFONT

		pygame.init()
		FPSCLOCK = pygame.time.Clock()
		DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGTH))
		BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
		pygame.display.set_caption('AD')
		
	def screenGrid(self):
		for x in range(0, WINDOWWIDTH, CELLSIZE):	# draw vertical lines
			pygame.draw.line(DISPLAYSURF, LIGHTGRAY, (x, 0), (x, WINDOWHEIGTH))
		for y in range(0, WINDOWHEIGTH, CELLSIZE):	# draw horizontal lines
			pygame.draw.line(DISPLAYSURF, LIGHTGRAY, (0, y), (WINDOWWIDTH, y))
			
	def screenMovement(self):
		for TANK in TANKARRAY:
			toX = TANK.moveQueueX[0] + CELLSIZE/2
			toY = TANK.moveQueueY[0] + CELLSIZE/2
			for num in range(1, len(TANK.moveQueueX)):
				x = toX
				y = toY
				toX += TANK.moveQueueX[num] * CELLSIZE
				toY += TANK.moveQueueY[num] * CELLSIZE
				pygame.draw.line(DISPLAYSURF, RED, (x, y), (toX, toY))
			toX = 0
			toY = 0
					
	def screenRefresh(self):
		DISPLAYSURF.fill(BGCOLOR)
		self.screenGrid()
		self.screenMovement()
		for TANK in TANKARRAY:
			TANK.drawUnit()
		pygame.display.update()
		FPSCLOCK.tick(FPS)
		
class MovementManager(object):
	def moveStore(self, TANK, toX, toY):
		TANK.moveQueueX.append(toX)
		TANK.moveQueueY.append(toY)
		
	def moveUnit(self, TANK):
		for step in range(1, len(TANK.moveQueueX)):
			TANK.coordX += TANK.moveQueueX[step] * CELLSIZE
			TANK.coordY += TANK.moveQueueY[step] * CELLSIZE
			pygame.time.wait(200)
			Window0.screenRefresh()
		TANK.moveQueueX[0] = TANK.coordX
		TANK.moveQueueY[0] = TANK.coordY
		del TANK.moveQueueX[1:len(TANK.moveQueueX)]
		del TANK.moveQueueY[1:len(TANK.moveQueueY)]
						
class Unit(object):
	coordX = 0
	coordY = 0
	statHealth = 0
	statArmor = 0
	statDamage = 0
	
	def createUnit(self):
		pass
		
	def destroyUnit(self):
		pass
	
	def drawUnit(self):
		pass

class Tank(Unit):
	coordX = -1 * CELLSIZE
	coordY = -1 * CELLSIZE
	statHealth = 0
	statArmor = 0
	statDamage = 0
	statSpeed = 5
	arrayPos = 0
	moveQueueX = []
	moveQueueY = []
	
	def createUnit(self, coordX, coordY): # new tank always needs to be the last one in the array
		print("A new tank appears!")
		global ARRAYPOSITION, TANKARRAY
		TANKARRAY.append(self)
		self.arrayPos = ARRAYPOSITION
		ARRAYPOSITION += 1 
		self.coordX = coordX * CELLSIZE
		self.coordY = coordY * CELLSIZE
		self.moveQueueX.append(self.coordX)
		self.moveQueueY.append(self.coordY)
	
	def destroyUnit(self):
		global ARRAYPOSITION, TANKARRAY
		self.coordX = -1 * CELLSIZE #resets the position just in case
		self.coordY = -1 * CELLSIZE
		del TANKARRAY[self.arrayPos]
		for TANK in TANKARRAY: #shifts all tanks so the new tank will be last in the array
			if self.arrayPos > TANK.arrayPos:
				TANK.arrayPos -= 1
		ARRAYPOSITION -= 1
		del self.moveQueueX[0:len(self.moveQueueX)]
		del self.moveQueueY[0:len(self.moveQueueY)]
		print("A tank has been erased!")
	
	def drawUnit(self):
		outerRect = pygame.Rect(self.coordX +1, self.coordY +1, CELLSIZE -1, CELLSIZE -1)
		innerRect = pygame.Rect(self.coordX +5, self.coordY +5, CELLSIZE -9, CELLSIZE -9)
		pygame.draw.rect(DISPLAYSURF, DARKRED, outerRect)
		pygame.draw.rect(DISPLAYSURF, RED, innerRect)
		
class Main(object):
	def __init__(self):
		global Window0, Input0, Movement0
		global MoveUp, MoveDown, MoveRight, MoveLeft
		Window0 = DrawingManager()
		Input0 = InputManager()
		Movement0 = MovementManager()
				
		Bulldozer = Tank()
		Bulldozer.createUnit(1, 1)
		
		while True:
			#TANKARRAY[0].coordX += 1 * CELLSIZE
			#pygame.time.wait(500)
			Input0.handleInput()
			Window0.screenRefresh()
		
	def terminate(self):
		pygame.quit()
		sys.exit()

StartShenanigans = Main()