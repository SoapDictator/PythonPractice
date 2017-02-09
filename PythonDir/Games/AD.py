#
#================
#|| Artificially Destined ||
#================
#by SoapDictator
#

import pygame, sys, math
from pygame.locals import *

class GameEventManager(object):
	EVENTQUEUE = []
	LASTADDEDEVENT = 0
	
	def eventAdd(self, eventName, data):	#TODO: event sorting mechanism
		event = 0
		if eventName == "EventUnitCreate":
			event = EventUnitCreate(data)
			priority = 3
		elif eventName == "EventUnitDestroy":
			event = EventUnitDestroy(data)
			priority = 4
		elif eventName == "EventUnitHealthCheck":
			event = EventUnitHealthCheck()
			priority = 2
		elif eventName == "EventUnitAbilityCheck":
			pass
			#priority = 5
		elif eventName == "EventUnitMove":
			event = EventUnitMove()
			priority = 6
		elif eventName == "EventUnitAttack":
			event = EventUnitAttack(data)
			priority = 1
		
		if event != 0:
			if len(self.EVENTQUEUE) > 1:
				if self.EVENTQUEUE[0][1] > priority:
					self.EVENTQUEUE.insert(0, [event, priority])
				elif self.EVENTQUEUE[len(self.EVENTQUEUE)-1][1] < priority:
					self.EVENTQUEUE.append([event, priority])
				else:
					for i in range(1, len(self.EVENTQUEUE)):
						if self.EVENTQUEUE[i-1][1] <= priority and self.EVENTQUEUE[i][1] >= priority:
							self.EVENTQUEUE.insert(i, [event, priority])
			else:
				self.EVENTQUEUE.append([event, priority])
			self.LASTADDEDEVENT = event
	
	def eventUndo(self):
		if Input0.getState() == 'unitSelected' and len(Unit0.MOVEQUEUE[Unit0.SELECTEDUNIT.arrayPos]) > 1:
			del Unit0.MOVEQUEUE[Unit0.SELECTEDUNIT.arrayPos][1:len(Unit0.MOVEQUEUE[Unit0.SELECTEDUNIT.arrayPos])]
		else:
			for i in range(0, len(self.EVENTQUEUE)):
				if self.LASTADDEDEVENT == self.EVENTQUEUE[i][0]:
					print("Undid %s" % self.EVENTQUEUE[i][0])
					del self.EVENTQUEUE[i]
					self.LASTADDEDEVENT = 0
	
	def eventHandle(self):
		self.eventAdd("EventUnitHealthCheck", 0)
		self.eventAdd("EventUnitMove", 0)
		
		for UNIT in Unit0.UNITARRAY:
			if isinstance(UNIT, Tank):
				if UNIT.targetedUnit != -1:
					Event0.eventAdd("EventUnitAttack", UNIT)
			elif isinstance(UNIT, Artillery):
				if UNIT.targetedCoord != [-1, -1]:
					Event0.eventAdd("EventUnitAttack", UNIT)

		for event in self.EVENTQUEUE:
			event[0].execute()
		del self.EVENTQUEUE[0:len(self.EVENTQUEUE)]
		
		#Unit0.unitCalculateVisibility()		commented out; needs fixing
		print("------------")

#------------------------------------------
		
class GameEvent(object):
	def execute(self):
		print("This is a prototype event, get out!")

class EventUnitCreate(GameEvent):
	def __init__(self, data):
		self.unitType = data[0]
		self.coord = data[1]
		
	def execute(self):
		Unit0.unitCreate(self.unitType, self.coord[0], self.coord[1])
		print("A new %s appeared!" %self.unitType)

class EventUnitDestroy(GameEvent):
	def __init__(self, deletedUnit):
		self.deletedUnit = deletedUnit
		
	def execute(self):
		Unit0.unitDestroy(self.deletedUnit)
		print("Unit lost.")

class EventUnitHealthCheck(GameEvent):
	def execute(self):
		for Unit in Unit0.UNITARRAY:
			if Unit.statHealth <= 0:
				Event0.eventAdd("EventUnitDestroy", Unit)
		print("Health checked.")

class EventUnitMove(GameEvent):
	def execute(self):
		Unit0.unitMove()
		print("Moved units.")

