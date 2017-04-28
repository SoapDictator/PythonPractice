from AD_unit import *

class GameEventManager(object):
	TURNCOUNTER = 0
	EVENTQUEUE = []
	LASTADDEDEVENT = None
	
	#event name: default priority
	EVENTDICT = {	"EventUnitAttack": 1, 
							"EventUnitHPCheck": 2,
							"EventUnitCreate": 3,
							"EventUnitDestroy": 4,
							"EventUnitAbilityCast": 5,
							"EventUnitMove": 6}
	
	def defineGlobals(self, EventManager, MapManager, UnitManager):
		global Event0, Map0, Unit0
		Event0 = EventManager
		Map0 = MapManager
		Unit0 = UnitManager
	
	def eventAdd(self, eventName, data = None, priorityMod = 0):	#TODO: event sorting mechanism
		if eventName not in self.EVENTDICT:
			pass
		
		targetEvent = getattr(Events, eventName)
		event = targetEvent(data)
		priority = self.EVENTDICT[eventName] + priorityMod
		
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
			self.eventAdd("EventUnitAbilityCast", priorityMod, priorityMod)
			if i == 0:	#preturn
				pass
			
			if i == 1:	#first half
				for UNIT in Unit0.TANKS:
					if UNIT.targetedUnit != None:
						Event0.eventAdd("EventUnitAttack", UNIT, priorityMod)
						
				self.eventAdd("EventUnitMove", Unit0.SCOUTS, priorityMod)
		
			if i == 2:	#second half
				for UNIT in Unit0.ARTILLERY:
					if UNIT.targetedCoord != [None]:
						Event0.eventAdd("EventUnitAttack", UNIT, priorityMod)
				
				#tempUnits = Unit0.TANKS + Unit0.ARTILLERY + Unit0.ENGINEERS
				#self.eventAdd("EventUnitMove", tempUnits, priorityMod)	#have to call it 3 times, otherwise destroyed units will try to move and cause a bug
				self.eventAdd("EventUnitMove", Unit0.TANKS, priorityMod)
				self.eventAdd("EventUnitMove", Unit0.ARTILLERY, priorityMod)
				self.eventAdd("EventUnitMove", Unit0.ENGINEERS, priorityMod)
			
			if i == 3:	#postturn
				pass
				
			priorityMod += 10
		
		for event in self.EVENTQUEUE:
			event[0].execute()
		del self.EVENTQUEUE[:]
		
		Unit0.unitFOV()
		print("============")
		self.TURNCOUNTER += 1
		print("==Turn %s==" % self.TURNCOUNTER)

#------------------------------------------

class Events:
	class GameEvent(object):
		def __init__(self, data):
			self.data = data

		def execute(self):
			print("This is a prototype event, get out!")

	class EventUnitCreate(GameEvent):
		#takes a unit type (as a string) and [coordinates] as data
			
		def execute(self):
			Unit0.unitCreate(self.data[0], self.data[1], self.data[2])
			print("A new %s appeared!" %self.data[0])

	class EventUnitDestroy(GameEvent):
		#takes a unit queued for destruction as data

		def execute(self):
			Unit0.unitDestroy(self.data)
			print("Unit lost.")

	class EventUnitHPCheck(GameEvent):
		#takes priority modifier as data

		def execute(self):
			for Unit in Unit0.UNITARRAY:
				if Unit.statHP <= 0:
					Event0.eventAdd("EventUnitDestroy", Unit, self.data)
				if Unit.statHP > Unit.statMaxHP:
					Unit.statHP = Unit.statMaxHP
			#print("HP checked.")

	class EventUnitMove(GameEvent):
		#takes a unit array as data
			
		def execute(self):
			if len(self.data) != 0:
				Unit0.unitMove(self.data)
				#print("Moved units.")

	class EventUnitAttack(GameEvent):
		#takes an attacking unit as data

		def execute(self):
			if self.data in Unit0.TANKS:
				targetedUnit = self.data.targetedUnit
				self.data.targetedUnit = None
			elif self.data in Unit0.ARTILLERY:
				targetedUnit = Map0.getUnit(self.data.targetedCoord)
				self.data.targetedCoord = [None]
			
			if targetedUnit != None:
				targetedUnit.statHP -= self.data.statDamage - targetedUnit.statArmor
			
			if self.data in Unit0.TANKS or self.data in Unit0.ARTILLERY:
				self.data.statAmmo -= 1
				
			print("A unit is (probably) under attack!")
			
	class EventUnitAbilityCast(GameEvent):
		#takes the prority modifier as data
		
		def execute(self):
			for unit in Unit0.UNITARRAY:
				if len(unit.instAbilities) > 0:
					for ability in unit.instAbilities:
						if ability.isActivated:
							if ability.priority == self.data:
								ability.execute()