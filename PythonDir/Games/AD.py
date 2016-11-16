#Artificial Destiny
#By SoapDictator

import pygame, sys
from pygame.locals import *

class GameEventManager(object):
	EVEQUEUE = []
	
	def __init__(self):
		print("this is GameEventManager __init__")
		
	def addEvent(self, event):
		self.EVENTQUEUE.append(event)
		
	def removeEvent(self, event):
		for index in range(0, len(self.EVENTQUEUE)-1):
			if self.EVENTQUEUE[index] == event:
				del EVENTQUEUE[index]
				for k in range(index+1, len(self.EVENTQUEUE)-1):
					self.EVENTQUEUE[k-1] = self.EVENTQUEUE[k]

class GameEvent(object):
	def __init__(self):
		print("This is a prototype event, get out!")

class InputManager(object):
	inputState = ['moveSelection', 'unitSelected']
	currentState = inputState[0]
	
	def getState(self):
		return self.currentState
		
	def setState(self, num):
		self.currentState = self.inputState[num]
	
	def handleInput(self):
		global SELECTEDTANK		#fix this :\
		for event in pygame.event.get():	#this is chinese level of programming, needs fixing as well
			if event.type == QUIT:
				self.terminate()
			elif self.getState() == 'moveSelection':
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.terminate()
					elif event.key == K_UP:		Map0.moveSelect(0, -1)
					elif event.key == K_DOWN:	Map0.moveSelect(0, +1)
					elif event.key == K_RIGHT:	Map0.moveSelect(+1, 0)
					elif event.key == K_LEFT:	Map0.moveSelect(-1, 0)
					elif event.key == K_e:		#fix that as well
						Unit0.unitSelect()
						if Unit0.SELECTEDTANK != -1:
							self.setState(1)
			elif self.getState() == 'unitSelected':
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
	FPS = 0
	FPSCLOCK = 0
	WINDOWWIDTH = 0
	WINDOWHEIGTH = 0
	DISPLAYSURF = 0
	BASICFONT = 0
	
	def __init__(self):
		self.screenConfig()
		self.screenColors()
		
		pygame.init()
		self.FPSCLOCK = pygame.time.Clock()
		self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGTH))
		self.BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
		pygame.display.set_caption('AD')
		
	def screenGrid(self):
		for x in range(0, self.WINDOWWIDTH, self.CELLSIZE):	# draw vertical lines
			pygame.draw.line(self.DISPLAYSURF, self.LIGHTGRAY, (x, 0), (x, self.WINDOWHEIGTH))
		for y in range(0, self.WINDOWHEIGTH, self.CELLSIZE):	# draw horizontal lines
			pygame.draw.line(self.DISPLAYSURF, self.LIGHTGRAY, (0, y), (self.WINDOWWIDTH, y))
			
	def screenSelect(self):
		outerRect = pygame.Rect(Map0.MAPSELECT.statCoord[0], Map0.MAPSELECT.statCoord[1], self.CELLSIZE, self.CELLSIZE)
		topX = Map0.MAPSELECT.statCoord[0]
		topY = Map0.MAPSELECT.statCoord[1]
		lowX = Map0.MAPSELECT.statCoord[0] + self.CELLSIZE
		lowY = Map0.MAPSELECT.statCoord[1] + self.CELLSIZE
		pygame.draw.line(self.DISPLAYSURF, self.GREEN, (topX, topY), (lowX, topY))
		pygame.draw.line(self.DISPLAYSURF, self.GREEN, (lowX, topY), (lowX, lowY))
		pygame.draw.line(self.DISPLAYSURF, self.GREEN, (lowX, lowY), (topX, lowY))
		pygame.draw.line(self.DISPLAYSURF, self.GREEN, (topX, lowY), (topX, topY))
			
	def screenMovement(self):
		for MOVE in Unit0.MOVEQUEUE:
			toX = MOVE[0][0] + self.CELLSIZE/2
			toY = MOVE[0][1] + self.CELLSIZE/2
			for num in range(1, len(MOVE)):
				x = toX
				y = toY
				toX += MOVE[num][0] * self.CELLSIZE
				toY += MOVE[num][1] * self.CELLSIZE
				pygame.draw.line(self.DISPLAYSURF, self.RED, (x, y), (toX, toY))
			toX = 0
			toY = 0
					
	def screenRefresh(self):
		self.DISPLAYSURF.fill(self.BGCOLOR)
		self.screenGrid()
		self.screenMovement()
		for TANK in Unit0.TANKARRAY:
			TANK.drawUnit()
		self.screenSelect()
		pygame.display.update()
	
	def screenConfig(self):
		self.FPS = 10
		self.WINDOWWIDTH = 640
		self.WINDOWHEIGTH = 480
		self.CELLSIZE = 20
		
		assert self.WINDOWWIDTH % self.CELLSIZE == 0
		assert self.WINDOWHEIGTH % self.CELLSIZE == 0

		self.CELLWIDTH = int(self.WINDOWWIDTH / self.CELLSIZE)
		self.CELLHEIGTH = int(self.WINDOWHEIGTH / self.CELLSIZE)
	
	def screenColors(self):
		#					R	G	B
		self.WHITE		= (255, 255, 255)
		self.BLACK		= (  0,	  0,   0)
		self.RED		= (155,   0,   0)
		self.DARKRED	= (255,   0,   0)
		self.GREEN		= (  0, 255,   0)
		self.DARKGREEN	= (  0, 155,   0)
		self.LIGHTGRAY	= (120, 120, 120)
		self.BGCOLOR	= self.BLACK

