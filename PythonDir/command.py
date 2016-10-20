class Command(object):
	def execute(self):
		print "I am here!"
	
class Command_Jump(Command):
	def execute(self):
		print "Unit rocket-jumped in one place. Rest in peaces."
		
class Command_Shoot(Command):
	def execute(self):
		print "The unit exploded something to bits."
		
class Command_Slide(Command):
	def execute(self):
		print "This unit can't slide, so sad. T_T"
		
class Command_Reload(Command):
	def execute(self):
		print "The unit reloaded it's weapon"

#these are "binds"
ButtonX = Command_Shoot()
ButtonY = Command_Reload()
ButtonA = Command_Jump()
ButtonB = Command_Slide()
		
class InputHandler(object):
	def __init__(self):
		print "Type 'X', 'Y', 'A' or 'B'"
	
	#I can just toss objects around the programm
	def HandleInput(self, ButtonPress):		
			if (ButtonPress == "X"): return ButtonX
			elif (ButtonPress == "Y"): return ButtonY
			elif (ButtonPress == "A"): return ButtonA
			elif (ButtonPress == "B"): return ButtonB
			else: exit()

#initialization and an endless cycle of button pressing
start = InputHandler()
while True:
	command = start.HandleInput(raw_input('> '))
	command.execute()