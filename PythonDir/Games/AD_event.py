from AD_unit import *

class GameEventManager(object):
	EVENTQUEUE = []
	LASTADDEDEVENT = 0
	
	def defineGlobals(self, EventManager, MapManager, UnitManager):
		global Event0, Map0, Unit0
		Event0 = EventManager
		Map0 = MapManager
		Unit0 = UnitManager
	
	def eventAdd(self, eventName, data = None):	#TODO: event sorting mechanism
		event = None
		if eventName == "EventUnitAttack":
			event = EventUnitAttack(data)
			if data in Unit0.TANKS:
				priority = 21
			elif data in Unit0.ARTILLERY or data in Unit0.ENGINEERS:
				priority = 31
			else:
				priority = 0
		elif eventName == "EventUnitHPCheck":
			event = EventUnitHPCheck()
			priority = 32
		elif eventName == "EventUnitCreate":
			event = EventUnitCreate(data)
			priority = 13
		elif eventName == "EventUnitDestroy":
			event = EventUnitDestroy(data)
			priority = 34
		elif eventName == "EventUnitAbilityCheck":
			pass
			#priority = 15
		elif eventName == "EventUnitMove":
			if len(data) != 0:
				event = EventUnitMove(data)
				if data == Unit0.SCOUTS:
					priority = 16
				elif data == Unit0.TANKS:
					priority = 26
				elif data == Unit0.ARTILLERY or data == Unit0.ENGINEERS:
					priority = 36
		
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
		if Input0.getState() == 'unitSelected' and len(Unit0.MOVEQUEUE[Unit0.SELECTEDUNIT.arrayPos]) > 1:
			del Unit0.MOVEQUEUE[Unit0.SELECTEDUNIT.arrayPos][1:len(Unit0.MOVEQUEUE[Unit0.SELECTEDUNIT.arrayPos])]
		else:
			for i in range(0, len(self.EVENTQUEUE)):
				if self.LASTADDEDEVENT == self.EVENTQUEUE[i][0]:
					print("Undid %s" % self.EVENTQUEUE[i][0])
					del self.EVENTQUEUE[i]
					self.LASTADDEDEVENT = 0
	
	def eventHandle(self):
		del Unit0.PLAYERFOV[0:len(Unit0.PLAYERFOV)-1] #ducktape to recalculate player FOV
		Unit0.PLAYERFOV = [[], []]
		
		self.eventAdd("EventUnitHPCheck")
		
		self.eventAdd("EventUnitMove", Unit0.SCOUTS)
		self.eventAdd("EventUnitMove", Unit0.TANKS)
		self.eventAdd("EventUnitMove", Unit0.ARTILLERY)
		self.eventAdd("EventUnitMove", Unit0.ENGINEERS)
		
		for UNIT in Unit0.UNITARRAY:
			if UNIT in Unit0.TANKS or UNIT in Unit0.ENGINEERS:
				if UNIT.targetedUnit != None:
					Event0.eventAdd("EventUnitAttack", UNIT)
			elif UNIT in Unit0.ARTILLERY:
				if UNIT.targetedCoord != [None]:
					Event0.eventAdd("EventUnitAttack", UNIT)
		
		
		for event in self.EVENTQUEUE:
			event[0].execute()
		del self.EVENTQUEUE[0:len(self.EVENTQUEUE)]
		
		Unit0.unitFOV()
		print("------------")

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
	def execute(self):
		for Unit in Unit0.UNITARRAY:
			if Unit.statHP <= 0:
				Event0.eventAdd("EventUnitDestroy", Unit)
			if Unit.statHP > Unit.statMaxHP:
				Unit.statHP = Unit.statMaxHP
		print("HP checked.")

class EventUnitMove(GameEvent):
	def __init__(self, data):
		self.data = data
		
	def execute(self):
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