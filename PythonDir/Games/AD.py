#Artificial Destiny
#By SoapDictator

import pygame, sys
from pygame.locals import *

class GameEventManager(object):
	EVENTQUEUE = []
	
	def eventAdd(self, eventName, data):	#TODO: event sorting mechanism
		event = 0
		if eventName == "EventTerminate":
			event = EventTerminate()
			priority = -1
		elif eventName == "EventUnitCreate":
			event = EventUnitCreate(data)
			priority = 3
		elif eventName == "EventUnitDestroy":
			event = EventUnitDestroy(data)
			priority = 4
		elif eventName == "EventUnitHealthCheck":
			event = EventUnitHealthCheck()
			priority = 2
		elif eventName == "EventUnitMove":
			event = EventUnitMove()
			priority = 5
		elif eventName == "EventUnitAttack":
			targetedUnit = Map0.mapGetUnit()
			if targetedUnit != -1 and targetedUnit != Unit0.SELECTEDUNIT:
				X = Unit0.SELECTEDUNIT.statCoord[0]
				Y = Unit0.SELECTEDUNIT.statCoord[1]
				toX = targetedUnit.statCoord[0]
				toY = targetedUnit.statCoord[1]
				if abs(X-toX)+abs(Y-toY) <= Unit0.SELECTEDUNIT.statFR:
					event = EventUnitAttack([Unit0.SELECTEDUNIT, targetedUnit])
					priority = 1
					Input0.setState(1)
		
		if event != 0:
			if len(self.EVENTQUEUE) > 1:
				if self.EVENTQUEUE[0][1] > priority:
					self.EVENTQUEUE.insert(0, [event, priority])
				elif self.EVENTQUEUE[len(self.EVENTQUEUE)-1][1] < priority:
					self.EVENTQUEUE.append([event, priority])
				else:
					for i in range(1, len(self.EVENTQUEUE)):
						if self.EVENTQUEUE[i-1][1] <= priority and self.EVENTQUEUE[i][1] > priority:
							self.EVENTQUEUE.insert(i, [event, priority])
			else:
				self.EVENTQUEUE.append([event, priority])
	
	def eventHandle(self):
		self.eventAdd("EventUnitHealthCheck", 0)
		self.eventAdd("EventUnitMove", 0)
		for event in self.EVENTQUEUE:
			event[0].execute()
		del self.EVENTQUEUE[0:len(self.EVENTQUEUE)]
		print("------------")

class GameEvent(object):
	def execute(self):
		print("This is a prototype event, get out!")

class EventTerminate(GameEvent):
	def execute(self):
		print("Terminated.")
		pygame.quit()
		sys.exit()

class EventUnitCreate(GameEvent):
	def __init__(self, data):
		self.unitType = data[0]
		self.coord = data[1]
		
	def execute(self):
		print("A new %s appears!" %self.unitType)
		Unit0.unitCreate(self.unitType, self.coord[0], self.coord[1])

class EventUnitDestroy(GameEvent):
	def __init__(self, deletedUnit):
		self.deletedUnit = deletedUnit
		
	def execute(self):
		print("Unit lost.")
		Unit0.unitDestroy(self.deletedUnit)

class EventUnitHealthCheck(GameEvent):
	def execute(self):
		print("Health check.")
		for Unit in Unit0.UNITARRAY:
			if Unit.statHealth <= 0:
				Event0.eventAdd("EventUnitDestroy", Unit)

class EventUnitMove(GameEvent):
	def execute(self):
		print("Moving units.")
		Unit0.unitMove()

class EventUnitAttack(GameEvent):
	def __init__(self, Units):
		self.attackingUnit = Units[0]
		self.targetedUnit = Units[1]
	
	def execute(self):
		print("A unit is under attack!")
		Unit0.unitAttack(self.attackingUnit, self.targetedUnit)

