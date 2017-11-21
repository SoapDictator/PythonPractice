#
#Artificially Destined
#=============
#by SoapDictator
#

import pygame, sys, math, thread
from pygame.locals import *
from managers import event, window, input, unit, map
		
class Main(object):
	#singleton implementation
	instance = None
	
	def __init__(self):
		if not Main.instance:
			Main.instance = Main.__Main()
			
	def __getattr__(self, name):
		return getattr(self.instance, name)
	
	class __Main():
		def __init__(self):
			global EVENT0, WINDOW0, INPUT0, UNIT0, MAP0
			EVENT0 = event.GameEventManager()
			WINDOW0 = window.WindowManager()
			INPUT0 = input.InputManager()
			UNIT0 = unit.UnitManager()
			MAP0 = map.MapManager()
			
			EVENT0.defineGlobals(EVENT0, MAP0, UNIT0)
			WINDOW0.defineGlobals(INPUT0, MAP0, UNIT0)	
			INPUT0.defineGlobals(EVENT0, WINDOW0, MAP0, UNIT0)
			MAP0.defineGlobals(WINDOW0, UNIT0)
			UNIT0.defineGlobals(WINDOW0, MAP0, UNIT0)
			
			#regression(haha) tests
			self.testTankAttack().testArtiAttack().testUnitCastAbility()
			
			#for manual testing
			self.testCreateUnits()
			
			while True:
				INPUT0.handleInput()
				WINDOW0.screenRefresh()
		
		#TESTS
		def testCreateUnits(self):
			EVENT0.eventAdd("EventUnitCreate", ("Artillery", [-4, -3], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("Artillery", [4, 3], "player2"))
			EVENT0.eventAdd("EventUnitCreate", ("Scout", [-3, -4], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("Scout", [3, 4], "player2"))
			EVENT0.eventHandle()
			
			return self
		
		def testUnitMove(self):
			EVENT0.eventAdd("EventUnitCreate", ("Tank", [0, 0], "player1"))
			EVENT0.eventHandle()
			
			tstUnit0 = units[len(units)-1]
			tstUnit0.setMoveQueue(MAP0.getPath(tstUnit0.getStatCur("SPD"), tstUnit0.getCoord(), [3, 3]))
			EVENT0.eventHandle()
			
			try:
				assert(tstUnit0.getCoord() == [3, 3])
			except:
				print("Test Fail: Tank horribly failed to move!")
			UNIT0.unitDestroy(tstUnit0)
			return self
		
		def testTankAttack(self):
			EVENT0.eventAdd("EventUnitCreate", ("Tank", [0, 0], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("Scout", [1, 1], "player2"))
			EVENT0.eventHandle()
			
			units = UNIT0.getAllUnits()
			tstUnit0 = units[len(units)-2]
			tstUnit1 = units[len(units)-1]
			
			tstUnit0.setTarget(tstUnit1)
			EVENT0.eventHandle()
			
			UNIT0.unitDestroy(tstUnit0)
			try:
				assert(tstUnit1.getStatCur("HP") <= 0)
			except:
				print("Test Fail: Tank's attack failed horribly!")
				UNIT0.unitDestroy(tstUnit1)
			return self
			
		def testArtiAttack(self):
			EVENT0.eventAdd("EventUnitCreate", ("Artillery", [0, 0], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("Scout", [3, 3], "player2"))
			EVENT0.eventHandle()
			
			units = UNIT0.getAllUnits()
			tstUnit0 = units[len(units)-2]
			tstUnit1 = units[len(units)-1]
			
			tstUnit0.setTarget(tstUnit1.getCoord())
			EVENT0.eventHandle()
			
			UNIT0.unitDestroy(tstUnit0)
			try:
				assert(tstUnit1.getStatCur("HP") <= 0)
			except:
				print("Test Fail: Artillery's attack failed horribly!")
				UNIT0.unitDestroy(tstUnit1)
			return self
			
		def testUnitCastAbility(self):
			EVENT0.eventAdd("EventUnitCreate", ("Engineer", [0, 0], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("Scout", [1, 1], "player1"))
			EVENT0.eventHandle()
			
			units = UNIT0.getAllUnits()
			tstUnit0 = units[len(units)-2]
			tstUnit1 = units[len(units)-1]
			
			tstUnit0.castAbility("A001", tstUnit1)
			EVENT0.eventHandle()
			
			UNIT0.unitDestroy(tstUnit0)
			UNIT0.unitDestroy(tstUnit1)
			return self

StartShenanigans = Main()