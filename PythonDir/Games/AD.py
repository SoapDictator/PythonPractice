#Artificial Destiny
#By SoapDictator

import pygame, sys
from pygame.locals import *

class InputManager(object):
	def handleInput(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				self.terminate()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:	self.terminate()
				elif event.key == K_UP:		Unit0.moveStore(0, -1)
				elif event.key == K_DOWN:	Unit0.moveStore(0, +1)
				elif event.key == K_RIGHT:	Unit0.moveStore(+1, 0)
				elif event.key == K_LEFT:	Unit0.moveStore(-1, 0)
				elif event.key == K_e:		Unit0.moveUnit()
								
	def terminate(self):
		pygame.quit()
		sys.exit()

class DrawingManager(object):
	def __init__(self):
		global FPS, WINDOWWIDTH, WINDOWHEIGTH
		global FPSCLOCK, DISPLAYSURF, BASICFONT
		
		self.screenConfig()
		self.screenColors()
		
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
		global TANKARRAY, ARRAYPOSITION
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
	
	def screenConfig(self):
		global FPS, WINDOWWIDTH, WINDOWHEIGTH
		global CELLSIZE, CELLWIDTH, CELLHEIGTH
		FPS = 10
		WINDOWWIDTH = 640
		WINDOWHEIGTH = 480
		CELLSIZE = 20
		
		assert WINDOWWIDTH % CELLSIZE == 0
		assert WINDOWHEIGTH % CELLSIZE == 0

		CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
		CELLHEIGTH = int(WINDOWHEIGTH / CELLSIZE)
	
	def screenColors(self):
		global WHITE, BLACK, BGCOLOR
		global LIGHTGRAY
		global GREEN, RED
		global DARKGREEN, DARKRED
		#             R    G    B
		WHITE		= (255, 255, 255)
		BLACK		= (  0,	  0,   0)
		RED			= (155,   0,   0)
		DARKRED		= (255,   0,   0)
		GREEN		= (  0, 255,   0)
		DARKGREEN	= (  0, 155,   0)
		LIGHTGRAY	= (120, 120, 120)
		BGCOLOR		= BLACK

class MapManager(object):
	def mapGetUnit(self, getX, getY):
		for TANK in TANKARRAY:
			if TANK.coordX == getX & TANK.coordY == getY:
				return TANK
			else:
				return False
				
class UnitManager(object):
	def __init__(self):
		global TANKARRAY, ARRAYPOSITION
		TANKARRAY = []
		ARRAYPOSITION = 0
	
	def unitCreate(self, coordX, coordY): # new tank always needs to be the last one in the array
		global TANKARRAY, ARRAYPOSITION
		print("A new tank appears!")
		NewTank = Tank()
		TANKARRAY.append(NewTank)
		NewTank.arrayPos = ARRAYPOSITION
		ARRAYPOSITION += 1 
		NewTank.coordX = coordX * CELLSIZE
		NewTank.coordY = coordY * CELLSIZE
		NewTank.moveQueueX.append(NewTank.coordX)
		NewTank.moveQueueY.append(NewTank.coordY)
		return NewTank
	
	def unitDestroy(self, Tank):
		global TANKARRAY, ARRAYPOSITION
		Tank.coordX = -1 * CELLSIZE #resets the position just in case
		Tank.coordY = -1 * CELLSIZE
		del TANKARRAY[Tank.arrayPos]
		for TANK in TANKARRAY: #shifts all tanks so the new tank will be last in the array
			if Tank.arrayPos > TANK.arrayPos:
				TANK.arrayPos -= 1
		ARRAYPOSITION -= 1
		del Tank.moveQueueX[0:len(Tank.moveQueueX)]
		del Tank.moveQueueY[0:len(Tank.moveQueueY)]
		print("A tank has been erased!")
		
	def moveStore(self, toX, toY):
		global SELECTEDTANK
		SELECTEDTANK.moveQueueX.append(toX)
		SELECTEDTANK.moveQueueY.append(toY)
		
	def moveUnit(self):
		global SELECTEDTANK
		for step in range(1, len(SELECTEDTANK.moveQueueX)):
			SELECTEDTANK.coordX += SELECTEDTANK.moveQueueX[step] * CELLSIZE
			SELECTEDTANK.coordY += SELECTEDTANK.moveQueueY[step] * CELLSIZE
			pygame.time.wait(200)
			Window0.screenRefresh()
		SELECTEDTANK.moveQueueX[0] = SELECTEDTANK.coordX
		SELECTEDTANK.moveQueueY[0] = SELECTEDTANK.coordY
		del SELECTEDTANK.moveQueueX[1:len(SELECTEDTANK.moveQueueX)]
		del SELECTEDTANK.moveQueueY[1:len(SELECTEDTANK.moveQueueY)]
		
	def unitSelect(self):	#this is a fucking disgrace, fix it ASAP
		global Map0, SELECTEDTANK
		SELECTEDTANK = Map0.mapGetUnit(20, 20)
		
				
class Unit(object):
	coordX = 0
	coordY = 0
	statHealth = 0
	statArmor = 0
	statDamage = 0
	
	def drawUnit(self):
		pass

class Tank(Unit):
	coordX = 0
	coordY = 0
	statHealth = 0
	statArmor = 0
	statDamage = 0
	statSpeed = 5
	arrayPos = 0
	moveQueueX = []
	moveQueueY = []
	
	def drawUnit(self):
		global DISPLAYSURF, CELLSIZE, DARKRED, RED
		outerRect = pygame.Rect(self.coordX +1, self.coordY +1, CELLSIZE -1, CELLSIZE -1)
		innerRect = pygame.Rect(self.coordX +5, self.coordY +5, CELLSIZE -9, CELLSIZE -9)
		pygame.draw.rect(DISPLAYSURF, DARKRED, outerRect)
		pygame.draw.rect(DISPLAYSURF, RED, innerRect)
		
class Main(object):
	def __init__(self):
		global Window0, Input0, Unit0, Map0
		global MoveUp, MoveDown, MoveRight, MoveLeft
		Window0 = DrawingManager()
		Input0 = InputManager()
		Unit0 = UnitManager()
		Map0 = MapManager()
		
		Bulldozer = Unit0.unitCreate(1, 1)
		Unit0.unitSelect()
		
		while True:
			Input0.handleInput()
			Window0.screenRefresh()
		
	def terminate(self):
		pygame.quit()
		sys.exit()

StartShenanigans = Main()