class InputManager(object):		#TODO: input binds for separate input states
	inputState = ['moveSelection', 'unitSelected', 'unitAttack']
	inputDict = {inputState[0]:	['moveSelect'], 
				 inputState[1]:	['moveStore'], 
				 inputState[2]:	['moveSelect']}
	currentState = inputState[0]
	
	def getState(self):
		return self.currentState
		
	def setState(self, num):
		self.currentState = self.inputState[num]
		if num == 0:
			 Unit0.SELECTEDUNIT = -1
	
	def handleInput(self):
		for event in pygame.event.get():	#this is chinese level of programming, needs fixing as well
			if event.type == QUIT:
				self.terminate()
			if event.type == KEYDOWN:
				if event.key == K_UP:		getattr(Unit0, self.inputDict[self.getState()][0])(0, -1)
				elif event.key == K_DOWN:	getattr(Unit0, self.inputDict[self.getState()][0])(0, +1)
				elif event.key == K_RIGHT:	getattr(Unit0, self.inputDict[self.getState()][0])(+1, 0)
				elif event.key == K_LEFT:	getattr(Unit0, self.inputDict[self.getState()][0])(-1, 0)
			if self.getState() == 'moveSelection':
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.terminate()
					elif event.key == K_e:
						Unit0.unitSelect()
						if Unit0.SELECTEDUNIT != -1:	self.setState(1)
						else:							Event0.eventHandle()
			elif self.getState() == 'unitSelected':
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.setState(0)
					elif event.key == K_e:		Event0.eventHandle()
					elif event.key == K_a:		self.setState(2)
			elif self.getState() == 'unitAttack':
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.setState(1)
					elif event.key == K_e:		Event0.eventAdd("EventUnitAttack", 0)

	def terminate(self):
		print("Terminated.")
		pygame.quit()
		sys.exit()
	
