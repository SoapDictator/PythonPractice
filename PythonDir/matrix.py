def create(n):
	matrix = []
	for i in range(0, n):
		matrix.append(range(0+i, n+i))
	return matrix
	
def mprint(matrix, n):
	for i in range(0, n):
		line = "[ "
		for j in range(0, n):
			line += "%i " % matrix[i][j]
		line += "]"
		print line

def diagonal(matrix, n):		
	for i in range(0, n):
		print "[%s %i %s]" % (" 0"*(0+i), matrix[i][i], "0 "*(n-1-i))