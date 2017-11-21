import pygame, sys, math
from pygame.locals import *
from utils import util
from obj import units

class UnitManager(object):
	#singleton implementation
	instance = None
	
	def __init__(self):
		if not UnitManager.instance:
			UnitManager.instance = UnitManager.__UnitManager()
			
	def __getattr__(self, name):
		return getattr(self.instance, name)
		
	class __UnitManager():
		PLAYERS = {"player1": 0, "player2": 1}
		UNITS = ["Tank", "Scout", "Artillery", "Engineer"]
		UNITSTATES = ["Operational", "Conflicted", "Banished", "Destroyed"]
		ABILITIES = ["A001", "A002"]
		EFFECTS = []
		
		#array of ALL units on the map
		unitArray = []
		
		playerSelectedDEFAULT = None
		playerSelected = None
		unitSelectedDEFAULT = None	#default value for a selected unit
		unitSelected = None
		
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
		
		#unit object factory
		def unitCreate(self, unitType, coord, player):
			if unitType not in self.UNITS:
				pass
			if len(coord) != 2:
				pass
			if player not in self.PLAYERS:
				pass
			
			toQ = coord[0]
			toR = coord[1]
			
			#object factory, nothing to see here
			targetUnit = getattr(units.Units, unitType)
			NewUnit = targetUnit()
			self.unitArray.append(NewUnit)
			
			#checking that the unit was properly created
			assert(NewUnit != None, "(Unit object factory) Failed to create the unit")
			
			#assigning values and adding the unit into appropriate arrays
			NewUnit.setOwnerID(self.PLAYERS[player])
			NewUnit.setArrayPosition(len(self.unitArray)-1)
			NewUnit.setCoord(toQ, toR)
			NewUnit.resetMoveQueue()
			
			if len(NewUnit.statAbilities) > 0:
				for abilityID in NewUnit.statAbilities:
					self.unitAddAbility(abilityID, NewUnit)
		
		def unitDestroy(self, deletedUnit):
			if deletedUnit not in self.unitArray:
				pass
			arrayPos = deletedUnit.getArrayPosition()
			
			del self.unitArray[arrayPos]
			
			#shifts all units situated after the deleted one in the array, since the moveQueue
			#position is tracked by arrayPos
			for UNIT in self.unitArray: 
				curArrayPos = UNIT.getArrayPosition()
				if arrayPos < curArrayPos:	
					UNIT.setArrayPosition(curArrayPos - 1)
		
		def isScout(self, unit):
			if unit.getType() == "scout":
				return True
			return False
			
		def isTank(self, unit):
			if unit.getType() == "tank":
				return True
			return False
			
		def isArti(self, unit):
			if unit.getType() == "artillery":
				return True
			return False
			
		def isEngi(self, unit):
			if unit.getType() == "engineer":
				return True
			return False
		
		def moveResolveConflicts(self):
			array = self.unitArray
			for j in range(0, len(array)-1):
				self.unitArray[j].resetState()
				for k in range(j+1, len(array)-1):
					if array[j].getCoord() == array[k].getCoord():
						array[j].setState(self.UNITSTATES[1])
					
		
		def unitMoveStart(self, units):
			flags = [0]*len(units)
			
			while True:
				flags = self.unitMoveTick(units, flags)
				 
				summ = sum(flags)
				if summ == len(units) or self.moveTick > self.moveTickNom:
					break
				pygame.time.delay(75)
				
			self.unitMoveReset(units)
			self.moveResolveConflicts()
		
		#moves units according to their movement queues in moveQueue
		def unitMoveTick(self, units, flags):		
			step = self.moveTick+1
			summ = 0
			
			for i in range (0, len(units)):
				if flags[i] == 1:
					continue
					
				curMoveQueue = units[i].getMoveQueue()
				
				if len(curMoveQueue) <= 1 or step >= len(curMoveQueue):
					flags[i] = 1
					continue
					
				units[i].setCoord(curMoveQueue[step][0], curMoveQueue[step][1])
				
			self.moveTick = step
			return flags
		
		def unitMoveReset(self, units):
			self.moveTick = 0
			
			for unit in units:
				unit.resetMoveQueue()
		
		def unitAddAbility(self, abilityID, caster):
			if abilityID not in self.ABILITIES:
				pass
				
			targetAbility = getattr(Abilities, abilityID)
			instance = targetAbility(caster)
			caster.instAbilities.append(instance)
			
		def calcPlayerFOV(self):
			self.resetPlayerFOV()
			toBeFOV = []
			
			for player in self.PLAYERS:
				del toBeFOV[:]
				ID = self.PLAYERS[player]
				for unit in self.unitArray:
					if unit.getOwnerID() == ID:
						for hex in MAP0.getVisibility(unit.getStatCur("VR"), unit.getCoord()):
							if hex not in self.playerFOV[ID]:
								toBeFOV.append(hex)
						
				self.playerFOV[ID] = toBeFOV[:]

	#------------------------------------------
	#getters and setters
		def setTarget(self, unit, targetCoord):
			if unit.statCur["AMM"] != 0:
				try:
					dist = util.getDistance(unit.statCoord, targetCoord)
				except:
					return False
				
				if self.isTank(unit):
					if dist <= unit.statCur["FRmax"] and targetCoord in self.getPlayerFOV(unit.ownerID):
						targetedUnit = MAP0.getUnit(targetCoord)
						if targetedUnit != None and targetedUnit != unit:
							unit.targetedUnit = targetedUnit
							return True
				
				if self.isArti(unit):
					if dist > unit.statCur["FRmin"] and dist <= unit.statCur["FRmax"]:
						unit.targetedCoord = targetCoord
						#deleting the movement queue to prevent movement in the same turn
						unit.resetMoveQueue()
						return True
			return False
	
		def getUnitSelected(self):
			return self.unitSelected
			
		def resetUnitSelected(self):
			self.unitSelected = self.unitSelectedDEFAULT
			
		def setUnitSelected(self, unit):
			if unit == self.unitSelectedDEFAULT:
				return
			self.unitSelected = unit
		
		def getAllUnits(self):
			return self.unitArray
		
		def getTanks(self):
			return list(filter(self.isTank, self.unitArray))
			
		def getScouts(self):
			return list(filter(self.isScout, self.unitArray))
			
		def getArties(self):
			return list(filter(self.isArti, self.unitArray))
			
		def getEngies(self):
			return list(filter(self.isEngi, self.unitArray))
		
		def getPlayerSelected(self):
			return self.playerSelected
		
		def getPlayerSelectedID(self):
			return self.PLAYERS[self.playerSelected]
		
		def setPlayerSelected(self, player):
			if player not in self.PLAYERS:
				pass
			self.playerSelected = player
			
		def getPlayerFOV(self, playerID):
			return self.playerFOV[playerID][:]
			
		def resetPlayerFOV(self):
			del self.playerFOV[:]
			for i in range(0, len(self.PLAYERS)):
				self.playerFOV.append([])
			
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
			
			dist = util.getDistance(self.caster.statCoord, self.target.statCoord)
			if dist <= self.caster.getStatCur("VR"):
				self.isActivated = True
		
		def execute(self):
			addedHP = 5
			self.target.setStatCur("HP", self.target.getStatCur("HP")+addedHP)
			if self.target.getStatCur("HP") > self.target.getStatNom("HP"):
				self.setStatCur("HP", self.target.getStatNom("HP"))
			self.deactivate()
			
			print("Added %s HP to %s(now %s HP)" % (addedHP, self.target, self.target.getStatCur("HP")))
			
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
					self.target.setStatCur("AMM", self.target.getStatCur("AMM")+addedAmmo)
					if unit.getStatCur("AMM") > unit.getStatNom("AMM"):
						self.setStatCur("AMM", self.target.getStatNom("AMM"))
					print("Added %s Ammo to %s(now %s Ammo)" % (addedAmmo, unit, unit.getStatCur("AMM")))
					
#------------------------------------------
#------------------------------------------
class Effects:
	class Effect(object):
		statName = "prototypeEffect"
		statTimer = 0
		unitAffected = None
		isABuff = False
		isNegative = False
		#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
		statBuff = [0, 0, 0, 0, 0, 0, 0, 0]
		
		def __init__(self, unit):
			self.unitAffected = unit
		
		def tick(self):
			self.statTimer = -1
			if self.statTimer == 0:
				self.destroy()
			
		def destroy(self):
			effectArray = self.statUnitAffected.instEffects
			del effectArray[effectArray.index(self)]
			print("%s\' \"%s\" has expired." % (self.statUnitAffected.getName(), self.statName))
			
		def effect(self, data):
			print("This is a prototype effect, get out!")