class DrawingManager(object):
	FPS = 0
	FPSCLOCK = 0
	WINDOWWIDTH = 0
	WINDOWHEIGHT = 0
	DISPLAYSURF = 0
	BASICFONT = 0
	
	def __init__(self):
		self.screenConfig()
		self.screenColors()
		
		pygame.init()
		self.FPSCLOCK = pygame.time.Clock()
		self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
		self.BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
		pygame.display.set_caption('AD')
		
	def screenDrawGrid(self):
		for x in range(0, self.WINDOWWIDTH, self.CELLSIZE):	# draw vertical lines
			pygame.draw.line(self.DISPLAYSURF, self.LIGHTGRAY, (x, 0), (x, self.WINDOWHEIGHT))
		for y in range(0, self.WINDOWHEIGHT, self.CELLSIZE):	# draw horizontal lines
			pygame.draw.line(self.DISPLAYSURF, self.LIGHTGRAY, (0, y), (self.WINDOWWIDTH, y))
	
	def screenDrawVO(self):
		for VO in Map0.MOARRAY:
			pygame.draw.rect(self.DISPLAYSURF, self.LIGHTGRAY, pygame.Rect(VO[0]*self.CELLSIZE+1, VO[1]*self.CELLSIZE+1, self.CELLSIZE -1, self.CELLSIZE -1))
	
	def screenDrawSelect(self):
		outerRect = pygame.Rect(Map0.MAPSELECT.statCoord[0], Map0.MAPSELECT.statCoord[1], self.CELLSIZE, self.CELLSIZE)
		topX = Map0.MAPSELECT.statCoord[0]*self.CELLSIZE
		topY = Map0.MAPSELECT.statCoord[1]*self.CELLSIZE
		lowX = Map0.MAPSELECT.statCoord[0]*self.CELLSIZE + self.CELLSIZE
		lowY = Map0.MAPSELECT.statCoord[1]*self.CELLSIZE + self.CELLSIZE
		pygame.draw.line(self.DISPLAYSURF, self.GREEN, (topX, topY), (lowX, topY))
		pygame.draw.line(self.DISPLAYSURF, self.GREEN, (lowX, topY), (lowX, lowY))
		pygame.draw.line(self.DISPLAYSURF, self.GREEN, (lowX, lowY), (topX, lowY))
		pygame.draw.line(self.DISPLAYSURF, self.GREEN, (topX, lowY), (topX, topY))
			
	def screenDrawMovement(self):
		for MOVE in Unit0.MOVEQUEUE:
			for num in range(1, len(MOVE)):
				X = MOVE[num-1][0]*self.CELLSIZE + self.CELLSIZE/2
				Y = MOVE[num-1][1]*self.CELLSIZE + self.CELLSIZE/2
				toX = MOVE[num][0]*self.CELLSIZE + self.CELLSIZE/2
				toY = MOVE[num][1]*self.CELLSIZE + self.CELLSIZE/2
				pygame.draw.line(self.DISPLAYSURF, self.LIGHTBLUE, (X, Y), (toX, toY))
	
	def screenDrawPossiblePath(self, coord, limit, color):
		Map0.mapGetPossiblePath(coord, limit)
		for i in range(1, len(Map0.FRONTIER)):
			toX = Map0.FRONTIER[i][0]*self.CELLSIZE+self.CELLSIZE/2
			toY = Map0.FRONTIER[i][1]*self.CELLSIZE+self.CELLSIZE/2
			pygame.draw.line(self.DISPLAYSURF, color, (toX-2, toY-2), (toX+2, toY+2))
	
	
	def screenRefresh(self):
		self.DISPLAYSURF.fill(self.BGCOLOR)
		self.screenDrawGrid()
		self.screenDrawVO()
		self.screenDrawMovement()
		for UNIT in Unit0.UNITARRAY:
			UNIT.drawUnit()
		#if Unit0.SELECTEDUNIT != -1:
		#	self.screenDrawPossiblePath(Unit0.SELECTEDUNIT.statCoord, Unit0.SELECTEDUNIT.statSpeed, self.LIGHTBLUE)
		#	self.screenDrawPossiblePath(Unit0.SELECTEDUNIT.statCoord, Unit0.SELECTEDUNIT.statFR, self.RED)
		if Map0.mapGetUnit() != -1:
			self.screenDrawPossiblePath(Map0.mapGetUnit().statCoord, Map0.mapGetUnit().statSpeed, self.LIGHTBLUE)
			self.screenDrawPossiblePath(Map0.mapGetUnit().statCoord, Map0.mapGetUnit().statFR, self.RED)
		self.screenDrawSelect()
		pygame.display.update()
	
	def screenConfig(self):
		self.FPS = 10
		self.WINDOWWIDTH = 640
		self.WINDOWHEIGHT = 480
		self.CELLSIZE = 20
		
		assert self.WINDOWWIDTH % self.CELLSIZE == 0
		assert self.WINDOWHEIGHT % self.CELLSIZE == 0

		self.CELLWIDTH = int(self.WINDOWWIDTH / self.CELLSIZE)
		self.CELLHEIGHT = int(self.WINDOWHEIGHT / self.CELLSIZE)
	
	def screenColors(self):
		#					R	G	B
		self.WHITE		= (255, 255, 255)
		self.BLACK		= (  0,	  0,   0)
		self.BLUE		= (0,   0,   155)
		self.RED		= (155,   0,   0)
		self.DARKRED	= (255,   0,   0)
		self.GREEN		= (  0, 255,   0)
		self.DARKGREEN	= (  0, 155,   0)
		self.LIGHTBLUE	= (60,   60, 200)
		self.LIGHTGRAY	= (120, 120, 120)
		self.BGCOLOR	= self.BLACK

class MapManager(object):
	NEIGHBOURS = {}
	MOARRAY = []
	FRONTIER = []
	
	def __init__(self):
		self.MAPSELECT = Unit()
		self.mapGenerateGraph()
	
	def mapGenerateGraph(self):
		for X in range(0, Window0.CELLWIDTH+1):
			for Y in range(0, Window0.CELLHEIGHT+1):
				self.NEIGHBOURS[X, Y] = []
				if X + 1 <= Window0.CELLWIDTH and [X+1, Y] not in self.MOARRAY:
					self.NEIGHBOURS[X, Y].append([X+1, Y])
				if Y + 1 <= Window0.CELLHEIGHT  and [X, Y+1] not in self.MOARRAY:
					self.NEIGHBOURS[X, Y].append([X, Y+1])
				if X - 1 >= 0  and [X-1, Y] not in self.MOARRAY:
					self.NEIGHBOURS[X, Y].append([X-1, Y])
				if Y - 1 >= 0  and [X, Y-1] not in self.MOARRAY:
					self.NEIGHBOURS[X, Y].append([X, Y-1])
	
	def mapGetUnit(self):
		for UNIT in Unit0.UNITARRAY:
			if UNIT.statCoord == self.MAPSELECT.statCoord:
				return UNIT
		return -1
	
	def mapGetPossiblePath(self, coord, limit):	#TODO: fix the "if"
		frontier = [[coord[0], coord[1]]]
		visited = {}
		visited[frontier[0][0], frontier[0][1]] = True
		flagBreak = False
		
		while not flagBreak:
			if abs(frontier[0][0]) >= abs(coord[0])-limit+1 and abs(frontier[0][1]) >= abs(coord[1])-limit+1:
				current = frontier[0]
				del frontier[0]
				for next in self.NEIGHBOURS[current[0], current[1]]:
					if not visited.has_key((next[0], next[1])):
						frontier.append(next)
						visited[next[0], next[1]] = True
			else:
				frontier.append([coord[0]+limit, coord[1]])
				flagBreak = True
		self.FRONTIER = frontier