class EventUnitAttack(GameEvent):
	def __init__(self, data):
		self.attackingUnit = data
	
	def execute(self):
		if isinstance(self.attackingUnit, Tank):
			if self.attackingUnit.targetedUnit != -1:
				self.attackingUnit.targetedUnit.statHealth -= self.attackingUnit.statDamage
				self.attackingUnit.targetedUnit = -1
		elif isinstance(self.attackingUnit, Artillery):
			targetedUnit = Map0.getUnit(self.attackingUnit.targetedCoord)
			if targetedUnit != -1:
				targetedUnit.statHealth -= self.attackingUnit.statDamage
			self.attackingUnit.targetedCoord = [-1, -1]
		print("A unit is (probably) under attack!")

#------------------------------------------

#Needs an overhaul since i use hexes now
class InputManager(object):
	inputState = ['moveSelection', 'unitSelected', 'unitTargetChange']
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
					elif event.key == K_z:		Event0.eventUndo()
			elif self.getState() == 'unitSelected':
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.setState(0)
					elif event.key == K_a:		self.setState(2)
					elif event.key == K_z:		Event0.eventUndo()
			elif self.getState() == 'unitTargetChange':
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.setState(1)
					elif event.key == K_e:		Unit0.SELECTEDUNIT.unitTargetChange()

	def terminate(self):
		print("Terminated.")
		pygame.quit()
		sys.exit()

