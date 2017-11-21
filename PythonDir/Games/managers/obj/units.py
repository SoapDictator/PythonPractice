import copy

class Units:
	class Unit(object):
		statName = "prototypeUnit"
		statState = "Operational"
		statCoord = [0, 0]
		statAbilities = []
		instAbilities = []
		instEffects = []
		arrayPos = 0
		moveQueue = []

		ownerID = None
		type = None
		
		#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
		statNom = None
		statCur = None
		
		def castAbility(self, abilityID, data):
			if self.statState == "Operational":
				if abilityID not in self.statAbilities:
					pass
				ability = self.instAbilities[self.statAbilities.index(abilityID)]
				ability.activate(data)
		
		def effectsTick(self):
			for effect in self.instEffects:
				effect.tick()
		
		def getStatNom(self, stat):
			return self.statNom[stat]
			
		def getStatCur(self, stat):
			return self.statCur[stat]
			
		def setStatCur(self, statName, statVal):
			self.statCur[statName] = statVal
		
		def setInitialStats (self, HP, AR, SPD, VR, DMG=None, FRmin=None, FRmax=None, AMM=None):
			stat = {}
			stat["HP"] = HP
			stat["AR"] = AR
			stat["SPD"] = SPD
			stat["VR"] = VR
			stat["DMG"] = DMG
			stat["FRmin"] = FRmin
			stat["FRmax"] = FRmax
			stat["AMM"] = AMM
			self.statNom = stat
			self.statCur = copy.deepcopy(stat)
		
		def getName(self):
			return self.statName
		
		def getType(self):
			return self.type
		
		def getMoveQueue(self):
			return self.moveQueue[:]
			
		def setMoveQueue(self, queue):
			self.moveQueue = queue[:]
			
		def resetMoveQueue(self):
			del self.moveQueue[:]
			
		def getCoord(self):
			return self.statCoord[:]
			
		def setCoord(self, Q, R):
			self.statCoord = [Q, R]
		
		def getTarget(self):
			return None
			
		def setTarget(self):
			return False
		
		def getOwnerID(self):
			return self.ownerID
		
		def setOwnerID(self, ownerID):
			self.ownerID = ownerID
		
		def getArrayPosition(self):
			return self.arrayPos
		
		def setArrayPosition(self, position):
			self.arrayPos = position
			
		def getState(self):
			return self.statState
			
		def setState(self, state):
			self.statState = state
			
		def resetState(self):
			self.statState = "Operational"
#------------------------------------------
			
	class US001(Unit):
		statName = "Scout"
		
		def __init__(self):
			self.type = "scout"
			#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
			self.setInitialStats(6, 2, 5, 5)

#------------------------------------------
			
	class UT001(Unit):
		statName = "Tank"
		targetedUnit = None
		
		def __init__(self):
			self.type = "tank"
			#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
			self.setInitialStats(10, 2, 4, 3, 10, 0, 3, 10)
		
		def setTarget(self, target):
			if self.statState == "Operational":
				self.targetedUnit = target
			
		def resetTarget(self):
			self.targetedUnit = None
			
		def getTarget(self):
			return self.targetedUnit

#------------------------------------------
			
	class UA001(Unit):
		statName = "Artillery"
		targetedCoord = None
		
		def __init__(self):
			self.type = "artillery"
			#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
			self.setInitialStats(8, 0, 4, 2, 11, 2, 6, 10)
		
		def setTarget(self, targetCoord):
			if self.statState == "Operational":
				self.targetedCoord = targetCoord
		
		def resetTarget(self):
			self.targetedCoord = None
			
		def getTarget(self):
			return self.targetedCoord
		
		def setMoveQueue(self, queue):
			super(Units.Artillery, self).setMoveQueue(queue)
			#deletes the targeted coordinate to prevent attacking in the same turn
			self.resetTarget()

#------------------------------------------
			
	class UE001(Unit):
		statName = "Engineer"
		statAbilities = ["A001", "A002"]
		
		def __init__(self):
			self.type = "engineer"
			#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
			self.setInitialStats(12, 3, 3, 2)