class UnitManager(object):
	UNITARRAY = []
	MOVEQUEUE = []
	SELECTEDUNIT = -1
	
	def unitCreate(self, unitType, toX, toY): 	# new unit always will be the last one in the array
		if unitType == "Scout":
			NewUnit = Scout()
		elif unitType == "Tank":
			NewUnit = Tank()
		elif unitType == "Artillery":
			NewUnit = Artillery()
		elif unitType == "Engineer":
			NewUnit = Engineer()
		self.UNITARRAY.append(NewUnit)
		NewUnit.arrayPos = len(self.UNITARRAY)-1
		
		NewUnit.statCoord = [toX, toY]
		self.MOVEQUEUE.append([[toX, toY]])
	
	def unitDestroy(self, deletedUnit):
		del self.UNITARRAY[deletedUnit.arrayPos]
		del self.MOVEQUEUE[deletedUnit.arrayPos]
		for UNIT in self.UNITARRAY: 	#shifts all tanks situated after the deleted one in the array
			if deletedUnit.arrayPos < UNIT.arrayPos:
				UNIT.arrayPos -= 1
		
	def moveStore(self, toX, toY):		#saves a move and checks for the previous move undo
		Position = self.SELECTEDUNIT.arrayPos
		moveLength = len(self.MOVEQUEUE[Position])-1
		X = self.MOVEQUEUE[Position][moveLength][0]
		Y = self.MOVEQUEUE[Position][moveLength][1]
		if [X+toX, Y+toY] == [self.MOVEQUEUE[Position][moveLength-1][0], self.MOVEQUEUE[Position][moveLength-1][1]]:
			del self.MOVEQUEUE[Position][moveLength]
		elif X+toX > Window0.CELLWIDTH or X+toX < 0:
			pass
		elif Y+toY > Window0.CELLHEIGHT or Y+toY < 0:
			pass
		elif [X+toX, Y+toY] in self.MOVEQUEUE[Position]:
			pass
		elif [X+toX, Y+toY] not in Map0.MOARRAY:
			self.MOVEQUEUE[Position].append([X+toX, Y+toY])
	
	def moveSelect(self, toX, toY):		#ducttape till I get the cursor support running
		Map0.MAPSELECT.statCoord[0] += toX
		Map0.MAPSELECT.statCoord[1] += toY
	
	def unitMove(self):
		stopFlag = [0]*len(self.MOVEQUEUE)
		sum = 0
		for step in range(1, 50):
			for UNIT in self.UNITARRAY:
				if len(self.MOVEQUEUE[UNIT.arrayPos]) == 1:
					stopFlag[UNIT.arrayPos] = 1
					continue
				elif step >= len(self.MOVEQUEUE[UNIT.arrayPos]):
					stopFlag[UNIT.arrayPos] = 1
					continue
				UNIT.statCoord[0] = self.MOVEQUEUE[UNIT.arrayPos][step][0]
				UNIT.statCoord[1] = self.MOVEQUEUE[UNIT.arrayPos][step][1]
			for flag in stopFlag:
				sum += flag
			if sum == len(self.MOVEQUEUE):
				break
			sum = 0
			pygame.time.wait(100)
			Window0.screenRefresh()
		
		for UNIT in self.UNITARRAY:
			self.MOVEQUEUE[UNIT.arrayPos][0] = [UNIT.statCoord[0], UNIT.statCoord[1]]
			del self.MOVEQUEUE[UNIT.arrayPos][1:len(self.MOVEQUEUE[UNIT.arrayPos])]
	
	def unitAttack(self, attackingUnit, targetedUnit):
		if isinstance(attackingUnit, Tank) or isinstance(attackingUnit, Artillery):
			targetedUnit.statHealth -= attackingUnit.statDamage
	
	def unitSelect(self):
		self.SELECTEDUNIT = Map0.mapGetUnit()
		
