import pygame, sys, math
from pygame.locals import *

class UnitManager(object):
	UNITARRAY = []	#array of ALL units on the map
	MOVEQUEUE = []	#array of ALL movement queues of ALL units, position of the movement queue is determined by a unit's position in UNITARRAY
	SCOUTS = []
	TANKS = []
	ARTILLERY = []
	ENGINEERS = []
	
	PLAYERARRAY = {}	#array of all players; defines unit ownership
	SELECTEDPLAYER = None
	SELECTEDUNIT = None	#currently selected unit; needs to be reseted after the unit is deselected
	
	PLAYERFOV = [[], []]
	
	def __init__(self):
		self.PLAYERARRAY["player1"] = 0
		self.PLAYERARRAY["player2"] = 1
		self.SELECTEDPLAYER = self.PLAYERARRAY["player1"]
	
	def defineGlobals(self, DrawingManager, MapManager, UnitManager):
		global Window0, Map0, Unit0
		Window0 = DrawingManager
		Map0 = MapManager
		Unit0 = UnitManager
	
	#creates a new unit and adds it to the UNITARRAY as well as creates an entry in MOVEQUEUE; new unit will always be the last one in the array
	def unitCreate(self, unitType, coord, player):
		toX = coord[0]
		toY = coord[1]
		if unitType == "Scout":
			NewUnit = Scout()
			self.SCOUTS.append(NewUnit)
		elif unitType == "Tank":
			NewUnit = Tank()
			self.TANKS.append(NewUnit)
		elif unitType == "Artillery":
			NewUnit = Artillery()
			self.ARTILLERY.append(NewUnit)
		elif unitType == "Engineer":
			NewUnit = Engineer()
			self.ENGINEERS.append(NewUnit)
		NewUnit.owner = player
		self.UNITARRAY.append(NewUnit)
		NewUnit.arrayPos = len(self.UNITARRAY)-1
		
		NewUnit.statCoord = [toX, toY]
		self.MOVEQUEUE.append([[toX, toY]])
	
	def unitDestroy(self, deletedUnit):
		del self.UNITARRAY[deletedUnit.arrayPos]
		del self.MOVEQUEUE[deletedUnit.arrayPos]
		for UNIT in self.UNITARRAY: 
			if deletedUnit.arrayPos < UNIT.arrayPos:	#shifts all tanks situated after the deleted one in the array, since the MOVEQUEUE position is tracked by arrayPos
				UNIT.arrayPos -= 1
		for i in range(0, 50):	#ducktape to delete the unit from the according type array
			if i < len(self.SCOUTS):
				if deletedUnit == self.SCOUTS[i]:
					del self.SCOUTS[i]
					break
			if i < len(self.TANKS):
				if deletedUnit == self.TANKS[i]:
					del self.TANKS[i]
					break
			if i < len(self.ARTILLERY):
				if deletedUnit == self.ARTILLERY[i]:
					del self.ARTILLERY[i]
					break
			if i < len(self.ENGINEERS):
				if deletedUnit == self.ENGINEERS[i]:
					del self.ENGINEERS[i]
					break
	
	#resolves situations when 2 or more units are trying to travel to the same final position
	def moveResolveCollision(self):
		for UNIT in self.UNITARRAY:
			#checking all units which are moving this turn
			if len(self.MOVEQUEUE[UNIT.arrayPos]) > 1: 
				for unit in self.UNITARRAY:
					if UNIT != unit:
						finalUNITpos = self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
						finalunitpos = self.MOVEQUEUE[unit.arrayPos][len(self.MOVEQUEUE[unit.arrayPos])-1]
						#moving unit can't take the position of the immobile unit
						if finalUNITpos == finalunitpos and len(self.MOVEQUEUE[unit.arrayPos]) < 2:
							del self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
						#if one unit moved less than the other it will take the position
						elif finalUNITpos == finalunitpos and len(self.MOVEQUEUE[UNIT.arrayPos]) > len(self.MOVEQUEUE[unit.arrayPos]):
							del self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
						#if one unit moved less than the other it will take the position
						elif finalUNITpos == finalunitpos and len(self.MOVEQUEUE[UNIT.arrayPos]) < len(self.MOVEQUEUE[unit.arrayPos]):
							del self.MOVEQUEUE[unit.arrayPos][len(self.MOVEQUEUE[unit.arrayPos])-1]
						#if both units moved the same distance						
						elif finalUNITpos == finalunitpos and len(self.MOVEQUEUE[UNIT.arrayPos]) == len(self.MOVEQUEUE[unit.arrayPos]):
							if UNIT.statSpeed > unit.statSpeed:
								del self.MOVEQUEUE[unit.arrayPos][len(self.MOVEQUEUE[unit.arrayPos])-1]
							elif UNIT.statSpeed < unit.statSpeed:
								del self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
							#if both units traveled same distance and have the same speed noone will take the final position
							else:
								del self.MOVEQUEUE[UNIT.arrayPos][len(self.MOVEQUEUE[UNIT.arrayPos])-1]
								#del self.MOVEQUEUE[unit.arrayPos][len(self.MOVEQUEUE[unit.arrayPos])-1]
	
	#moves units according to their movement queues in MOVEQUEUE
	def unitMove(self, units):
		self.moveResolveCollision()
		stopFlag = [0]*len(self.MOVEQUEUE)
		sum = 0
		for step in range(1, 50):
			for UNIT in units:
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
			if sum == len(units):
				break
			sum = 0
			pygame.time.wait(75)
			Window0.screenRefresh()
		
		for UNIT in units:
			self.MOVEQUEUE[UNIT.arrayPos][0] = [UNIT.statCoord[0], UNIT.statCoord[1]]
			del self.MOVEQUEUE[UNIT.arrayPos][1:len(self.MOVEQUEUE[UNIT.arrayPos])]
	
	def unitFOV(self):
		for unit in self.UNITARRAY:
			for hex in Map0.getVisibility(unit.statVR, unit.statCoord):
				if hex not in self.PLAYERFOV[self.PLAYERARRAY[unit.owner]]:
					self.PLAYERFOV[self.PLAYERARRAY[unit.owner]].append(hex)

