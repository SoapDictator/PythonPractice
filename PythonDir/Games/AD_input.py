import pygame, sys
from pygame.locals import *
from AD_unit import *

class InputManager(object):
	inputState = ['moveSelection', 'unitSelected', 'unitTarget']
	currentState = inputState[0]
	
	def defineGlobals(self, EventManager, DrawingManager, MapManager, UnitManager):
		global Event0, Window0, Map0, Unit0
		Event0 = EventManager
		Window0 = DrawingManager
		Map0 = MapManager
		Unit0 = UnitManager
	
	def getState(self):
		return self.currentState
		
	def setState(self, num):
		self.currentState = self.inputState[num]
		if num == 0:
			 Unit0.SELECTEDUNIT = -1
	
	def handleInput(self):
		for event in pygame.event.get():	#this is chinese level of programming, needs fixing as well
			if event.type == QUIT:
				self.terminate()
			if self.getState() == 'moveSelection':
				if pygame.mouse.get_pressed() == (1, 0, 0):
					coord = Window0.pixeltohex(pygame.mouse.get_pos())
					Unit0.SELECTEDUNIT = Map0.getUnit(coord)
					if Unit0.SELECTEDUNIT != None:	self.setState(1)
					elif coord not in Map0.MOARRAY:
						Map0.MOARRAY.append(coord)
					else:
						for i in range(0, len(Map0.MOARRAY)+1):
							if Map0.MOARRAY[i] == coord:
								del Map0.MOARRAY[i]
								break
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.terminate()
					elif event.key == K_e:	Event0.eventHandle()
					elif event.key == K_z:		Event0.eventUndo()
			elif self.getState() == 'unitSelected':
				if pygame.mouse.get_pressed() == (1, 0, 0):
					coord = Window0.pixeltohex(pygame.mouse.get_pos())
					path = Map0.getPath(Unit0.SELECTEDUNIT.statSpeed, Unit0.SELECTEDUNIT.statCoord, coord)
					Unit0.MOVEQUEUE[Unit0.SELECTEDUNIT.arrayPos] = path[::-1]
					self.setState(0)
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.setState(0)
					elif event.key == K_a:		self.setState(2)
					elif event.key == K_z:			Event0.eventUndo()
			elif self.getState() == 'unitTarget':
				if pygame.mouse.get_pressed() == (1, 0, 0):
					if isinstance(Unit0.SELECTEDUNIT, Tank) or isinstance(Unit0.SELECTEDUNIT, Engineer):
						FR = Unit0.SELECTEDUNIT.statFR
					elif isinstance(Unit0.SELECTEDUNIT, Artillery):
						FR = Unit0.SELECTEDUNIT.statMaxFR
					else:
						FR = 0
						
					coord = Window0.pixeltohex(pygame.mouse.get_pos())
					if Map0.getDistance(Unit0.SELECTEDUNIT.statCoord, coord) <= FR:
						isok = Unit0.SELECTEDUNIT.targetChange(coord)
						if isok:
							self.setState(1)
						break
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:	self.setState(1)
					elif event.key == K_e:		
						Unit0.SELECTEDUNIT.targetChange()
						self.setState(1)

	def terminate(self):
		print("Terminated.")
		pygame.quit()
		sys.exit()