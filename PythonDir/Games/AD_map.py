import pygame, sys, math

class MapManager(object):
	MAP = []
	NEIGHBOURS = {}
	MOARRAY = []
	VOARRAY = []
	
	def defineGlobals(self, DrawingManager, UnitManager):
		global Window0, Unit0
		Window0 = DrawingManager
		Unit0 = UnitManager
		
		self.createMap()
	
	def __init__(self):
		#this is currently the only way to add Movement Obsticles
		self.MOARRAY.append([1, 0])
		self.MOARRAY.append([-1, 0])
		self.MOARRAY.append([-1, 1])
		self.MOARRAY.append([0, 1])
		self.MOARRAY.append([0, -2])
		self.MOARRAY.append([-2, 2])
		self.MOARRAY.append([2, 0])
		self.MOARRAY.append([3, 0])
		self.MOARRAY.append([4, 0])
		self.MOARRAY.append([-1, -1])
		self.MOARRAY.append([1, -2])
	
	#generates a graph of all possible transitions from one tile to another
	def createMap(self):
		self.DIRECTIONS = [[-1, 0], [-1, +1], [0, +1],
										[+1, 0], [+1, -1], [0, -1]]
	
		for Q in range(-Window0.MAPRADIUS, Window0.MAPRADIUS+1):
			for R in range(-Window0.MAPRADIUS, Window0.MAPRADIUS+1):
				if self.getDistance([Q, R], [0, 0]) > Window0.MAPRADIUS:
					continue
				self.MAP.append([Q, R])
				self.NEIGHBOURS[Q, R] = []
				for hex in self.DIRECTIONS:
					newHex = [Q+hex[0], R+hex[1]]
					if self.getDistance(newHex, [0, 0]) <= Window0.MAPRADIUS:
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
		N = self.getDistance(origin, target)
		if N != 0:	div = 1/float(N)
		else:		div = 0
		result = []
		
		#if your target is outside the map the line will go to the closest to your target hex
		for i in range(0, N+1):
			Q =  float(origin[0]) + float(target[0] - origin[0]) * div * i
			R = float(origin[1]) + float(target[1] - origin[1]) * div * i
			
			hex = Window0.hexRound([Q, R])
			if hex not in self.MAP:
				continue
			result.append(hex)
		return result
	
	#returns a hexes in a ring of a given radius; width=0 returns the entire circle
	def getRing(self, limit, coord = [0, 0], width = 1, MO = False):
		frontier = [[coord[0], coord[1]]]
		current = frontier[0]
		visited = {}
		visited[coord[0], coord[1]] = 0
		
		while True:
			for next in self.NEIGHBOURS[current[0], current[1]]:
				if not visited.has_key((next[0], next[1])) and not (next in self.MOARRAY and MO):
					frontier.append(next)
					visited[next[0], next[1]] = visited[current[0], current[1]] + 1
			del frontier[0]
			current = frontier[0]
			if visited[current[0], current[1]] == limit or len(frontier) == 0:
				break
			
		if width == 1:
			return frontier
		elif width == 0:
			return visited
	
	#returns a unit in a given coordiante if it's there, otherwise returns None
	def getUnit(self, coord):
		for UNIT in Unit0.UNITARRAY:
			if [UNIT.statCoord[0], UNIT.statCoord[1]] == [coord[0], coord[1]]:
				return UNIT
		return None
	
	def getPath(self, limit, origin, target):
		frontier = [[origin[0], origin[1]]]
		current = frontier[0]
		came_from = {}
		came_from[origin[0], origin[1]] = [[None], 0]
		
		while True:
			for next in self.NEIGHBOURS[current[0], current[1]]:
				if not came_from.has_key((next[0], next[1])) and next not in self.MOARRAY:
					frontier.append(next)
					depth = came_from[current[0], current[1]][1] + 1
					came_from[next[0], next[1]] = [[current[0], current[1]], depth]
			del frontier[0]
			current = frontier[0]
			depth = came_from[current[0], current[1]][1]
			if depth >= limit or len(frontier) == 0 or current == target:
				break

		#if your target is outside the limit pathfinder will rather make a path to the closest to your target hex
		if not came_from.has_key((target[0], target[1])):
			line = self.getLine(origin, target)
			for hex in line[::-1]:
				if came_from.has_key((hex[0], hex[1])):
					target = hex
					break
		
		current = target
		path = [current]
		while current != origin:
			current = came_from[current[0], current[1]][0]
			path.append(current)
		return path
		
	def getVisibility(self, limit, coord):
		isVisible = []
		pixelOrigin = Window0.hextopixel(coord)
		
		for target in self.getRing(limit, coord, 0):
			breakFlag = 0
			pixelTarget = Window0.hextopixel(target)
		
			N = self.getDistance(coord, target)
			pixelN = [pixelOrigin[0]-pixelTarget[0], pixelOrigin[1]-pixelTarget[1]]
			if N != 0:	pixelDiv = [float(pixelN[0])/N, float(pixelN[1])/N]
			else:		pixelDiv = [0, 0]
		
			for i in range(0, N+1):	
				Q = pixelOrigin[0] - int(pixelDiv[0]*i)
				R = pixelOrigin[1] - int(pixelDiv[1]*i)
				hexr = (R - Window0.POINTCENTER[1]) / (Window0.CELLSIZE/2 * 1.5)
				hexq = (Q - Window0.POINTCENTER[0]) / (Window0.CELLSIZE/2 * math.sqrt(3)) - hexr*0.5
				
				rq = round(hexq)
				rr = round(hexr)
				rs = round(-hexq-hexr)
				
				dq = abs(rq - hexq)
				dr = abs(rr - hexr)
				ds = abs(rs + hexq + hexr)
				
				if dq > ds and dq > dr:
					rq = -rs-rr
				elif ds > dr:
					pass
				else:
					rr = -rq-rs
				
				if [rq, rr] in self.MOARRAY:
					break
				breakFlag += 1
			
			if breakFlag == N+1:
				isVisible.append([target[0], target[1]])
		
		return isVisible