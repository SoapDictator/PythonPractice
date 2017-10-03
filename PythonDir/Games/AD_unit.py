import pygame, sys, math
from pygame.locals import *

global PLAYERS, AVAILIBLEUNITS, AVAILIBLEABILITIES, AVAILIBLEEFFECTS
PLAYERS = {"player1": 0, "player2": 1}
AVAILIBLEUNITS = ["Tank", "Scout", "Artillery", "Engineer"]
AVAILIBLEABILITIES = ["A001", "A002"]
AVAILIBLEEFFECTS = []

class UnitManager(object):
	#array of ALL units on the map
	unitArray = []
	
	unitListScout = []
	unitListTank = []
	unitListArti = []
	unitListEngi = []
	
	#array of ALL movement queues of ALL units, position of the movement queue is 
	#determined by a unit's position in unitArray
	moveQueue = []
	
	playerSelectedDEFAULT = None
	playerSelected = None
	unitSelectedDEFAULT = None	#default value for a selected unit
	unitSelected = None
	
	unitMoveFlags = []
	moveTickNom = 50
	moveTick = 0
	
	playerFOV = []
	
	def __init__(self):
		self.setPlayerSelected("player1")
		self.resetPlayerFOV()
	
	def defineGlobals(self, DrawingManager, MapManager, UnitManager):
		global WINDOW0, MAP0, UNIT0
		WINDOW0 = DrawingManager
		MAP0 = MapManager
		UNIT0 = UnitManager
	
	#creates a new unit and adds it to the unitArray as well as creates an entry in 
	#moveQueue; new unit will always be the last one in the array
	def unitCreate(self, unitType, coord, player):
		if unitType not in AVAILIBLEUNITS:
			pass
		if len(coord) != 2:
			pass
		if player not in PLAYERS:
			pass
		
		toQ = coord[0]
		toR = coord[1]
		
		#object factory, nothing to see here
		targetUnit = getattr(Units, unitType)
		NewUnit = targetUnit()
		self.unitArray.append(NewUnit)
		
		#assigning values and adding the unit into appropriate arrays
		NewUnit.setOwner(PLAYERS[player])
		NewUnit.setArrayPosition(len(self.unitArray)-1)
		NewUnit.setCoord(toQ, toR)
		self.moveQueue.append([[toQ, toR]])
		
		if len(NewUnit.statAbilities) > 0:
			for abilityID in NewUnit.statAbilities:
				self.unitAddAbility(abilityID, NewUnit)
	
	def unitDestroy(self, deletedUnit):
		if deletedUnit not in self.unitArray():
			pass
		arrayPos = deletedUnit.getArrayPosition()
		
		del self.unitArray[arrayPos]
		del self.moveQueue[arrayPos]
		
		if self.isScout(deletedUnit):
			del UNIT0.unitListScout[UNIT0.unitListScout.index(deletedUnit)]
		elif self.isTank(deletedUnit):
			del UNIT0.unitListTank[UNIT0.unitListTank.index(deletedUnit)]
		elif self.isArti(deletedUnit):
			del UNIT0.unitListArti[UNIT0.unitListArti.index(deletedUnit)]
		elif self.isEngi(deletedUnit):
			del UNIT0.unitListEngi[UNIT0.unitListEngi.index(deletedUnit)]
		
		#shifts all units situated after the deleted one in the array, since the moveQueue
		#position is tracked by arrayPos
		for UNIT in self.unitArray: 
			curArrayPos = UNIT.getArrayPosition()
			if arrayPos < curArrayPos:	
				UNIT.setArrayPosition(curArrayPos - 1)
	
	def isScout(self, unit):
		if unit in UNIT0.unitListScout:
			return True
		return False
		
	def isTank(self, unit):
		if unit in UNIT0.unitListTank:
			return True
		return False
		
	def isArti(self, unit):
		if unit in UNIT0.unitListArti:
			return True
		return False
		
	def isEngi(self, unit):
		if unit in UNIT0.unitListEngi:
			return True
		return False
	
	#rewrite this ASAP
	#resolves situations when 2 or more units are trying to travel to the same final position
	def moveResolveCollision(self):
		for UNIT in self.unitArray:
			#checking all units which are moving this turn
			if len(UNIT.getMoveQueue()) > 1: 
				for unit in self.unitArray:
					if UNIT != unit:
						UNITMoveLen = len(UNIT.getMoveQueue())
						unitMoveLen = len(unit.getMoveQueue())
						
						UNITMoveTime = float(UNITMoveLen)/UNIT.statCur["SPD"]
						unitMoveTime = float(unitMoveLen)/unit.statCur["SPD"]
						
						if UNITMoveTime > UNITMoveTime and unitMoveLen < 2:
							del UNIT.getMoveQueue()[UNITMoveLen-1]
						elif UNITMoveTime < UNITMoveTime and unitMoveLen < 2:
							del unit.getMoveQueue()[unitMoveLen-1]
						else: #defaut action if oth units arrived at the same time
							del UNIT.getMoveQueue()[UNITMoveLen-1]
	
	def unitMoveStart(self, units):
		self.unitMoveFlags = [0]*len(self.moveQueue)
		flag = False
		
		self.moveResolveCollision()
		
		while True:
			if self.unitMoveTick(units):
				break
			pygame.time.wait(75)
			
		self.unitMoveReset(units)
	
	#moves units according to their movement queues in moveQueue
	def unitMoveTick(self, units):		
		step = self.moveTick
		summ = 0
		
		for UNIT in units:
			unitArrayPos = UNIT.getArrayPosition()
			if self.unitMoveFlags[unitArrayPos] == 1:
				continue
				
			curMoveQueue = UNIT.getMoveQueue()
			
			if len(curMoveQueue) <= 1 or step >= len(curMoveQueue):
				self.unitMoveFlags[unitArrayPos] = 1
				continue
				
			UNIT.setCoord(curMoveQueue[step][0], curMoveQueue[step][1])
			
		self.moveTick = step+1
	
		#stop conditions
		for flag in self.unitMoveFlags:
			summ += flag
		if summ == len(units) or self.moveTick > self.moveTickNom:
			return True
		return False
	
	def unitMoveReset(self, units):
		self.moveTick = 0
		del self.unitMoveFlags[:]
		
		for unit in units:
			arrayPos = unit.getArrayPosition()
			self.moveQueue[arrayPos][0] = unit.getCoord()
			del self.moveQueue[arrayPos][1:]
	
	def unitAddAbility(self, abilityID, caster):
		if abilityID not in AVAILIBLEEFFECTS:
			pass
			
		targetAbility = getattr(Abilities, abilityID)
		instance = targetAbility(caster)
		caster.instAbilities.append(instance)

