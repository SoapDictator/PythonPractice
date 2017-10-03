import sys, math, pygame
from AD_unit import *

class DrawingManager(object):
	FPS = 0
	FPSCLOCK = 0
	WINDOWWIDTH = 0
	WINDOWHEIGHT = 0
	DISPLAYSURF = 0
	BASICFONT = 0
	
	SCROLL = [0, 0]
	SCROLLSPEED = 10
	
	COLORMAP = {}
	
	GUI = None
	
	def defineGlobals(self, InputManager, MapManager, UnitManager):
		global INPUT0, MAP0, UNIT0, WINDOW0
		INPUT0 = InputManager
		MAP0 = MapManager
		UNIT0 = UnitManager
		WINDOW0 = self
		self.GUI = GUI()
	
	def __init__(self):
		self.screenConfig()
		self.screenColors()
		
		pygame.init()
		self.FPSCLOCK = pygame.time.Clock()
		self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
		self.BASICFONT = pygame.font.Font('freesansbold.ttf', 12)
		pygame.display.set_caption('AD')
		
		h = float(self.CELLSIZE)
		w = math.sqrt(3)/2 * h
		self.PIXELPOINTS =	[[0, 0.5*h], [0.5*w, 0.25*h], [0.5*w, -0.25*h], 
										[0, -0.5*h], [-0.5*w, -0.25*h], [-0.5*w, 0.25*h]]
		self.PIXELEDGES =	[[-0.25*w, 0.375*h], [-0.5*w, 0], [-0.25*w, -0.375*h], 
										[0.25*w, -0.375*h], [0.5*w, 0], [0.25*w, 0.375*h]]

	#takes settings frrom config.txt
	def screenConfig(self):
		config = open("config.txt", "r")
		for line in config:
			if "FPS = " in line:
				self.FPS = float(line[6:9])
			elif "WINDOWWIDTH = " in line:
				self.WINDOWWIDTH = int(line[14:])
			elif "WINDOWHEIGHT = " in line:
				self.WINDOWHEIGHT = int(line[15:])
			elif "CELLSIZE = " in line:
				self.CELLSIZE = int(line[11:])
			elif "MAPRADIUS = " in line:
				self.MAPRADIUS = int(line[12:])

		self.CELLWIDTH = int(self.WINDOWWIDTH / self.CELLSIZE)
		self.CELLHEIGHT = int(self.WINDOWHEIGHT / self.CELLSIZE)
		
		self.POINTCENTER = [self.WINDOWWIDTH/2, self.WINDOWHEIGHT/2]
	
	def screenColors(self):
		#									R		G		B
		self.WHITE				= (255,	255,	255)
		self.BLACK				= (0,		0,		0)
		self.LIGHTBLUE			= (180,	180,	255)
		self.BLUE					= (120,	120,	255)
		self.LIGHTRED			= (205,	92,	92)
		self.RED					= (220,	0,		0)
		self.DARKRED			= (120,	0,		0)
		self.GREEN				= (34,	180,	34)
		self.YELLOW				= (220,	220,	0)
		self.GREENYELLOW		= (173,	220,	47)
		self.LIGHTGRAY			= (150,	150,	150)
		self.DARKGREY			= (60,	60,	60)
		self.BGCOLOR			= self.DARKGREY
		
	def hextopixel(self, hex):
		x = self.SCROLL[0] + self.POINTCENTER[0] + self.CELLSIZE/2 * math.sqrt(3) * (hex[0] +hex[1]*0.5)
		y = self.SCROLL[1] + self.POINTCENTER[1] + self.CELLSIZE/2 * 1.5 * hex[1]
		return [int(x), int(y)]
		
	def pixeltohex(self, pixelHex):
		y = (pixelHex[1] - self.SCROLL[1] - self.POINTCENTER[1]) / (self.CELLSIZE/2 * 1.5)
		x = (pixelHex[0] - self.SCROLL[0] - self.POINTCENTER[0]) / (self.CELLSIZE/2 * math.sqrt(3)) - y*0.5
		return self.hexRound([x, y])
		
	def screenScroll(self, scroll):
		self.SCROLL[0] += scroll[0]*self.SCROLLSPEED
		self.SCROLL[1] += scroll[1]*self.SCROLLSPEED
	
	#takes float hex coordinates and rounds it to the nearest hex
	def hexRound(self, hex):
		rx = round(hex[0])
		ry = round(-hex[0]-hex[1])	#since axial coordinates are used Y has to be calculated
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
			
		return [int(rx), int(rz)]
	
	#draws a single hex; width=1 will draw an outline, width=0 draws a solid figure
	def drawHex(self, hex, color = [255, 255, 255], width = 1):
		pixelhex = self.hextopixel(hex)
		points = []
		
		for i in range(0, 6):
			points.append([pixelhex[0]+self.PIXELPOINTS[i][0], 
									pixelhex[1]+self.PIXELPOINTS[i][1]])
		if width == 0:
			pygame.draw.polygon(self.DISPLAYSURF, color, points, width)
		else:
			pygame.draw.aalines(self.DISPLAYSURF, color, True, points, width)
	
	#draws a direct line from origin to target
	def drawLine(self, origin, target, color = [255, 255, 255]):
		pixelOrigin = self.hextopixel(origin)
		pixelTarget = self.hextopixel(target)
		
		N = MAP0.getDistance(origin, target)
		pixelN = [pixelOrigin[0]-pixelTarget[0],pixelOrigin[1]-pixelTarget[1]]
		if N != 0:	pixelDiv = [float(pixelN[0])/N, float(pixelN[1])/N]
		else:		pixelDiv = [0, 0]
		
		pygame.draw.aaline(self.DISPLAYSURF, color, pixelOrigin, pixelTarget, 1)
		for i in range(0, N+1):
			X = pixelOrigin[0] - int(pixelDiv[0]*i)
			Y = pixelOrigin[1] - int(pixelDiv[1]*i)
			pygame.draw.circle(self.DISPLAYSURF, color, [X, Y], 3)
	
	#draws all hexes or their outlines fitting on the screen using one color
	def drawGrid(self, color = [255, 255, 255], width = 1):
		hexStart = self.pixeltohex([-self.CELLSIZE, -self.CELLSIZE])
		hexStop = self.pixeltohex([self.WINDOWWIDTH+self.CELLSIZE, self.WINDOWHEIGHT+self.CELLSIZE])
		
		for hex in MAP0.getRectangle(hexStart, hexStop):
			if width == 1:
				pixelhex = self.hextopixel(hex)
				points = []
				if MAP0.getDistance(hex, [0, 0]) != 20:
					for i in range(2, 6):
						points.append([pixelhex[0]+self.PIXELPOINTS[i][0], 
												pixelhex[1]+self.PIXELPOINTS[i][1]])
					pygame.draw.aalines(self.DISPLAYSURF, color, False, points, width)
				#need a couple checks to only draw missing lines on the map edges
				else:
					self.drawHex(hex, color, width)
			else:
				self.drawHex(hex, self.COLORMAP[hex[0], hex[1]], width)
			#displays the coordinates on the hex itself
			#if width == 1:
				#textsurf = self.BASICFONT.render('%s, %s' % (q+offset2, r), True, self.WHITE)
				#textrect = textsurf.get_rect()
				#textrect.center = (self.hextopixel([q+offset2, r]))
				#self.DISPLAYSURF.blit(textsurf, textrect)
	
	def colorMapReset(self):
		for hex in MAP0.MAP:
			self.COLORMAP[hex[0], hex[1]] = self.LIGHTGRAY
	
	def colorMapInsert(self, hex, color):
		self.COLORMAP[hex[0], hex[1]] =  color
		
	#draws EVERYTHING again on each frame
	def screenRefresh(self):			
		#fills the background with a single color
		self.DISPLAYSURF.fill(self.BGCOLOR)
		self.colorMapReset()
		unitSelected = UNIT0.getUnitSelected()
		playerSelectedID = UNIT0.getPlayerSelectedID()
		
		#draws visible for the selected player hexes
		for hex in UNIT0.getPlayerFOV(UNIT0.getPlayerSelectedID()):
			self.colorMapInsert(hex, (200, 200, 200))
		
		#draws possible movement options and a calculated path to chosen destination
		if INPUT0.getState() == 'unitSelected' and unitSelected != None:
			speed = unitSelected.statCur["SPD"]
			coord = unitSelected.getCoord()
			for hex in MAP0.getRing(speed, coord, width = 0, MO = True):
				self.colorMapInsert(hex, self.LIGHTBLUE)
			for hex in MAP0.getPath(speed, coord, self.pixeltohex(pygame.mouse.get_pos())):
				self.colorMapInsert(hex, self.BLUE)
		
		#draws all hexes a selected unit can attack
		if INPUT0.getState() == 'unitTarget' and unitSelected != None:
			if UNIT0.isTank(unitSelected) or UNIT0.isArti(unitSelected):
				#INPUT0.setState(1)
			
				tempMaxArea = MAP0.getRing(unitSelected.statCur["FRmax"], unitSelected.getCoord(), width = 0)
				tempMinArea = MAP0.getRing(unitSelected.statCur["FRmin"], unitSelected.getCoord(), width = 0)
				for hex in tempMaxArea:
					#we don't need to draw tiles unit can't attack because of min Fire Range
					if hex not in tempMinArea:
						self.colorMapInsert(hex, self.LIGHTRED)
		
		#draws all MOs
		for hex in MAP0.MOARRAY:
			self.colorMapInsert(hex, self.DARKGREY)
		
		#draws units visible for the selected player
		for unit in UNIT0.getAllUnits():
			if unit.getOwner() == playerSelectedID:
				self.colorMapInsert(unit.statCoord, self.GREENYELLOW)
			else:
				if unit.getCoord() in UNIT0.getPlayerFOV(UNIT0.getPlayerSelectedID()):
					#redraws the units with a different color so they're visible during unit's attack targeting
					if INPUT0.getState() == 'unitTarget':
						self.colorMapInsert(unit.statCoord, self.RED)
					else:
						self.colorMapInsert(unit.statCoord, self.LIGHTRED)
		
		#simply draws a hex grid of all hexes on the map
		self.drawGrid(width = 0)
		self.drawGrid()
		if unit != None:
			self.GUI.drawSelf()
		
		#draws movement queues and attack targets for owned units
		for unit in UNIT0.getAllUnits():
			if unit.getOwner() == UNIT0.getPlayerSelected():
				if unit.targetedUnit != None:
					if UNIT0.isTank(unit):
						self.drawLine(unit.getCoord(), unit.getTarget().statCoord, self.RED)
					elif UNIT0.isArti(unit):
						self.drawLine(unit.getCoord(), unit.getTarget(), self.RED)
				
				path = unit.getMoveQueue()
				for i in range(1, len(path)):
					self.drawLine(path[i-1], path[i], self.BLUE)
		
		pygame.display.update()
		self.FPSCLOCK.tick(self.FPS)
		
