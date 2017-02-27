import sys, math, pygame

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
		
		self.MAPRADIUS = 7
		self.POINTCENTER = [(0.5+self.MAPRADIUS)*math.sqrt(3)/2*self.CELLSIZE, 
										(0.5+self.MAPRADIUS*0.75)*self.CELLSIZE]
	
	def screenColors(self):
		#								R		G		B
		self.WHITE				= (255, 255, 255)
		self.BLACK				= (    0,     0,     0)
		self.LIGHTBLUE		= (180, 180, 255)
		self.BLUE					= (120, 120, 255)
		self.LIGHTRED			= (205,   92,   92)
		self.RED					= (220,     0,     0)
		self.DARKRED			= (120,     0,     0)
		self.GREEN				= (  34, 180,    34)
		self.YELLOW			= (220, 220,     0)
		self.GREENYELLOW	= (173, 220,   47)
		self.LIGHTGRAY		= (150, 150, 150)
		self.DARKGREY			= (60, 60, 60)
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
		h = float(self.CELLSIZE)
		w = 1.732*0.5 * h
		directions_pixel = [[0, 0.5*h], [0.5*w, 0.25*h], [0.5*w, -0.25*h], 
									[0, -0.5*h], [-0.5*w, -0.25*h], [-0.5*w, 0.25*h]]
		pixelhex = self.hextopixel(hex)
		points = []
		
		for i in range(0, 6):
			points.append([pixelhex[0]+directions_pixel[i][0], 
									pixelhex[1]+directions_pixel[i][1]])
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
		
	def drawGrid(self, color = [255, 255, 255], width = 1):
		for q in range(-self.MAPRADIUS, self.MAPRADIUS+1):
			r1 = max(-self.MAPRADIUS, -q-self.MAPRADIUS)
			r2 = min(self.MAPRADIUS, -q+self.MAPRADIUS)
			
			for r in range(r1, r2+1):
				self.drawHex([q, r], color, width)

	#draws EVERYTHING again on each frame
	def screenRefresh(self):
		self.DISPLAYSURF.fill(self.BGCOLOR)
		self.drawGrid(self.LIGHTGRAY, 0)
		
		for unit in Unit0.UNITARRAY:
			for hex in Map0.getVisibility(unit.statVR, unit.statCoord):
				self.drawHex(hex, (200, 200, 200), 0)
		
		if Input0.getState() == 'unitSelected':
			for hex in Map0.getRing(Unit0.SELECTEDUNIT.statSpeed, Unit0.SELECTEDUNIT.statCoord, width = 0, MO = True):
				self.drawHex(hex, self.LIGHTBLUE, 0)
			for hex in Map0.getPath(Unit0.SELECTEDUNIT.statSpeed, Unit0.SELECTEDUNIT.statCoord, self.pixeltohex(pygame.mouse.get_pos())):
				self.drawHex(hex, self.BLUE, 0)
					
		if Input0.getState() == 'unitTarget':
			for hex in Map0.getRing(Unit0.SELECTEDUNIT.statFR, Unit0.SELECTEDUNIT.statCoord, width = 0):
				self.drawHex(hex, self.LIGHTRED, 0)
		
		for hex in Map0.MOARRAY:
			self.drawHex(hex, self.DARKGREY, 0)
		
		for unit in Unit0.UNITARRAY:
			self.drawHex(unit.statCoord, self.GREENYELLOW, 0)
			
		if Input0.getState() == 'unitTarget':
			for hex in Map0.getRing(Unit0.SELECTEDUNIT.statFR, Unit0.SELECTEDUNIT.statCoord, width = 0):
				if Map0.getUnit(hex) != None and [hex[0], hex[1]] != Unit0.SELECTEDUNIT.statCoord:
					self.drawHex(hex, self.RED, 0)
		
		self.drawGrid()
		
		pygame.display.update()