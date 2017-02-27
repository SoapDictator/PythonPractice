import pygame, sys, math
from pygame.locals import *

class UnitManager(object):
	global SELECTEDUNIT
	UNITARRAY = []	#array of ALL units on the map
	MOVEQUEUE = []	#array of ALL movement queues of ALL units, position of the movement queue is determined by a unit's position in UNITARRAY
	SELECTEDUNIT = None	#currently selected unit, default value is "-1"; needs to be reseted after the unit is deselected
	
	def defineGlobals(self, DrawingManager, MapManager):
		global Window0, Map0
		Window0 = DrawingManager
		Map0 = MapManager
	
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
	
	#resolves situations when 2 or more units are trying to take the same final position
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
			del self.MOVEQUEUE[UNIT.arrayPos][1:len(self.MOVEQUEUE[UNIT.arrayPos])]

#------------------------------------------
		
class Unit(object):
	statCoord = [0, 0]
	statHealth = 10
	statArmor = 0
	statSpeed = 5
	statVR = 3
	arrayPos = 0
	
class Scout(Unit):
	pass
		
class Tank(Unit):
	statDamage = 10
	statFR = 3
	statAmmoCap = 10
	targetedUnit = None
		
	def targetChange(self, coord):
		if self.statAmmoCap != 0:
			targetedUnit = Map0.getUnit(coord)
			if targetedUnit != None and targetedUnit != SELECTEDUNIT:
				if Map0.getDistance(self.statCoord, targetedUnit.statCoord) <= SELECTEDUNIT.statFR:
					self.targetedUnit = targetedUnit
					return True
		return False

class Artillery(Unit):
	statDamage = 10
	statMinFR = 2
	statMaxFR = 5
	statAmmoCap = 10
	targetedCoord = [None]
	
	def targetChange(self, coord):
		if self.statAmmoCap != 0:
			targetedCoord = [coord[0], coord[1]]
			if Map0.getDistance(self.statCoord, targetedCoord) > SELECTEDUNIT.statMinFR and Map0.getDistance(self.statCoord, targetedCoord) <= SELECTEDUNIT.statMaxFR:
				self.targetedCoord = targetedCoord
				return True
		return False
		
class Engineer(Unit):
	statDamage = 5
	statFR = 5