#------------------------------------------
		
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
		
	def hextopixel(self, hex):
		x = self.POINTCENTER[0] + self.CELLSIZE/2 * math.sqrt(3) * (hex[0] +hex[1]*0.5)
		y = self.POINTCENTER[1] + self.CELLSIZE/2 * 1.5 * hex[1]
		return [int(x), int(y)]
		
	def pixeltohex(self, pixelHex):
		y = (pixelHex[1] - self.POINTCENTER[1]) / (self.CELLSIZE/2 * 1.5)
		x = (pixelHex[0] - self.POINTCENTER[0]) / (self.CELLSIZE/2 * math.sqrt(3)) - y*0.5
		return self.hexRound([x, y])
		
	def hexRound(self, hex):
		rx = round(hex[0])
		ry = round(-hex[0]-hex[1])
		rz = round(hex[1])
		
		dx = abs(rx - hex[0])
		dy = abs(ry + hex[0] + hex[1])
		dz = abs(rz - hex[1])
		
		if dx > dy and dx > dz:
			rx = -ry-rz
		elif dy > dz:
			#ry = -rx-rz
			pass
		else:
			rz = -rx-ry
			
		return [rx, rz]
	
	#draws a single hex; width=1 will draw an outline, width=0 draws a solid figure
	def drawHex(self, hex, color = [255, 255, 255], width = 1):
		h = self.CELLSIZE
		w = math.sqrt(3)/2 * h
		directions_pixel = [[0, 0.5*h], [0.5*w, 0.25*h], [0.5*w, -0.25*h], 
									[0, -0.5*h], [-0.5*w, -0.25*h], [-0.5*w, 0.25*h]]
		pixelhex = self.hextopixel(hex)
		points = []
		
		for i in range(0, 6):
			points.append([pixelhex[0]+directions_pixel[i][0], 
									pixelhex[1]+directions_pixel[i][1]])
		pygame.draw.polygon(self.DISPLAYSURF, color, points, width)
	
	#draws a direct line from origin to target
	def drawLine(self, origin, target, color = [255, 255, 255]):
		pixelOrigin = self.hextopixel(origin)
		pixelTarget = self.hextopixel(target)
		
		N = Map0.getDistance(origin, target)
		pixelN = [pixelOrigin[0]-pixelTarget[0],pixelOrigin[1]-pixelTarget[1]]
		if N != 0:	pixelDiv = [float(pixelN[0])/N, float(pixelN[1])/N]
		else:		pixelDiv = [0, 0]
		
		pygame.draw.line(self.DISPLAYSURF, color, pixelOrigin, pixelTarget, 1)
		for i in range(0, N+1):
			X = pixelOrigin[0] - int(pixelDiv[0]*i)
			Y = pixelOrigin[1] - int(pixelDiv[1]*i)
			pygame.draw.circle(self.DISPLAYSURF, color, [X, Y], 3)
		
	def drawGrid(self, color = [255, 255, 255], width = 1):
		for q in range(-self.MAPRADIUS, self.MAPRADIUS+1):
			r1 = max(-self.MAPRADIUS, -q-self.MAPRADIUS)
			r2 = min(self.MAPRADIUS, -q+self.MAPRADIUS)
			
			for r in range(r1, r2+1):
				self.drawHex([q, r], color, width)

	#draws EVERYTHING again on each frame
	def screenRefresh(self):
		self.DISPLAYSURF.fill(self.BGCOLOR)
		self.drawGrid([150, 150, 150], 0)
		
		#for hex in Map0.getLine(self.pixeltohex(pygame.mouse.get_pos()), [3, 0]):
		#for hex in Map0.getRing(Map0.getDistance(self.pixeltohex(pygame.mouse.get_pos()), [0, 0]), width = 0):
		for hex in Map0.getPath(self.MAPRADIUS, [0, 0], self.pixeltohex(pygame.mouse.get_pos())):
			self.drawHex(hex, [120, 120, 255], 0)
		self.drawGrid()
		#self.drawLine(self.pixeltohex(pygame.mouse.get_pos()), [3, 0])
		
		pygame.display.update()
	
	#takes settings frrom config.txt
	def screenConfig(self):
		config = open("config.txt", "r")
		for line in config:
			if "FPS = " in line:
				self.FPS = float(line[6:9])
			elif "WINDOWWIDTH = " in line:
				self.WINDOWWIDTH = int(line[14:18])
			elif "WINDOWHEIGHT = " in line:
				self.WINDOWHEIGHT = int(line[15:19])
			elif "CELLSIZE = " in line:
				self.CELLSIZE = int(line[11:15])
		
		#assert self.WINDOWWIDTH % self.CELLSIZE == 0
		#assert self.WINDOWHEIGHT % self.CELLSIZE == 0

		self.CELLWIDTH = int(self.WINDOWWIDTH / self.CELLSIZE)
		self.CELLHEIGHT = int(self.WINDOWHEIGHT / self.CELLSIZE)
		
		self.MAPRADIUS = 4
		self.POINTCENTER = [(0.5+self.MAPRADIUS)*math.sqrt(3)/2*self.CELLSIZE, 
										(0.5+self.MAPRADIUS*0.75)*self.CELLSIZE]
	
	def screenColors(self):
		#								R		G		B
		self.WHITE				= (255, 255, 255)
		self.BLACK				= (    0,     0,     0)
		self.BLUE					= (    0,     0, 155)
		self.RED					= (255,     0,     0)
		self.DARKRED			= (120,     0,     0)
		self.GREEN				= (    0, 255,     0)
		self.YELLOW			= (255, 255,     0)
		self.GREENYELLOW	= (173, 255,   47)
		self.LIGHTBLUE		= (  0,   150, 255)
		self.LIGHTGRAY		= (120, 120, 120)
		self.BGCOLOR	= [60, 60, 60]

#------------------------------------------
		
