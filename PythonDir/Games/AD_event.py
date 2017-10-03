from AD_unit import *
import thread

global AVAILIBLEEVENTS
#dictionary entry format - (event name: priority)
AVAILIBLEEVENTS = {	"EventUnitAttack": 1, 
									"EventUnitHPCheck": 2,
									"EventUnitCreate": 3,
									"EventUnitDestroy": 4,
									"EventUnitAbilityCast": 5,
									"EventUnitMove": 6}

class GameEventManager(object):
	turnCounter = 0
	eventQueue = []
	eventLastest = None
	
	def defineGlobals(self, EventManager, MapManager, UnitManager):
		global Event0, Map0, Unit0
		Event0 = EventManager
		Map0 = MapManager
		Unit0 = UnitManager
	
	def eventAdd(self, eventName, data = None, priorityMod = 0):	#TODO: event sorting mechanism
		if eventName not in AVAILIBLEEVENTS:
			pass
		
		targetEvent = getattr(Events, eventName)
		event = targetEvent(data)
		priority = AVAILIBLEEVENTS[eventName] + priorityMod
		
		if len(self.eventQueue) > 1:
			if self.eventQueue[0][1] > priority:
				self.eventQueue.insert(0, [event, priority])
			elif self.eventQueue[len(self.eventQueue)-1][1] < priority:
				self.eventQueue.append([event, priority])
			else:
				for i in range(1, len(self.eventQueue)):
					if self.eventQueue[i-1][1] <= priority and self.eventQueue[i][1] >= priority:
						self.eventQueue.insert(i, [event, priority])
						break
		else:
			if len(self.eventQueue) == 1 and self.eventQueue[0][1] > priority:
				self.eventQueue.insert(0, [event, priority])
			else:
				self.eventQueue.append([event, priority])
		self.eventLastest = event
	
	def eventUndo(self):
		if self.eventLastest != None:
			for i in range(0, len(self.eventQueue)):
				if self.eventLastest == self.eventQueue[i][0]:
					print("Undid %s" % self.eventQueue[i][0])
					del self.eventQueue[i]
					self.eventLastest = None
	
	def eventHandle(self):
		Unit0.resetPlayerFOV()
		
		priorityMod = 0
		for i in range (0, 4):
			self.eventAdd("EventUnitHPCheck", priorityMod, priorityMod)
			self.eventAdd("EventUnitAbilityCast", priorityMod, priorityMod)
			if i == 0:	#preturn
				pass
			
			if i == 1:	#first half
				for UNIT in Unit0.getTanks():
					if UNIT.getTarget() != None:
						Event0.eventAdd("EventUnitAttack", UNIT, priorityMod)
						
				self.eventAdd("EventUnitMove", Unit0.getScouts(), priorityMod)
		
			if i == 2:	#second half
				for UNIT in Unit0.getArties():
					if UNIT.getTarget() != None:
						Event0.eventAdd("EventUnitAttack", UNIT, priorityMod)
				
				#tempUnits = Unit0.TANKS + Unit0.ARTILLERY + Unit0.ENGINEERS
				#self.eventAdd("EventUnitMove", tempUnits, priorityMod)
				
				#have to call it 3 times, otherwise destroyed units will try to move and cause a bug
				self.eventAdd("EventUnitMove", Unit0.getEngies(), priorityMod)
				self.eventAdd("EventUnitMove", Unit0.getArties(), priorityMod)
				self.eventAdd("EventUnitMove", Unit0.getTanks(), priorityMod)
											
			if i == 3:	#postturn
				pass
				
			priorityMod += 10
		
		for event in self.eventQueue:
			event[0].execute()
		self.eventQueueReset()
		
		Unit0.setPlayerFOV(Unit0.getPlayerSelectedID())
		print("============")
		self.turnCounter += 1
		print("==Turn %s==" % self.turnCounter)
		
	def eventQueueReset(self):
		del self.eventQueue[:]
		
	def getTurnCounter(self):
		return self.turnCounter

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
			for Unit in Unit0.getAllUnits():
				if Unit.statCur["HP"] <= 0:
					Event0.eventAdd("EventUnitDestroy", Unit)
				if Unit.statCur["HP"] > Unit.statNom["HP"]:
					Unit.statCur["HP"] = Unit.statNom["HP"]
			#print("HP checked.")

	class EventUnitMove(GameEvent):
		#takes a unit array as data
		def execute(self):
			if len(self.data) != 0:
				#thread.start_new_thread(Unit0.unitMoveStart, (self.data, ))
				Unit0.unitMoveStart(self.data)
				#print("Moved units.")

	class EventUnitAttack(GameEvent):
		#takes an attacking unit as data
		def execute(self):
			attacker = self.data
			target = attacker.getTarget()
			if target == None:
				pass
				
			attacker.resetTarget()
			
			target.statCur["HP"] -= self.data.statCur["DMG"] - target.statCur["AR"]
			
			if Unit0.isTank(attacker) or Unit0.isArti(attacker):
				attacker.statCur["AMM"] -= 1
				
			print("A unit is (probably) under attack!")
			
	class EventUnitAbilityCast(GameEvent):
		#takes the prority modifier as data
		def execute(self):
			for unit in Unit0.getAllUnits():
				if len(unit.instAbilities) > 0:
					for ability in unit.instAbilities:
						if ability.isActivated:
							if ability.priority == self.data:
								ability.execute()