class Unit(object):
	statCoord = [0, 0]
	statHealth = 10
	statArmor = 0
	statDamage = 10
	statSpeed = 5
	statVR = 6
	arrayPos = 0
	
	def drawUnit(self):
		pass

class Scout(Unit):
	def drawUnit(self):
		outerRect = pygame.Rect(self.statCoord[0]*Window0.CELLSIZE+1, self.statCoord[1]*Window0.CELLSIZE+1, Window0.CELLSIZE -1, Window0.CELLSIZE -1)
		innerRect = pygame.Rect(self.statCoord[0]*Window0.CELLSIZE+5, self.statCoord[1]*Window0.CELLSIZE+5, Window0.CELLSIZE -9, Window0.CELLSIZE -9)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.DARKRED, outerRect)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.RED, innerRect)
		
class Tank(Unit):
	statFR = 4
	statAmmoCap = 10
	
	def drawUnit(self):
		outerRect = pygame.Rect(self.statCoord[0]*Window0.CELLSIZE+1, self.statCoord[1]*Window0.CELLSIZE+1, Window0.CELLSIZE -1, Window0.CELLSIZE -1)
		innerRect = pygame.Rect(self.statCoord[0]*Window0.CELLSIZE+5, self.statCoord[1]*Window0.CELLSIZE+5, Window0.CELLSIZE -9, Window0.CELLSIZE -9)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.DARKRED, outerRect)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.RED, innerRect)

class Artillery(Unit):
	statMinFR = 1
	statMaxFR = 10
	statAmmoCap = 10
	
	def drawUnit(self):
		outerRect = pygame.Rect(self.statCoord[0]*Window0.CELLSIZE+1, self.statCoord[1]*Window0.CELLSIZE+1, Window0.CELLSIZE -1, Window0.CELLSIZE -1)
		innerRect = pygame.Rect(self.statCoord[0]*Window0.CELLSIZE+5, self.statCoord[1]*Window0.CELLSIZE+5, Window0.CELLSIZE -9, Window0.CELLSIZE -9)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.DARKRED, outerRect)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.RED, innerRect)
		
class Engineer(Unit):
	statFR = 5
	
	def drawUnit(self):
		outerRect = pygame.Rect(self.statCoord[0]*Window0.CELLSIZE+1, self.statCoord[1]*Window0.CELLSIZE+1, Window0.CELLSIZE -1, Window0.CELLSIZE -1)
		innerRect = pygame.Rect(self.statCoord[0]*Window0.CELLSIZE+5, self.statCoord[1]*Window0.CELLSIZE+5, Window0.CELLSIZE -9, Window0.CELLSIZE -9)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.DARKRED, outerRect)
		pygame.draw.rect(Window0.DISPLAYSURF, Window0.RED, innerRect)

class Main(object):
	def __init__(self):
		global Event0, Window0, Input0, Unit0, Map0
		Event0 = GameEventManager()
		Window0 = DrawingManager()
		Input0 = InputManager()
		Unit0 = UnitManager()
		Map0 = MapManager()
		
		self.test()
		
		while True:
			Input0.handleInput()
			Window0.screenRefresh()
			Window0.FPSCLOCK.tick(Window0.FPS)
	
	def test(self):
		Event0.eventAdd("EventUnitCreate", ("Tank", [1, 1]))
		Event0.eventAdd("EventUnitCreate", ("Tank", [3, 1]))
		Event0.eventHandle()
		Map0.MOARRAY.append([1, 2])
		Map0.MOARRAY.append([3, 2])
		#Event0.eventAdd("EventTerminate")		#in case things go wrong

StartShenanigans = Main()