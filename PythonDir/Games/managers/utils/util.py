import tempfile, pkgutil, pygame

def loadFont(filename, size=8):
	with tempfile.NamedTemporaryFile() as f:
		data = pkgutil.get_data('AD', filename)
		f.write(data)
		f.seek(0)
		font = pygame.font.Font(filename, size)
	return font

#curently calculates distance in axial hexagonal coordinates
def getDistance(origin, target):
	#true distance
	#return math.sqrt(math.pow(abs(target[0]-origin[0]), 2) + math.pow(abs(target[1]-origin[1]), 2))
	
	#calculates how many non-diagonal steps it will take to get from origin to target
	#return abs(target[0]-origin[0]) + abs(target[1]-origin[1])
	
	#calculates distance in axial hex coordinates
	aq = origin[0]
	ar = origin[1]
	bq = target[0]
	br = target[1]
	return (abs(aq-bq) + abs(aq+ar-bq-br) + abs(ar-br))/2