#------------------------------------------
#getters and setters
	def getUnitSelected(self):
		return self.unitSelected
		
	def resetUnitSelected(self):
		self.unitSelected = self.unitSelectedDEFAULT
		
	def setUnitSelected(self, unit):
		if unit == self.unitSelectedDEFAULT:
			pass
		self.unitSelected = unit
	
	def getAllUnits(self):
		return self.unitArray
	
	def getTanks(self):
		return self.unitListTank
		
	def getScouts(self):
		return self.unitListScout
		
	def getArties(self):
		return self.unitListArti
		
	def getEngies(self):
		return self.unitListEngi
	
	def getPlayerSelected(self):
		return self.playerSelected
	
	def getPlayerSelectedID(self):
		return PLAYERS[self.playerSelected]
	
	def setPlayerSelected(self, player):
		if player not in PLAYERS:
			pass
		self.playerSelected = player
		
	def getPlayerFOV(self, playerID):
		return self.playerFOV[playerID]
		
	def resetPlayerFOV(self):
		del self.playerFOV[:]
		for i in range(0, len(PLAYERS)):
			self.playerFOV.append([])
			
	def setPlayerFOV(self, playerID):
		self.resetPlayerFOV()
		
		toBeFOV = []
		for unit in self.unitArray:
			for hex in MAP0.getVisibility(unit.statCur["VR"], unit.getCoord()):
				if hex not in self.playerFOV[playerID]:
					toBeFOV.append(hex)
					
		self.playerFOV[playerID] = toBeFOV
		
#------------------------------------------
#------------------------------------------

class Units:
	class Unit(object):
		statCoord = [0, 0]
		statAbilities = []
		instAbilities = []
		arrayPos = 0
		owner = None
		
		statNom = {	"HP": 0,
							"AR": 0,
							"SH": 0,
							"SPD": 0,
							"VR": 0}
		statCur = {}
		
		def castAbility(self, abilityID, data):
			if abilityID not in self.statAbilities:
				pass
			ability = self.instAbilities[self.statAbilities.index(abilityID)]
			ability.activate(data)
						
		def setInitialStats (self, HP, AR, SH, SPD, VR):
			self.statNom["HP"] = HP
			self.statNom["AR"] = AR
			self.statNom["SH"] = SH
			self.statNom["SPD"] = SPD
			self.statNom["VR"] = VR
			self.statCur = self.statNom.copy()
			
		def getMoveQueue(self):
			return UNIT0.moveQueue[self.arrayPos]
			
		def setMoveQueue(self, queue):
			UNIT0.moveQueue[self.arrayPos] = queue[:]
			
		def resetMoveQueue(self):
			UNIT0.moveQueue[self.arrayPos] = [self.statCoord[:]]
			
		def getCoord(self):
			return self.statCoord
			
		def setCoord(self, Q, R):
			self.statCoord = [Q, R]
		
		def getTarget(self):
			return None
			
		def setTarget(self):
			return False
		
		def getOwner(self):
			return self.owner
		
		def getOwnerID(self):
			return PLAYERS[self.owner]
		
		def setOwner(self, owner):
			self.owner = owner
		
		def getArrayPosition(self):
			return self.arrayPos
		
		def setArrayPosition(self, position):
			self.arrayPos = position
