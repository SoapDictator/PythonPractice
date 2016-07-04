def print_two(*args):
	arg1, arg2 = args
	print "%r %r"	% (arg1, arg2)
def print_two_again(arg1, arg2):
	print "%r %r"	% (arg1, arg2)
def print_none():
	print "[UFO took this message]"
	
print_two("I don't", "even care")
print_two_again("Damn", "son")
print_none()