#------------------------------------------
		
class Unit(object):
	statCoord = [0, 0]
	arrayPos = 0
	owner = None
	
class Scout(Unit):
	statMaxHP = 6
	statHP = statMaxHP
	statArmor = 0
	statSpeed = 5
	statVR = 5
		
class Tank(Unit):
	statMaxHP = 10
	statHP = statMaxHP
	statArmor = 2
	statSpeed = 4
	statVR = 3
	statDamage = 10
	statFR = 3
	statAmmoCap = 10
	targetedUnit = None
		
	def targetChange(self, coord):
		if self.statAmmoCap != 0:
			if Map0.getDistance(self.statCoord, coord) <= self.statFR and coord in Unit0.PLAYERFOV[0]:
				targetedUnit = Map0.getUnit(coord)
				if targetedUnit != None and targetedUnit != self:
					self.targetedUnit = targetedUnit
					return True
		return False

class Artillery(Unit):
	statMaxHP = 8
	statHP = statMaxHP
	statArmor = 0
	statSpeed = 4
	statVR = 2
	statDamage = 11
	statMinFR = 2
	statMaxFR = 5
	statAmmoCap = 10
	targetedCoord = [None]
	
	def targetChange(self, coord):
		if self.statAmmoCap != 0:
			targetedCoord = [coord[0], coord[1]]
			dist = Map0.getDistance(self.statCoord, targetedCoord)
			if dist > self.statMinFR and dist <= self.statMaxFR:
				self.targetedCoord = targetedCoord
				return True
		return False
		
class Engineer(Unit):
	statMaxHP = 12
	statHP = statMaxHP
	statArmor = 1
	statSpeed = 3
	statVR = 2
	statDamage = -5
	statFR = 3
	targetedUnit = None
	
	def targetChange(self, coord):
		if Map0.getDistance(self.statCoord, coord) <= self.statFR and coord in Unit0.PLAYERFOV[0]:
			targetedUnit = Map0.getUnit(coord)
			if targetedUnit != None and targetedUnit != self:
				self.targetedUnit = targetedUnit
				return True
		return False