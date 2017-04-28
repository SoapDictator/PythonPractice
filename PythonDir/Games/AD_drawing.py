import sys, math, pygame
from AD_unit import *

class DrawingManager(object):
	FPS = 0
	FPSCLOCK = 0
	WINDOWWIDTH = 0
	WINDOWHEIGHT = 0
	DISPLAYSURF = 0
	BASICFONT = 0
	
	def defineGlobals(self, InputManager, MapManager, UnitManager):
		global Input0, Map0, Unit0
		Input0 = InputManager
		Map0 = MapManager
		Unit0 = UnitManager
	
	def __init__(self):
		self.screenConfig()
		self.screenColors()
		
		pygame.init()
		self.FPSCLOCK = pygame.time.Clock()
		self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
		self.BASICFONT = pygame.font.Font('freesansbold.ttf', 12)
		pygame.display.set_caption('AD')
		
		h = float(self.CELLSIZE)
		w = 1.732*0.5 * h
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
		
		#assert self.WINDOWWIDTH % self.CELLSIZE == 0
		#assert self.WINDOWHEIGHT % self.CELLSIZE == 0

		self.CELLWIDTH = int(self.WINDOWWIDTH / self.CELLSIZE)
		self.CELLHEIGHT = int(self.WINDOWHEIGHT / self.CELLSIZE)
		
		self.POINTCENTER = [(0.5+self.MAPRADIUS)*math.sqrt(3)/2*self.CELLSIZE, 
										(0.5+self.MAPRADIUS*0.75)*self.CELLSIZE]
	
	def screenColors(self):
		#									R		G		B
		self.WHITE				= (255, 255, 255)
		self.BLACK				= (    0,     0,     0)
		self.LIGHTBLUE		= (180, 180, 255)
		self.BLUE					= (120, 120, 255)
		self.LIGHTRED			= (205,   92,   92)
		self.RED					= (220,     0,     0)
		self.DARKRED			= (120,     0,     0)
		self.GREEN				= (  34, 180,   34)
		self.YELLOW			= (220, 220,     0)
		self.GREENYELLOW	= (173, 220,   47)
		self.LIGHTGRAY		= (150, 150, 150)
		self.DARKGREY			= (  60,   60,   60)
		self.BGCOLOR	= self.DARKGREY
		
	def hextopixel(self, hex):
		x = self.POINTCENTER[0] + self.CELLSIZE/2 * math.sqrt(3) * (hex[0] +hex[1]*0.5)
		y = self.POINTCENTER[1] + self.CELLSIZE/2 * 1.5 * hex[1]
		return [int(x), int(y)]
		
	def pixeltohex(self, pixelHex):
		y = (pixelHex[1] - self.POINTCENTER[1]) / (self.CELLSIZE/2 * 1.5)
		x = (pixelHex[0] - self.POINTCENTER[0]) / (self.CELLSIZE/2 * math.sqrt(3)) - y*0.5
		return self.hexRound([x, y])
	
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
		pygame.draw.polygon(self.DISPLAYSURF, color, points, width)
		
		#displays the coordinates on the hex itself
		textsurf = self.BASICFONT.render('%s, %s' % (hex[0], hex[1]), True, self.WHITE)
		textrect = textsurf.get_rect()
		textrect.center = (pixelhex)
		self.DISPLAYSURF.blit(textsurf, textrect)
	
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
	
	#draws all hexes or their outlines using one color
	def drawGrid(self, color = [255, 255, 255], width = 1):
		for q in range(-self.MAPRADIUS, self.MAPRADIUS+1):
			r1 = max(-self.MAPRADIUS, -q-self.MAPRADIUS)
			r2 = min(self.MAPRADIUS, -q+self.MAPRADIUS)
			
			for r in range(r1, r2+1):
				self.drawHex([q, r], color, width)
				textsurf = self.BASICFONT.render('%s, %s' % (q, r), True, self.WHITE)
				textrect = textsurf.get_rect()
				textrect.center = (self.hextopixel([q, r]))
				self.DISPLAYSURF.blit(textsurf, textrect)

	#draws EVERYTHING again on each frame
	def screenRefresh(self):
		#fills the background with a single color
		self.DISPLAYSURF.fill(self.BGCOLOR)
		#draws all hexes on the map with one color
		self.drawGrid(self.LIGHTGRAY, 0)
		
		#draws visible for the selected player hexes
		for hex in Unit0.PLAYERFOV[Unit0.SELECTEDPLAYER]:
			self.drawHex(hex, (200, 200, 200), 0)
		
		#draws possible movement options and a calculated path to chosen destination
		if Input0.getState() == 'unitSelected':
			for hex in Map0.getRing(Unit0.SELECTEDUNIT.statSpeed, Unit0.SELECTEDUNIT.statCoord, width = 0, MO = True):
				self.drawHex(hex, self.LIGHTBLUE, 0)
			for hex in Map0.getPath(Unit0.SELECTEDUNIT.statSpeed, Unit0.SELECTEDUNIT.statCoord, self.pixeltohex(pygame.mouse.get_pos())):
				self.drawHex(hex, self.BLUE, 0)
		
		#draws all hexes a selected unit can attack
		if Input0.getState() == 'unitTarget':
			if Unit0.SELECTEDUNIT in Unit0.TANKS:
				FR = Unit0.SELECTEDUNIT.statFR
			elif Unit0.SELECTEDUNIT in Unit0.ARTILLERY:
				FR = Unit0.SELECTEDUNIT.statMaxFR
			else:
				FR = 0
				
			for hex in Map0.getRing(FR, Unit0.SELECTEDUNIT.statCoord, width = 0):
				if Unit0.SELECTEDUNIT in Unit0.ARTILLERY:
					if hex in Map0.getRing(Unit0.SELECTEDUNIT.statMinFR, Unit0.SELECTEDUNIT.statCoord, width = 0):
						continue
				self.drawHex(hex, self.LIGHTRED, 0)
		
		#draws all MOs
		for hex in Map0.MOARRAY:
			self.drawHex(hex, self.DARKGREY, 0)
		
		#draws units visible for the selected player
		for unit in Unit0.UNITARRAY:
			if Unit0.PLAYERARRAY[unit.owner] == Unit0.SELECTEDPLAYER:
				self.drawHex(unit.statCoord, self.GREENYELLOW, 0)
			else:
				if unit.statCoord in Unit0.PLAYERFOV[Unit0.SELECTEDPLAYER]:
					self.drawHex(unit.statCoord, self.LIGHTRED, 0)
		
		#redraws the units with a different color so they're visible during unit's attack targeting
		if Input0.getState() == 'unitTarget':
			if Unit0.SELECTEDUNIT in Unit0.TANKS:
				FR = Unit0.SELECTEDUNIT.statFR
			elif Unit0.SELECTEDUNIT in Unit0.ARTILLERY:
				FR = Unit0.SELECTEDUNIT.statMaxFR
			else:
				FR = 0
			
			for hex in Map0.getRing(FR, Unit0.SELECTEDUNIT.statCoord, width = 0):
				if Map0.getUnit(hex) != None and [hex[0], hex[1]] != Unit0.SELECTEDUNIT.statCoord and [hex[0], hex[1]] in Unit0.PLAYERFOV[Unit0.SELECTEDPLAYER]:
					self.drawHex(hex, self.RED, 0)
					
		#draws movement queues and attack targets for owned units
		for unit in Unit0.UNITARRAY:
			if Unit0.PLAYERARRAY[unit.owner] == Unit0.SELECTEDPLAYER:
				if unit in Unit0.TANKS:
					if unit.targetedUnit != None:
						self.drawLine(unit.statCoord, unit.targetedUnit.statCoord, self.RED)
				elif unit in Unit0.ARTILLERY:
					if unit.targetedCoord != [None]:
						self.drawLine(unit.statCoord, unit.targetedCoord, self.RED)
				
				path = Unit0.MOVEQUEUE[unit.arrayPos]
				for i in range(1, len(path)):
					self.drawLine(path[i-1], path[i], self.BLUE)
		
		#simply draws a hex grid of all hexes on the map
		self.drawGrid()
		
		pygame.display.update()