#
#================
#|| Artificially Destined ||
#================
#written by SoapDictator
#================

import pygame, sys, math, thread
from pygame.locals import *
from AD_event import *
from AD_drawing import *
from AD_input import *
from AD_map import *
from AD_unit import *
		
class Main(object):
	def __init__(self):
		global Event0, Window0, Input0, Unit0, Map0
		Event0 = GameEventManager()
		Window0 = DrawingManager()
		Input0 = InputManager()
		Unit0 = UnitManager()
		Map0 = MapManager()
		
		Event0.defineGlobals(Event0, Map0, Unit0)
		Window0.defineGlobals(Input0, Map0, Unit0)	
		Input0.defineGlobals(Event0, Window0, Map0, Unit0)
		Map0.defineGlobals(Window0, Unit0)
		Unit0.defineGlobals(Window0, Map0, Unit0)
		
		print("\n============")
		print("==Turn 0==")
		self.test()
		
		#try:
		#	thread.start_new_thread(Window0.screenStartDrawing, ())
		#except:
		#	print(":(")
		
		while True:
			Input0.handleInput()
			Window0.screenRefresh()
	
	def test(self):
		Event0.eventAdd("EventUnitCreate", ("Tank", [0, 0], "player1"))
		Event0.eventAdd("EventUnitCreate", ("Artillery", [2, 1], "player2"))
		Event0.eventHandle()
		
		#Unit0.UNITARRAY[0].statCur["HP"] -= 8
		testUnit = Unit0.getAllUnits()[1]
		#testUnit.castAbility(testUnit.statAbilities[0], Unit0.UNITARRAY[0])
		Event0.eventHandle()

StartShenanigans = Main()