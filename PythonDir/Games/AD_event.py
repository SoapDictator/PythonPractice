from AD_unit import *

class GameEventManager(object):
	EVENTQUEUE = []
	LASTADDEDEVENT = None
	
	def defineGlobals(self, EventManager, MapManager, UnitManager):
		global Event0, Map0, Unit0
		Event0 = EventManager
		Map0 = MapManager
		Unit0 = UnitManager
	
	def eventAdd(self, eventName, data = None, priorityMod = 0):	#TODO: event sorting mechanism
		event = None
		priority = 0
		if eventName == "EventUnitAttack":
			event = EventUnitAttack(data)
			priority += 1
		elif eventName == "EventUnitHPCheck":
			event = EventUnitHPCheck(data)
			priority += 2
		elif eventName == "EventUnitCreate":
			event = EventUnitCreate(data)
			priority += 3
		elif eventName == "EventUnitDestroy":
			event = EventUnitDestroy(data)
			priority += 4
		elif eventName == "EventUnitAbilityCheck":
			pass
			#priority = +5
		elif eventName == "EventUnitMove":
			if len(data) != 0:
				event = EventUnitMove(data)
				priority = +6
		
		priority += priorityMod
		if event != None:
			if len(self.EVENTQUEUE) > 1:
				if self.EVENTQUEUE[0][1] > priority:
					self.EVENTQUEUE.insert(0, [event, priority])
				elif self.EVENTQUEUE[len(self.EVENTQUEUE)-1][1] < priority:
					self.EVENTQUEUE.append([event, priority])
				else:
					for i in range(1, len(self.EVENTQUEUE)):
						if self.EVENTQUEUE[i-1][1] <= priority and self.EVENTQUEUE[i][1] >= priority:
							self.EVENTQUEUE.insert(i, [event, priority])
							break
			else:
				if len(self.EVENTQUEUE) == 1 and self.EVENTQUEUE[0][1] > priority:
					self.EVENTQUEUE.insert(0, [event, priority])
				else:
					self.EVENTQUEUE.append([event, priority])
			self.LASTADDEDEVENT = event
	
	def eventUndo(self):
		Unit = Unit0.SELECTEDUNIT
		if Unit != None:
			if len(Unit0.MOVEQUEUE[Unit.arrayPos]) > 1:
				del Unit0.MOVEQUEUE[Unit.arrayPos][1:]
			else:
				if Unit in Unit0.TANKS or Unit in Unit0.ENGINEERS:
					Unit.targetedUnit = None
				elif Unit in Unit0.ARTILLERY:
					Unit.targetedCoord = [None]
		elif self.LASTADDEDEVENT != None:
			for i in range(0, len(self.EVENTQUEUE)):
				if self.LASTADDEDEVENT == self.EVENTQUEUE[i][0]:
					print("Undid %s" % self.EVENTQUEUE[i][0])
					del self.EVENTQUEUE[i]
					self.LASTADDEDEVENT = None
	
	def eventHandle(self):
		del Unit0.PLAYERFOV[0:len(Unit0.PLAYERFOV)-1] #ducktape to recalculate player FOV
		Unit0.PLAYERFOV = [[], []]
		
		priorityMod = 0
		for i in range (0, 4):
			self.eventAdd("EventUnitHPCheck", priorityMod, priorityMod)
			#if i == 0:
			
			if i == 1:
				for UNIT in Unit0.TANKS:
					if UNIT.targetedUnit != None:
						Event0.eventAdd("EventUnitAttack", UNIT, priorityMod)
						
				self.eventAdd("EventUnitMove", Unit0.SCOUTS, priorityMod)
		
			if i == 2:
				for UNIT in Unit0.ENGINEERS:
					if UNIT.targetedUnit != None:
						Event0.eventAdd("EventUnitAttack", UNIT, priorityMod)
				for UNIT in Unit0.ARTILLERY:
					if UNIT.targetedCoord != [None]:
						Event0.eventAdd("EventUnitAttack", UNIT, priorityMod)
				
				tempUnits = Unit0.TANKS + Unit0.ARTILLERY + Unit0.ENGINEERS
				self.eventAdd("EventUnitMove", tempUnits, priorityMod)
			
			#if i == 3:
			priorityMod += 10
		
		for event in self.EVENTQUEUE:
			event[0].execute()
		del self.EVENTQUEUE[:]
		
		Unit0.unitFOV()
		print("=======")

#------------------------------------------
		
class GameEvent(object):
	def execute(self):
		print("This is a prototype event, get out!")

class EventUnitCreate(GameEvent):
	def __init__(self, data):
		self.data = data
		
	def execute(self):
		Unit0.unitCreate(self.data[0], self.data[1], self.data[2])
		print("A new %s appeared!" %self.data[0])

class EventUnitDestroy(GameEvent):
	def __init__(self, data):
		self.data = data
		
	def execute(self):
		Unit0.unitDestroy(self.data)
		print("Unit lost.")

class EventUnitHPCheck(GameEvent):
	def __init__(self, data):
		self.data = data

	def execute(self):
		for Unit in Unit0.UNITARRAY:
			if Unit.statHP <= 0:
				Event0.eventAdd("EventUnitDestroy", Unit, self.data)
			if Unit.statHP > Unit.statMaxHP:
				Unit.statHP = Unit.statMaxHP
		print("HP checked.")

class EventUnitMove(GameEvent):
	def __init__(self, data):
		self.data = data
		
	def execute(self):
		if len(self.data) != 0:
			Unit0.unitMove(self.data)
			print("Moved units.")

class EventUnitAttack(GameEvent):
	def __init__(self, data):
		self.attackingUnit = data
	
	def execute(self):
		if self.attackingUnit in Unit0.TANKS or self.attackingUnit in Unit0.ENGINEERS:
			targetedUnit = self.attackingUnit.targetedUnit
			self.attackingUnit.targetedUnit = None
		elif self.attackingUnit in Unit0.ARTILLERY:
			targetedUnit = Map0.getUnit(self.attackingUnit.targetedCoord)
			self.attackingUnit.targetedCoord = [None]
		if targetedUnit != None:
			targetedUnit.statHP -= self.attackingUnit.statDamage - targetedUnit.statArmor
		print("A unit is (probably) under attack!")