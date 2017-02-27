from AD_unit import *

class GameEventManager(object):
	EVENTQUEUE = []
	LASTADDEDEVENT = 0
	
	def defineGlobals(self, MapManager, UnitManager):
		global Map0, Unit0
		Map0 = MapManager
		Unit0 = UnitManager
	
	def eventAdd(self, eventName, data):	#TODO: event sorting mechanism
		event = 0
		if eventName == "EventUnitCreate":
			event = EventUnitCreate(data)
			priority = 3
		elif eventName == "EventUnitDestroy":
			event = EventUnitDestroy(data)
			priority = 4
		elif eventName == "EventUnitHealthCheck":
			event = EventUnitHealthCheck()
			priority = 2
		elif eventName == "EventUnitAbilityCheck":
			pass
			#priority = 5
		elif eventName == "EventUnitMove":
			event = EventUnitMove()
			priority = 6
		elif eventName == "EventUnitAttack":
			event = EventUnitAttack(data)
			priority = 1
		
		if event != 0:
			if len(self.EVENTQUEUE) > 1:
				if self.EVENTQUEUE[0][1] > priority:
					self.EVENTQUEUE.insert(0, [event, priority])
				elif self.EVENTQUEUE[len(self.EVENTQUEUE)-1][1] < priority:
					self.EVENTQUEUE.append([event, priority])
				else:
					for i in range(1, len(self.EVENTQUEUE)):
						if self.EVENTQUEUE[i-1][1] <= priority and self.EVENTQUEUE[i][1] >= priority:
							self.EVENTQUEUE.insert(i, [event, priority])
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
		self.eventAdd("EventUnitHealthCheck", 0)
		self.eventAdd("EventUnitMove", 0)
		
		for UNIT in Unit0.UNITARRAY:
			if isinstance(UNIT, Tank):
				if UNIT.targetedUnit != None:
					Event0.eventAdd("EventUnitAttack", UNIT)
			elif isinstance(UNIT, Artillery):
				if UNIT.targetedCoord != [None]:
					Event0.eventAdd("EventUnitAttack", UNIT)

		for event in self.EVENTQUEUE:
			event[0].execute()
		del self.EVENTQUEUE[0:len(self.EVENTQUEUE)]
		
		#Unit0.unitCalculateVisibility()		commented out; needs fixing
		print("------------")

#------------------------------------------
		
class GameEvent(object):
	def execute(self):
		print("This is a prototype event, get out!")

class EventUnitCreate(GameEvent):
	def __init__(self, data):
		self.unitType = data[0]
		self.coord = data[1]
		
	def execute(self):
		Unit0.unitCreate(self.unitType, self.coord[0], self.coord[1])
		print("A new %s appeared!" %self.unitType)

class EventUnitDestroy(GameEvent):
	def __init__(self, deletedUnit):
		self.deletedUnit = deletedUnit
		
	def execute(self):
		Unit0.unitDestroy(self.deletedUnit)
		print("Unit lost.")

class EventUnitHealthCheck(GameEvent):
	def execute(self):
		for Unit in Unit0.UNITARRAY:
			if Unit.statHealth <= 0:
				Event0.eventAdd("EventUnitDestroy", Unit)
		print("Health checked.")

class EventUnitMove(GameEvent):
	def execute(self):
		Unit0.unitMove()
		print("Moved units.")

class EventUnitAttack(GameEvent):
	def __init__(self, data):
		self.attackingUnit = data
	
	def execute(self):
		if isinstance(self.attackingUnit, Tank):
			if self.attackingUnit.targetedUnit != None:
				self.attackingUnit.targetedUnit.statHealth -= self.attackingUnit.statDamage
				self.attackingUnit.targetedUnit = None
		elif isinstance(self.attackingUnit, Artillery):
			targetedUnit = Map0.getUnit(self.attackingUnit.targetedCoord)
			if targetedUnit != -1:
				targetedUnit.statHealth -= self.attackingUnit.statDamage
			self.attackingUnit.targetedCoord = [None]
		print("A unit is (probably) under attack!")