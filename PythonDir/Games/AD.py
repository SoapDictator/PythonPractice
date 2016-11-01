#Artificial Destiny
#By SoapDictator

import pygame, sys
from pygame.locals import *

class InputManager(object):
	global STATE, CURRENTSTATE
	STATE = ['moveSelection', 'unitSelected']
	CURRENTSTATE = STATE[0]
	
	def getState(self):
		global CURRENTSTATE
		return CURRENTSTATE
		
	def setState(self, num):
		global STATE, CURRENTSTATE
		CURRENTSTATE = STATE[num]
	
	def handleInput(self):
		global SELECTEDTANK #fix this :\
		state = self.getState()
		for event in pygame.event.get():
			if event.type == QUIT:
				self.terminate()
			elif state == 'moveSelection':
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.terminate()
					elif event.key == K_UP:		Map0.moveSelect(0, -1)
					elif event.key == K_DOWN:	Map0.moveSelect(0, +1)
					elif event.key == K_RIGHT:	Map0.moveSelect(+1, 0)
					elif event.key == K_LEFT:	Map0.moveSelect(-1, 0)
					elif event.key == K_e:		#fix that as well
						Unit0.unitSelect()
						if SELECTEDTANK != 0:
							self.setState(1)
			elif state == 'unitSelected':
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.setState(0)
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
			
	def screenSelect(self):
		global DISPLAYSURF, CELLSIZE, GREEN, MAPSELECT
		outerRect = pygame.Rect(MAPSELECT.coordX, MAPSELECT.coordY, CELLSIZE, CELLSIZE )
		topX = MAPSELECT.coordX
		topY = MAPSELECT.coordY
		lowX = MAPSELECT.coordX + CELLSIZE
		lowY = MAPSELECT.coordY + CELLSIZE
		pygame.draw.line(DISPLAYSURF, GREEN, (topX, topY), (lowX, topY))
		pygame.draw.line(DISPLAYSURF, GREEN, (lowX, topY), (lowX, lowY))
		pygame.draw.line(DISPLAYSURF, GREEN, (lowX, lowY), (topX, lowY))
		pygame.draw.line(DISPLAYSURF, GREEN, (topX, lowY), (topX, topY))
			
	def screenMovement(self):
		global TANKARRAY
		for k in range(0, len(TANKARRAY)-1):
			toX = TANKARRAY[k].moveQueueX[0] + CELLSIZE/2
			toY = TANKARRAY[k].moveQueueY[0] + CELLSIZE/2
			for num in range(1, len(TANKARRAY[k].moveQueueX)):
				x = toX
				y = toY
				toX += TANKARRAY[k].moveQueueX[num] * CELLSIZE
				toY += TANKARRAY[k].moveQueueY[num] * CELLSIZE
				pygame.draw.line(DISPLAYSURF, RED, (x, y), (toX, toY))
			toX = 0
			toY = 0
					
	def screenRefresh(self):
		DISPLAYSURF.fill(BGCOLOR)
		self.screenGrid()
		self.screenMovement()
		for TANK in TANKARRAY:
			TANK.drawUnit()
		self.screenSelect()
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
	def __init__(self):
		global MAPSELECT
		MAPSELECT = Unit()
		
	def mapGetUnit(self):
		global MAPSELECT, TANKARRAY
		for TANK in TANKARRAY:
			if TANK.coordX == MAPSELECT.coordX:
				if TANK.coordY == MAPSELECT.coordY:
					return TANK
		return 0
	
	def moveSelect(self, toX, toY):
		global MAPSELECT, CELLSIZE
		MAPSELECT.coordX += toX*CELLSIZE
		MAPSELECT.coordY += toY*CELLSIZE
		
				
class UnitManager(object):
	def __init__(self):
		global TANKARRAY
		TANKARRAY = []
	
	def unitCreate(self, coordX, coordY): # new tank always needs to be the last one in the array
		global TANKARRAY
		print("A new tank appears!")
		NewTank = Tank()
		TANKARRAY.append(NewTank)
		NewTank.arrayPos = len(TANKARRAY)-1
		NewTank.coordX = coordX * CELLSIZE
		NewTank.coordY = coordY * CELLSIZE
		NewTank.moveQueueX[0] = NewTank.coordX
		NewTank.moveQueueY[0] = NewTank.coordY
		return NewTank
	
	def unitDestroy(self, Tank):
		global TANKARRAY
		Tank.coordX = -1 * CELLSIZE #resets the position just in case
		Tank.coordY = -1 * CELLSIZE
		del TANKARRAY[Tank.arrayPos]
		for TANK in TANKARRAY: #shifts all tanks so the new tank will be last in the array
			if Tank.arrayPos > TANK.arrayPos:
				TANK.arrayPos -= 1
		del Tank.moveQueueX[0:len(Tank.moveQueueX)]
		del Tank.moveQueueY[0:len(Tank.moveQueueY)]
		print("A tank has been erased!")
		
	def moveStore(self, toX, toY):
		global SELECTEDTANK#, TANKARRAY
		SELECTEDTANK.moveQueueX.append(toX)
		#print(TANKARRAY[0].moveQueueX[len(TANKARRAY[0].moveQueueX)-1])
		SELECTEDTANK.moveQueueY.append(toY)
		
	def moveUnit(self):		#this is a fucking disgrace, fix it ASAP
		for TANK in TANKARRAY:
			for step in range(1, len(TANK.moveQueueX)):
				TANK.coordX += TANK.moveQueueX[step] * CELLSIZE
				TANK.coordY += TANK.moveQueueY[step] * CELLSIZE
				pygame.time.wait(200)
				Window0.screenRefresh()
		TANK.moveQueueX[0] = TANK.coordX
		TANK.moveQueueY[0] = TANK.coordY
		del TANK.moveQueueX[1:len(TANK.moveQueueX)]
		del TANK.moveQueueY[1:len(TANK.moveQueueY)]
		
	def unitSelect(self):
		global Map0, SELECTEDTANK
		SELECTEDTANK = Map0.mapGetUnit()
		
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
	moveQueue = [0]*20
	
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
		Blinker = Unit0.unitCreate(3, 1)
		
		while True:
			Input0.handleInput()
			Window0.screenRefresh()
		
	def terminate(self):
		pygame.quit()
		sys.exit()

StartShenanigans = Main()