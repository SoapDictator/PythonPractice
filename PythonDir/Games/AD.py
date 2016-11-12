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
						if SELECTEDTANK != -1:
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
		outerRect = pygame.Rect(MAPSELECT.statCoord[0], MAPSELECT.statCoord[1], CELLSIZE, CELLSIZE )
		topX = MAPSELECT.statCoord[0]
		topY = MAPSELECT.statCoord[1]
		lowX = MAPSELECT.statCoord[0] + CELLSIZE
		lowY = MAPSELECT.statCoord[1] + CELLSIZE
		pygame.draw.line(DISPLAYSURF, GREEN, (topX, topY), (lowX, topY))
		pygame.draw.line(DISPLAYSURF, GREEN, (lowX, topY), (lowX, lowY))
		pygame.draw.line(DISPLAYSURF, GREEN, (lowX, lowY), (topX, lowY))
		pygame.draw.line(DISPLAYSURF, GREEN, (topX, lowY), (topX, topY))
			
	def screenMovement(self):
		global TANKARRAY, MOVEQUEUE
		for TANK in TANKARRAY:
			toX = MOVEQUEUE[TANK.arrayPos][0][0] + CELLSIZE/2
			toY = MOVEQUEUE[TANK.arrayPos][0][1] + CELLSIZE/2
			for num in range(1, len(MOVEQUEUE[TANK.arrayPos])):
				x = toX
				y = toY
				toX += MOVEQUEUE[TANK.arrayPos][num][0] * CELLSIZE
				toY += MOVEQUEUE[TANK.arrayPos][num][1] * CELLSIZE
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
			if TANK.statCoord == MAPSELECT.statCoord:
				return TANK
		return -1
	
	def moveSelect(self, toX, toY):
		global MAPSELECT, CELLSIZE
		MAPSELECT.statCoord[0] += toX*CELLSIZE
		MAPSELECT.statCoord[1] += toY*CELLSIZE
		
				
class UnitManager(object):
	def __init__(self):
		global TANKARRAY, MOVEQUEUE
		TANKARRAY = []
		MOVEQUEUE = []
	
	def unitCreate(self, toX, toY): # new tank always needs to be the last one in the array
		global TANKARRAY, MOVEQUEUE
		print("A new tank appears!")
		NewTank = Tank()
		TANKARRAY.append(NewTank)
		NewTank.arrayPos = len(TANKARRAY)-1
		
		NewTank.statCoord[0] = toX * CELLSIZE
		NewTank.statCoord[1] = toY * CELLSIZE
		
		MOVEQUEUE.append([NewTank.statCoord])
	
	def unitDestroy(self, Tank): #needs fixing
		global TANKARRAY, MOVEQUEUE
		Tank.statCoord[0] = -1 * CELLSIZE #resets the position just in case
		Tank.statCoord[1] = -1 * CELLSIZE
		del TANKARRAY[Tank.arrayPos]
		del MOVEQUEUE[Tank.arrayPos]
		for TANK in TANKARRAY: #shifts all tanks so the new tank will be last in the array
			if Tank.arrayPos > TANK.arrayPos:
				TANK.arrayPos -= 1
		print("A tank has been erased!")
		
	def moveStore(self, toX, toY):
		global SELECTEDTANK, MOVEQUEUE
		MOVEQUEUE[SELECTEDTANK.arrayPos].append([toX, toY])
		
	def moveUnit(self):		#this is a fucking disgrace, fix it ASAP
		global TANKARRAY, MOVEQUEUE
		print(MOVEQUEUE)
		for TANK in TANKARRAY:
			for step in range(1, len(MOVEQUEUE[TANK.arrayPos])):
				TANK.statCoord[0] += MOVEQUEUE[TANK.arrayPos][step][0]*CELLSIZE
				TANK.statCoord[1] += MOVEQUEUE[TANK.arrayPos][step][1]*CELLSIZE
				pygame.time.wait(200)
				Window0.screenRefresh()
			MOVEQUEUE[TANK.arrayPos][0] = TANK.statCoord
			del MOVEQUEUE[TANK.arrayPos][1:len(MOVEQUEUE[TANK.arrayPos])]
		
	def unitSelect(self):
		global Map0, SELECTEDTANK
		SELECTEDTANK = Map0.mapGetUnit()
		
class Unit(object):
	statCoord = [0, 0]
	statHealth = 0
	statArmor = 0
	statDamage = 0
	
	def drawUnit(self):
		pass

class Tank(Unit):
	statCoord = [0, 0]
	statHealth = 0
	statArmor = 0
	statDamage = 0
	statSpeed = 5
	arrayPos = 0
	
	def drawUnit(self):
		global DISPLAYSURF, CELLSIZE, DARKRED, RED
		outerRect = pygame.Rect(self.statCoord[0] +1, self.statCoord[1] +1, CELLSIZE -1, CELLSIZE -1)
		innerRect = pygame.Rect(self.statCoord[0] +5, self.statCoord[1] +5, CELLSIZE -9, CELLSIZE -9)
		pygame.draw.rect(DISPLAYSURF, DARKRED, outerRect)
		pygame.draw.rect(DISPLAYSURF, RED, innerRect)
		
class Main(object):
	def __init__(self):
		global Window0, Input0, Unit0, Map0
		global MoveUp, MoveDown, MoveRight, MoveLeft
		global TANKARRAY
		Window0 = DrawingManager()
		Input0 = InputManager()
		Unit0 = UnitManager()
		Map0 = MapManager()
		
		Unit0.unitCreate(1, 1)
		Unit0.unitCreate(3, 1)
		TANKARRAY[0].statCoord = [20, 20]
		
		while True:
			Input0.handleInput()
			Window0.screenRefresh()
		
	def terminate(self):
		pygame.quit()
		sys.exit()

StartShenanigans = Main()