#------------------------------------------
			
	class Scout(Unit):
		def __init__(self):
			UNIT0.unitListScout.append(self)
			self.setInitialStats(6, 5, 0, 5, 5)

#------------------------------------------
			
	class Tank(Unit):
		targetedUnit = None
		
		def __init__(self):
			UNIT0.unitListTank.append(self)
			self.setInitialStats(10, 2, 2, 4, 3, 10, 0, 3, 10)
		
		def setTarget(self, coord):
			if self.statCur["AMM"] != 0:
				dist = MAP0.getDistance(self.statCoord, coord)
				if dist <= self.statCur["FRmax"] and coord in UNIT0.getPlayerFOV(self.owner):
					targetedUnit = MAP0.getUnit(coord)
					if targetedUnit != None and targetedUnit != self:
						self.targetedUnit = targetedUnit
						return True
			return False
			
		def resetTarget(self):
			self.targetedUnit = None
			
		def getTarget(self):
			return self.targetedUnit
			
		def setInitialStats (self, HP, AR, SH, SPD, VR, DMG, FRmin, FRmax, AMM):
			self.statNom["DMG"] = DMG
			self.statNom["FRmin"] = FRmin
			self.statNom["FRmax"] = FRmax
			self.statNom["AMM"] = AMM
			super(Units.Tank, self).setInitialStats(HP, AR, SH, SPD, VR)

#------------------------------------------
			
	class Artillery(Unit):
		targetedCoord = None
		
		def __init__(self):
			UNIT0.unitListArti.append(self)
			self.setInitialStats(8, 0, 4, 4, 2, 11, 2, 5, 10)
		
		def setTarget(self, coord):
			if self.statCur["AMM"] != 0:
				targetedCoord = [coord[0], coord[1]]
				dist = MAP0.getDistance(self.statCoord, targetedCoord)
				if dist > self.statCur["FRmin"] and dist <= self.statCur["FRmax"]:
					self.targetedCoord = targetedCoord
					#deleting the movement queue to prevent movement in the same turn
					self.resetMoveQueue()
					return True
			return False
		
		def resetTarget(self):
			self.targetedCoord = None
			
		def getTarget(self):
			return self.targetedCoord
		
		def setMoveQueue(self, queue):
			super(Units.Artillery, self).setMoveQueue(queue)
			#deletes the targeted coordinate to prevent attacking in the same turn
			self.resetTarget()

		def setInitialStats (self, HP, AR, SH, SPD, VR, DMG, FRmin, FRmax, AMM):
			self.statNom["DMG"] = DMG
			self.statNom["FRmin"] = FRmin
			self.statNom["FRmax"] = FRmax
			self.statNom["AMM"] = AMM
			super(Units.Artillery, self).setInitialStats(HP, AR, SH, SPD, VR)

#------------------------------------------
			
	class Engineer(Unit):
		statAbilities = ["A001", "A002"]
		
		def __init__(self):
			UNIT0.unitListEngi.append(self)
			self.setInitialStats(12, 3, 4, 3, 2)
			
#------------------------------------------
#------------------------------------------
class Abilities:
	class Ability(object):	
		statName = "PrototypeAbility"
		priority = 0
		isActivated = False
		caster = None
		effects = []
		
		def __init__(self, caster):
			self.caster = caster
		
		#transfers casting data and checks the activation conditions
		def activate(self,data):
			self.isActivated = True
			
		def deactivate(self):
			self.isActivated = False
		
		#action of the activated ability
		def execute(self):
			print("This is a prototype ability, get out!")

	class A001(Ability):
		statName = "EngieHeal"
		priority = 30
		
		#takes targeted unit as data
		def activate(self, data):
			self.target = data
			
			dist = MAP0.getDistance(self.caster.statCoord, self.target.statCoord)
			if dist <= self.caster.statCur["VR"]:
				self.isActivated = True
		
		def execute(self):
			addedHP = 5
			self.target.statCur["HP"] += addedHP
			if self.target.statCur["HP"] > self.target.statNom["HP"]:
				self.target.statCur["HP"] = self.target.statNom["HP"]
			self.deactivate()
			
			print("Added %s HP to %s(now %s HP)" % (addedHP, self.target, self.target.statCur["HP"]))
			
	class A002(Ability):
		statName = "ReplenishAmmo"
		priority = 30
		
		def activate(self, data):
			self.isActivated = True # passive ability, therefore it's always activated
		
		def execute(self):
			addedAmmo = 5
			for dir in MAP0.DIRECTIONS:
				hex = [0, 0]
				hex[0] = self.caster.statCoord[0] + dir[0]
				hex[1] = self.caster.statCoord[1] + dir[1]
				unit = MAP0.getUnit(hex)
				if unit in UNIT0.unitListTank or unit in UNIT0.unitListArti:
					unit.statCur["AMM"] += addedAmmo
					if unit.statCur["AMM"] > unit.statNom["AMM"]:
						unit.statCur["AMM"] = unit.statNom["AMM"]
					print("Added %s Ammo to %s(now %s Ammo)" % (addedAmmo, unit, unit.statCur["AMM"]))