class MapManager(object):
	def __init__(self):
		self.MAPSELECT = Unit()
		
	def mapGetUnit(self):
		for TANK in Unit0.TANKARRAY:
			if TANK.statCoord == self.MAPSELECT.statCoord:
				return TANK
		return -1
	
	def moveSelect(self, toX, toY):
		self.MAPSELECT.statCoord[0] += toX*Window0.CELLSIZE
		self.MAPSELECT.statCoord[1] += toY*Window0.CELLSIZE
		
				
class UnitManager(object):
	TANKARRAY = []
	MOVEQUEUE = []
	SELECTEDTANK = 0
	
	def unitCreate(self, toX, toY): 	# new tank always will be the last one in the array
		print("A new tank appears!")
		NewTank = Tank()
		self.TANKARRAY.append(NewTank)
		NewTank.arrayPos = len(self.TANKARRAY)-1
		
		NewTank.statCoord = [toX * Window0.CELLSIZE, toY * Window0.CELLSIZE]
		self.MOVEQUEUE.append([[toX * Window0.CELLSIZE, toY * Window0.CELLSIZE]])
	
	def unitDestroy(self, deletedTank):
		del self.TANKARRAY[deletedTank.arrayPos]
		del self.MOVEQUEUE[deletedTank.arrayPos]
		for TANK in self.TANKARRAY: 	#shifts all tanks so the new tank will be last in the array
			if deletedTank.arrayPos < TANK.arrayPos:
				TANK.arrayPos -= 1
		print("A tank has been erased!")
		
	def moveStore(self, toX, toY):
		moveLength = len(self.MOVEQUEUE[self.SELECTEDTANK.arrayPos])
		if self.MOVEQUEUE[self.SELECTEDTANK.arrayPos][moveLength-1] == [-toX, -toY]:
			del self.MOVEQUEUE[self.SELECTEDTANK.arrayPos][moveLength-1]
		else:
			self.MOVEQUEUE[self.SELECTEDTANK.arrayPos].append([toX, toY])
		
	def moveUnit(self):
		for TANK in self.TANKARRAY:
			for step in range(1, len(self.MOVEQUEUE[TANK.arrayPos])):
				TANK.statCoord[0] += self.MOVEQUEUE[TANK.arrayPos][step][0]*Window0.CELLSIZE
				TANK.statCoord[1] += self.MOVEQUEUE[TANK.arrayPos][step][1]*Window0.CELLSIZE
				pygame.time.wait(100)
				Window0.screenRefresh()
		
		for TANK in self.TANKARRAY:
			self.MOVEQUEUE[TANK.arrayPos][0] = [TANK.statCoord[0], TANK.statCoord[1]]
			del self.MOVEQUEUE[TANK.arrayPos][1:len(self.MOVEQUEUE[TANK.arrayPos])]
		
	def unitSelect(self):
		self.SELECTEDTANK = Map0.mapGetUnit()
		
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
		outerRect = pygame.Rect(self.statCoord[0] +1, self.statCoord[1] +1, Window0.CELLSIZE -1, Window0.CELLSIZE -1)
		innerRect = pygame.Rect(self.statCoord[0] +5, self.statCoord[1] +5, Window0.CELLSIZE -9, Window0.CELLSIZE -9)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.DARKRED, outerRect)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.RED, innerRect)
		
class Main(object):
	def __init__(self):
		global Window0, Input0, Unit0, Map0
		#global MoveUp, MoveDown, MoveRight, MoveLeft	#rudiment from the commmand prompt
		Window0 = DrawingManager()
		Input0 = InputManager()
		Unit0 = UnitManager()
		Map0 = MapManager()
		
		Unit0.unitCreate(1, 1)
		Unit0.unitCreate(3, 1)
		
		while True:
			Input0.handleInput()
			Window0.screenRefresh()
			Window0.FPSCLOCK.tick(Window0.FPS)
		
	def terminate(self):
		pygame.quit()
		sys.exit()

StartShenanigans = Main()