class MapManager(object):
	NEIGHBOURS = {}
	MOARRAY = []
	VOARRAY = []
	
	def __init__(self):
		self.MAPSELECT = Unit()
		#this is currently the only way to add Movement Obsticles
		#self.MOARRAY.append([3, 0])
		#self.MOARRAY.append([3, 2])
		#self.MOARRAY.append([3, 4])
		#self.MOARRAY.append([3, 6])
		self.createNeighbours()
	
	#generates a graph of all possible transitions from one tile to another
	def createNeighbours(self):
		self.DIRECTIONS = [[-1, 0], [-1, +1], [0, +1],
										[+1, 0], [+1, -1], [0, -1]]
	
		for Q in range(-Window0.MAPRADIUS, Window0.MAPRADIUS+1):
			for R in range(-Window0.MAPRADIUS, Window0.MAPRADIUS+1):
				self.NEIGHBOURS[Q, R] = []
				for hex in self.DIRECTIONS:
					newHex = [Q+hex[0], R+hex[1]]
					if self.getDistance(newHex, [0, 0]) <= Window0.MAPRADIUS and newHex not in self.MOARRAY:
						self.NEIGHBOURS[Q, R].append([newHex[0], newHex[1]])
	
	#curently calculates distance in axial hexagonal coordinates
	def getDistance(self, origin, target):
		#true distance
		#return math.sqrt(math.pow(abs(target[0]-origin[0]), 2) + math.pow(abs(target[1]-origin[1]), 2))
		
		#calculates how many non-diagonal steps it will take to get from origin to target
		#return abs(target[0]-origin[0]) + abs(target[1]-origin[1])
		
		#calculates distance in axial hex coordinates
		aq = origin[0]
		ar = origin[1]
		bq = target[0]
		br = target[1]
		return (abs(aq-bq) + abs(aq+ar-bq-br) + abs(ar-br))/2
	
	#returns all hexes on the line between the 2 points
	def getLine(self, origin, target):
		N = Map0.getDistance(origin, target)
		if N != 0:	div = 1/float(N)
		else:		div = 0
		result = []
		
		for i in range(0, N+1):
			Q =  float(origin[0]) + float(target[0] - origin[0]) * div * i
			R = float(origin[1]) + float(target[1] - origin[1]) * div * i
			result.append(Window0.hexRound([Q, R]))
		return result
	
	#returns a hexes in a ring of a given radius; width=0 returns the entire circle
	def getRing(self, limit, coord = [0, 0], width = 1):
		frontier = [[coord[0], coord[1]]]
		visited = {}
		visited[coord[0], coord[1]] = None
		flagBreak = False
		
		while not flagBreak:
			current = frontier[0]
			del frontier[0]
			if self.getDistance(coord, current) < limit:
				for next in self.NEIGHBOURS[current[0], current[1]]:
					if not visited.has_key((next[0], next[1])):
						frontier.append(next)
						visited[next[0], next[1]] = [current[0], current[1]]
			else:
				frontier.append([current[0], current[1]])
				flagBreak = True
		if width == 1:
			return frontier
		elif width == 0:
			return visited
	
	#returns a unit in a given coordiante if it's there, otherwise returns -1 int
	def getUnit(self, coord):
		for UNIT in Unit0.UNITARRAY:
			if UNIT.statCoord == coord:
				return UNIT
		return -1
	
	def getPath(self, limit, origin, target):
		came_from = self.getRing(limit, origin, 0)
		
		current = target
		path = [current]
		while current != origin:
			current = came_from[current[0], current[1]]
			path.append(current)
		return path
		
#------------------------------------------
		
