#Artificial Destiny
#By SoapDictator

import pygame, sys
from pygame.locals import *

global FPS = 30
global windowWidth = 640
global windowHeight = 480
global cellSize = 20

assert windowWidth % cellSize == 0
assert windowHeight % cellSize == 0

global cellWidth = int(windowWidth / cellSize)
global cellHeight = int(windowWidth / cellSize)

#             R    G    B
global WHITE     = (255, 255, 255)
global BLACK     = (  0,   0,   0)
global RED       = (255,   0,   0)
global GREEN     = (  0, 255,   0)
global DARKGREEN = (  0, 155,   0)
global DARKGRAY  = ( 40,  40,  40)
global BGCOLOR = BLACK

class Window(object):
	def __init__(self):
		

class Unit(object):
	coordX = 0
	coordY = 0
	statHealth = 0
	statArmor = 0
	statDamage = 0

class Tank(Unit):
	coordX = 0
	coordY = 0
	statHealth = 0
	statArmor = 0
	statDamage = 0
	def __init__(self):
		print("A new tank appears!")
		print("Its health equals %s") % statHealth
		
Bulldozer = Tank()