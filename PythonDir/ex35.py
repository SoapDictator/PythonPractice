from sys import exit

print "\n"

def gold_room():
	print "This room is full of gold. How much do you take?"
	
	choice = raw_input("> ")
	if "0" in choice or "1" in choice:
		how_much = int(choice)
	else:
		dead("Man, learn to type a number.")
		
	if how_much < 50:
		print "Nice, you're not greedy, you win!"
		exit(0)
	else:
		dead("You greedy bastard!")
		
def bear_room():
	print "There is a bear here."
	print "The bear has a bunch of honey."
	print "The fat bear is in front of another door."
	print "How are you going to move the bear?"
	bear_moved = False
	
	while True:
		choice = raw_input("> ")
		
		if "take" in choice and "honey" in choice:
			dead("The bear looks at you then slaps your face off.")
		elif "taunt" in choice and "bear" in choice and not bear_moved:
			print "The bear has moved from the door. You can go through it now."
			bear_moved = True
		elif "taunt" in choice and "bear" in choice and bear_moved:
			dead("The bear gets pissed and chews you leg off.")
		elif "open" in choice and "door" in choice and bear_moved:
			gold_room()
		else:
			print "I got no idea what that means."
			
def cthulhu_room():
	print "Here you see the great evil Cthulhu."
	print "He, it, whatever stares at you and you go insane."
	print "Do you flee for you life or eat your head?"
	
	choice = raw_input("> ")
	
	if "flee" in choice:
		start()
	elif "head" in choice:
		dead("Well that was tasty!")
	elif "cats" in choice:
		print "Oh no, did somebody say 'cats'? Catsplosion! Run for your li-"
		exit(0)
	else:
		cthulhu_room()
	
def dead(why):
	print why, "Good job!"
	exit(0)

def start():
	print "You are in a dark room."
	print "There is a door to you right and left."
	print "Which one do you take?"
	
	choice = raw_input("> ")
	
	if "left" in choice:
		bear_room()
	elif "right" in choice:
		cthulhu_room()
	else:
		dead("You stumble around the room untill you starve.")
		
start()