class UnitManager(object):
	UNITARRAY = []	#array of ALL units on the map
	MOVEQUEUE = []	#array of ALL movement queues of ALL units, position of the movement queue is determined by a unit's position in UNITARRAY
	SELECTEDUNIT = -1	#currently selected unit, default value is "-1"; needs to be reseted after the unit is deselected
	
	#creates a new unit and adds it to the UNITARRAY as well as creates an entry in MOVEQUEUE; new unit will always be the last one in the array
	def unitCreate(self, unitType, toX, toY):
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
		for UNIT in self.UNITARRAY: 	#shifts all tanks situated after the deleted one in the array, since the MOVEQUEUE position is tracked by arrayPos
			if deletedUnit.arrayPos < UNIT.arrayPos:
				UNIT.arrayPos -= 1
		
	#saves a move and checks for the previous move undo
	def moveStore(self, toX, toY):
		Position = self.SELECTEDUNIT.arrayPos
		moveLength = len(self.MOVEQUEUE[Position])-1
		X = self.MOVEQUEUE[Position][moveLength][0]
		Y = self.MOVEQUEUE[Position][moveLength][1]
		if [X+toX, Y+toY] == [self.MOVEQUEUE[Position][moveLength-1][0], self.MOVEQUEUE[Position][moveLength-1][1]]:
			del self.MOVEQUEUE[Position][moveLength]
		elif [X+toX, Y+toY] in self.MOVEQUEUE[Position]:	#unit cannot move through the same position twice
			pass
		elif moveLength >= self.SELECTEDUNIT.statSpeed:
			pass
		elif [X+toX, Y+toY] not in Map0.MOARRAY[X, Y]:
			self.MOVEQUEUE[Position].append([X+toX, Y+toY])
	
	#resolves situations when 2 or more units are trying to take the same final position
	def moveResolveCollision(self):
		for UNIT in self.UNITARRAY:
			if len(self.MOVEQUEUE[UNIT.arrayPos]) > 1: #checking all units which are moving this turn
				for unit in self.UNITARRAY:
					if UNIT != unit:
						finalUNITpos = self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
						finalunitpos = self.MOVEQUEUE[unit.arrayPos][len(self.MOVEQUEUE[unit.arrayPos])-1]
						if finalUNITpos == finalunitpos and len(self.MOVEQUEUE[unit.arrayPos]) < 2:	#moving unit can't take the position of the immobile unit
							del self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
						elif finalUNITpos == finalunitpos and len(self.MOVEQUEUE[UNIT.arrayPos]) > len(self.MOVEQUEUE[unit.arrayPos]):	#if one unit moved less than the other it will take the position
							del self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
						elif finalUNITpos == finalunitpos and len(self.MOVEQUEUE[UNIT.arrayPos]) < len(self.MOVEQUEUE[unit.arrayPos]):	#if one unit moved less than the other it will take the position
							del self.MOVEQUEUE[unit.arrayPos][len(self.MOVEQUEUE[unit.arrayPos])-1]
						elif finalUNITpos == finalunitpos and len(self.MOVEQUEUE[UNIT.arrayPos]) == len(self.MOVEQUEUE[unit.arrayPos]):	#if both units moved the same distance
							if UNIT.statSpeed > unit.statSpeed:
								del self.MOVEQUEUE[unit.arrayPos][len(self.MOVEQUEUE[unit.arrayPos])-1]
							elif UNIT.statSpeed < unit.statSpeed:
								del self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
							else:	#if both units traveled same distance and have the same speed noone will take the final position
								del self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
								del self.MOVEQUEUE[unit.arrayPos][len(self.MOVEQUEUE[unit.arrayPos])-1]
								
	def moveClearMoveQueue(self, unit):
		del self.MOVEQUEUE[unit.arrayPos][1:len(self.MOVEQUEUE[unit.arrayPos])]
	
	#moves all units according to their movement queues in MOVEQUEUE
	def unitMove(self):
		self.moveResolveCollision()
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
			self.moveClearMoveQueue(UNIT)
	
	def unitSelect(self):
		self.SELECTEDUNIT = Map0.getUnit(Map0.MAPSELECT.statCoord)

#------------------------------------------
		
class Unit(object):
	statCoord = [0, 0]
	statHealth = 10
	statArmor = 0
	statSpeed = 5
	statVR = 6
	arrayPos = 0
	
class Scout(Unit):
	pass
		
class Tank(Unit):
	statDamage = 10
	statFR = 4
	statAmmoCap = 10
	targetedUnit = -1
		
	def unitTargetChange(self):
		if self.statAmmoCap != 0:
			targetedUnit = Map0.getUnit(Map0.MAPSELECT.statCoord)
			if targetedUnit != -1 and targetedUnit != Unit0.SELECTEDUNIT:
				if Map0.getDistance(self.statCoord, targetedUnit.statCoord) <= Unit0.SELECTEDUNIT.statFR:
					self.targetedUnit = targetedUnit
					Input0.setState(1)

class Artillery(Unit):
	statDamage = 10
	statMinFR = 2
	statMaxFR = 10
	statAmmoCap = 10
	targetedCoord = [None]
	
	def unitTargetChange(self):
		if self.statAmmoCap != 0:
			targetedCoord = [Map0.MAPSELECT.statCoord[0], Map0.MAPSELECT.statCoord[1]]
			if Map0.getDistance(self.statCoord, targetedCoord) > Unit0.SELECTEDUNIT.statMinFR and Map0.getDistance(self.statCoord, targetedCoord) <= Unit0.SELECTEDUNIT.statMaxFR:
				self.targetedCoord = [targetedCoord[0], targetedCoord[1]]
				Input0.setState(1)
		
class Engineer(Unit):
	statDamage = 5
	statFR = 5

#------------------------------------------
		
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
		Event0.eventAdd("EventUnitCreate", ("Tank", [1, 3]))
		Event0.eventAdd("EventUnitCreate", ("Artillery", [3, 1]))
		Event0.eventAdd("EventUnitCreate", ("Tank", [0, 0]))
		Event0.eventHandle()

StartShenanigans = Main()