class GUI(object):
	wCommB = 0	#button size
	wCommPad = 0	#padding between buttons
	wCommEdge = 0	#edge of the gui window
	
	def __init__(self):
		self.wCommB = WINDOW0.WINDOWWIDTH*0.06
		self.wCommPad = 6
		self.wCommEdge = 2
			
	def defButtons(self):
		unit = UNIT0.getUnitSelected()
		wCommButtons = []
		
		if unit != None:			
			wCommButtons.append("Cancel")
			if len(unit.statAbilities) > 0:
				for ability in unit.instAbilities:
					wCommButtons.append(ability.statName)
			if unit.statCur["SPD"] > 0:
				wCommButtons.append("Move")
			if unit.statCur["FRmax"] > 0:
				wCommButtons.append("Attack")
		return wCommButtons
	
	def drawSelf(self):
		#drawing background for unit command buttons
		wCommButtons = self.defButtons()
		bNum = len(wCommButtons)
		
		wCommW = WINDOW0.WINDOWWIDTH - bNum*self.wCommB - (bNum+1)*self.wCommPad - self.wCommEdge
		wCommH = WINDOW0.WINDOWHEIGHT - self.wCommB - self.wCommPad - 2*self.wCommEdge
		guiRect = pygame.Rect(wCommW, wCommH, WINDOW0.WINDOWWIDTH-wCommW-self.wCommEdge, WINDOW0.WINDOWHEIGHT-wCommH-self.wCommEdge)
		
		pygame.draw.rect(WINDOW0.DISPLAYSURF, WINDOW0.DARKGREY, guiRect)
		pygame.draw.rect(WINDOW0.DISPLAYSURF, WINDOW0.WHITE, guiRect, self.wCommEdge)
		
		#drawing the unit command buttons
		for i in range(0, bNum):
			buttonW = WINDOW0.WINDOWWIDTH-self.wCommB*(i+1) -self.wCommPad*(i+1) -self.wCommEdge
			buttonH = WINDOW0.WINDOWHEIGHT-self.wCommB -self.wCommPad
			buttonRect = pygame.Rect(buttonW, buttonH, self.wCommB, self.wCommB)
			
			pygame.draw.rect(WINDOW0.DISPLAYSURF, WINDOW0.LIGHTGRAY, buttonRect)
			pygame.draw.rect(WINDOW0.DISPLAYSURF, WINDOW0.WHITE, buttonRect, self.wCommEdge)
			
			textsurf = WINDOW0.BASICFONT.render('%s' % wCommButtons[i], True, WINDOW0.WHITE)
			textrect = textsurf.get_rect()
			textrect.center = ([buttonW+self.wCommB/2, buttonH+self.wCommB/2])
			WINDOW0.DISPLAYSURF.blit(textsurf, textrect)