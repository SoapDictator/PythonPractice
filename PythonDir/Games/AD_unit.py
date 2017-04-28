import pygame, sys, math
from pygame.locals import *

class UnitManager(object):
	#array of ALL units on the map
	UNITARRAY = []
	
	SCOUTS = []
	TANKS = []
	ARTILLERY = []
	ENGINEERS = []
	
	#array of ALL movement queues of ALL units, position of the movement queue is determined by a unit's position in UNITARRAY
	MOVEQUEUE = []
	
	#dictionary of all existing abilities; "name": priority
	ABILITYARRAY = {"A001": "EngieHeal", "A002": "ReplenishAmmo"}
	
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
		
		targetUnit = getattr(Units, unitType)
		NewUnit = targetUnit()
		self.UNITARRAY.append(NewUnit)
		
		NewUnit.owner = player
		NewUnit.arrayPos = len(self.UNITARRAY)-1
		NewUnit.statCoord = [toX, toY]
		self.MOVEQUEUE.append([[toX, toY]])
		NewUnit.instAbilities = []
		
		if len(NewUnit.statAbilities) > 0:
			for ability in NewUnit.statAbilities:
				self.unitAddAbility(ability, NewUnit)
	
	def unitDestroy(self, deletedUnit):
		arrayPos = deletedUnit.arrayPos
		
		del self.UNITARRAY[arrayPos]
		del self.MOVEQUEUE[arrayPos]
		del deletedUnit.instAbilities[:]
		
		if deletedUnit in Unit0.SCOUTS:
			del Unit0.SCOUTS[Unit0.SCOUTS.index(deletedUnit)]
		elif deletedUnit in Unit0.TANKS:
			del Unit0.TANKS[Unit0.TANKS.index(deletedUnit)]
		elif deletedUnit in Unit0.ARTILLERY:
			del Unit0.ARTILLERY[Unit0.ARTILLERY.index(deletedUnit)]
		elif deletedUnit in Unit0.ENGINEERS:
			del Unit0.ENGINEERS[Unit0.ENGINEERS.index(deletedUnit)]
		
		for UNIT in self.UNITARRAY: 
			if arrayPos < UNIT.arrayPos:	#shifts all tanks situated after the deleted one in the array, since the MOVEQUEUE position is tracked by arrayPos
				UNIT.arrayPos -= 1
	
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
				if len(self.MOVEQUEUE[UNIT.arrayPos]) <= 1:
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
			del self.MOVEQUEUE[UNIT.arrayPos][1:]
	
	def unitAddAbility(self, abilityID, caster):
		if abilityID not in self.ABILITYARRAY:
			pass
		targetAbility = getattr(Abilities, abilityID)
		instance = targetAbility(caster)
		caster.instAbilities.append(instance)
	
	def unitFOV(self):
		for unit in self.UNITARRAY:
			for hex in Map0.getVisibility(unit.statVR, unit.statCoord):
				if hex not in self.PLAYERFOV[self.PLAYERARRAY[unit.owner]]:
					self.PLAYERFOV[self.PLAYERARRAY[unit.owner]].append(hex)

#------------------------------------------
class Units:
	class Unit(object):
		statCoord = [0, 0]
		statAbilities = []
		instAbilities = []
		arrayPos = 0
		owner = None
		
		def addMoveQueue(self, queue):
			Unit0.MOVEQUEUE[self.arrayPos] = queue[:]
			
		def castAbility(self, abilityID, data):
			if abilityID not in self.statAbilities:
				pass
			ability = self.instAbilities[self.statAbilities.index(abilityID)]
			ability.activate(data)
		
	class Scout(Unit):
		statMaxHP = 6
		statHP = statMaxHP
		statArmor = 0
		statSpeed = 5
		statVR = 5
		
		def __init__(self):
			Unit0.SCOUTS.append(self)
			
	class Tank(Unit):
		statMaxHP = 10
		statHP = statMaxHP
		statArmor = 2
		statSpeed = 4
		statVR = 3
		statDamage = 10
		statFR = 3
		statAmmoCap = 10
		statAmmo = statAmmoCap
		targetedUnit = None
		
		def __init__(self):
			Unit0.TANKS.append(self)
		
		def targetChange(self, coord):
			if self.statAmmoCap != 0:
				player = Unit0.PLAYERARRAY[self.owner]
				if Map0.getDistance(self.statCoord, coord) <= self.statFR and coord in Unit0.PLAYERFOV[player]:
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
		statAmmo = statAmmoCap
		targetedCoord = [None]
		
		def __init__(self):
			Unit0.ARTILLERY.append(self)
		
		def targetChange(self, coord):
			if self.statAmmoCap != 0:
				targetedCoord = [coord[0], coord[1]]
				dist = Map0.getDistance(self.statCoord, targetedCoord)
				if dist > self.statMinFR and dist <= self.statMaxFR:
					self.targetedCoord = targetedCoord
					Unit0.MOVEQUEUE[self.arrayPos] = [self.statCoord[:]]	#deleting the movement queue to prevent movement in the same turn
					return True
			return False
		
		def addMoveQueue(self, queue):
			super(Artillery, self).addMoveQueue(queue)
			self.targetedCoord = [None]	#deletes the targeted coordinate to prevent attacking in the same turn
			
			
	class Engineer(Unit):
		statMaxHP = 12
		statHP = statMaxHP
		statArmor = 1
		statSpeed = 3
		statVR = 2
		statDamage = -5
		statFR = 3
		statAbilities = ["A001", "A002"]
		
		def __init__(self):
			Unit0.ENGINEERS.append(self)
#------------------------------------------

class Abilities:
	class Ability(object):	
		statName = "PrototypeAbility"
		priority = 0
		isActivated = False
		caster = None
		
		def __init__(self, caster):
			self.caster = caster
		
		#transfers casting data and checks the activation conditions
		def activate(self,data):
			pass
		
		#action of the activated ability
		def execute(self):
			print("This is a prototype ability, get out!")

	class A001(Ability):
		statName = "EngieHeal"
		priority = 30
		
		#takes targeted unit as data
		def activate(self, data):
			self.target = data
			
			dist = Map0.getDistance(self.caster.statCoord, self.target.statCoord)
			if dist <= self.caster.statFR:
				self.isActivated = True
				
		def execute(self):
			self.isActivated = False
			addedHP = 5
			self.target.statHP += addedHP
			if self.target.statHP > self.target.statMaxHP:
				self.target.statHP = self.target.statMaxHP
			print("Added %s HP to %s(now %s HP)" % (addedHP, self.target, self.target.statHP))
			
	class A002(Ability):
		statName = "ReplenishAmmo"
		priority = 30
		isActivated = True
		
		def activate(self, data):
			self.isActivated = True # passive ability, therefore it's always activated
		
		def execute(self):
			addedAmmo = 5
			for dir in Map0.DIRECTIONS:
				hex = [0, 0]
				hex[0] = self.caster.statCoord[0] + dir[0]
				hex[1] = self.caster.statCoord[1] + dir[1]
				unit = Map0.getUnit(hex)
				if unit in Unit0.TANKS or unit in Unit0.ARTILLERY:
					unit.statAmmo += addedAmmo
					if unit.statAmmo > unit.statAmmoCap:
						unit.statAmmo = unit.statAmmoCap
					print("Added %s Ammo to %s(now %s Ammo)" % (addedAmmo, unit, unit.statAmmo))